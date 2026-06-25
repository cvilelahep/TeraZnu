"""
hepmc_reader.py — Streaming parser for HepMC2 ASCII format.

Each call to __iter__ yields one fully-populated EventRecord.
Supports both plain .hepmc files and gzip-compressed .hepmc.gz files.
"""
from __future__ import annotations
import gzip
import io
from pathlib import Path
from typing import Iterator

from event_record import EventRecord, Particle, Vertex


def _open(path: str | Path):
    path = Path(path)
    if path.suffix == ".gz":
        return gzip.open(path, "rt")
    return open(path, "r")


def _parse_weights(tokens: list[str], idx: int) -> list[float]:
    """Parse  <n_weights>  w1 w2 ...  from token list starting at idx."""
    n = int(tokens[idx])
    return [float(tokens[idx + 1 + i]) for i in range(n)]


class HepmcReader:
    """
    Streaming HepMC2 ASCII parser.

    Usage
    -----
    >>> reader = HepmcReader("my_file.hepmc")
    >>> for record in reader:
    ...     print(record)
    """

    def __init__(self, path: str | Path):
        self.path = Path(path)

    def __iter__(self) -> Iterator[EventRecord]:
        with _open(self.path) as fh:
            record: EventRecord | None = None

            for raw in fh:
                line = raw.strip()
                if not line or line.startswith("#"):
                    continue

                kind = line[0]

                # ── Event header ──────────────────────────────────────────────
                if kind == "E":
                    if record is not None:
                        yield record
                    record = self._parse_event_line(line)

                # ── Vertex ────────────────────────────────────────────────────
                elif kind == "V" and record is not None:
                    vtx = self._parse_vertex_line(line)
                    record.vertices[vtx.barcode] = vtx

                # ── Particle ──────────────────────────────────────────────────
                elif kind == "P" and record is not None:
                    p, vtx_barcode = self._parse_particle_line(line)
                    record.particles[p.barcode] = p
                    # attach to the most recently seen vertex
                    if vtx_barcode and vtx_barcode in record.vertices:
                        record.vertices[vtx_barcode].particles_out.append(p.barcode)

                # ── Units / cross-section lines (skip gracefully) ─────────────
                # U, C, H, F, N lines in HepMC2/3 — just ignore for now

            if record is not None:
                yield record

    # ── line parsers ────────────────────────────────────────────────────────

    @staticmethod
    def _parse_event_line(line: str) -> EventRecord:
        """
        E <event_number> <n_mpi> <scale> <alpha_qcd> <alpha_qed>
          <signal_process_id> <signal_process_vertex> <n_vertices>
          <beam1_barcode> <beam2_barcode> <n_random_states> [r0 r1 ...]
          <n_weights> [w0 w1 ...]
        """
        tokens = line.split()
        r = EventRecord()
        r.event_number          = int(tokens[1])
        r.n_mpi                 = int(tokens[2])
        r.scale                 = float(tokens[3])
        r.alpha_qcd             = float(tokens[4])
        r.alpha_qed             = float(tokens[5])
        r.signal_process_id     = int(tokens[6])
        r.signal_process_vertex = int(tokens[7])
        r.n_vertices            = int(tokens[8])
        r.beam1_barcode         = int(tokens[9])
        r.beam2_barcode         = int(tokens[10])

        # skip random state integers
        idx = 11
        n_random = int(tokens[idx]); idx += 1 + n_random

        # weights
        if idx < len(tokens):
            try:
                r.weights = _parse_weights(tokens, idx)
            except (IndexError, ValueError):
                r.weights = []

        return r

    @staticmethod
    def _parse_vertex_line(line: str) -> Vertex:
        """
        V <barcode> <id> <x> <y> <z> <t> <n_orphans> <n_particles_out> <n_weights>
        """
        tokens = line.split()
        return Vertex(
            barcode         = int(tokens[1]),
            x               = float(tokens[3]),
            y               = float(tokens[4]),
            z               = float(tokens[5]),
            t               = float(tokens[6]),
        )

    @staticmethod
    def _parse_particle_line(line: str) -> tuple[Particle, int | None]:
        """
        P <barcode> <pid> <px> <py> <pz> <energy> <mass> <status>
          <pol_theta> <pol_phi> <vtx_barcode> ...
        Returns (Particle, end_vertex_barcode).
        """
        tokens = line.split()
        p = Particle(
            barcode = int(tokens[1]),
            pid     = int(tokens[2]),
            px      = float(tokens[3]),
            py      = float(tokens[4]),
            pz      = float(tokens[5]),
            energy  = float(tokens[6]),
            mass    = float(tokens[7]),
            status  = int(tokens[8]),
        )
        end_vtx = int(tokens[11]) if len(tokens) > 11 else None
        return p, end_vtx
