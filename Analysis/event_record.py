"""
event_record.py — Central event record that accumulates data from all modules.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any


@dataclass
class Particle:
    """A single final-state or intermediate particle."""
    barcode: int
    pid: int
    status: int
    px: float
    py: float
    pz: float
    energy: float
    mass: float
    production_vertex: int
    end_vertex: int

    @property
    def pt(self) -> float:
        return (self.px**2 + self.py**2) ** 0.5

    @property
    def p(self) -> float:
        return (self.px**2 + self.py**2 + self.pz**2) ** 0.5

    @property
    def eta(self) -> float:
        import math
        p = self.p
        if p == 0:
            return 0.0
        cos_theta = self.pz / p
        if abs(cos_theta) >= 1.0:
            return float("inf") * (1 if cos_theta > 0 else -1)
        return -0.5 * math.log((1 - cos_theta) / (1 + cos_theta))

    @property
    def phi(self) -> float:
        import math
        return math.atan2(self.py, self.px)


@dataclass
class Vertex:
    """An interaction vertex."""
    barcode: int
    x: float
    y: float
    z: float
    t: float
    particles_in: list[int] = field(default_factory=list)   # barcodes
    particles_out: list[int] = field(default_factory=list)  # barcodes


@dataclass
class EventRecord:
    """
    Holds all data for one event: raw HepMC data plus whatever modules append.

    Modules write into `extras` under a namespace key they own, e.g.:
        record.extras["JetFinder"] = {"jets": [...], "n_jets": 3}
    """
    # --- header ---
    event_number: int = 0
    n_mpi: int = 0
    scale: float = 0.0
    alpha_qcd: float = 0.0
    alpha_qed: float = 0.0
    signal_process_id: int = 0
    signal_process_vertex: int = 0
    n_vertices: int = 0
    beam1_barcode: int = 0
    beam2_barcode: int = 0
    weights: list[float] = field(default_factory=list)

    # --- content ---
    particles: dict[int, Particle] = field(default_factory=dict)
    vertices: dict[int, Vertex] = field(default_factory=dict)

    # --- module outputs ---
    extras: dict[str, Any] = field(default_factory=dict)

    # --- convenience views ---
    @property
    def final_state(self) -> list[Particle]:
        """Particles with status == 1 (stable final-state)."""
        return [p for p in self.particles.values() if p.status == 1]

    @property
    def beam_particles(self) -> list[Particle]:
        return [p for p in self.particles.values() if p.status == 4]

    def __repr__(self) -> str:
        return (
            f"<EventRecord #{self.event_number}  "
            f"particles={len(self.particles)}  "
            f"vertices={len(self.vertices)}  "
            f"extras={list(self.extras.keys())}>"
        )
