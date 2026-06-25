"""
framework.py — Orchestrates reading and module execution.
"""
from __future__ import annotations
import sys
import time
from pathlib import Path
from typing import Iterator

from event_record import EventRecord
from base_module import BaseModule
from hepmc_reader import HepmcReader


class Framework:
    """
    Main driver: reads a HepMC file, passes each event through a pipeline
    of registered modules, and (optionally) yields processed EventRecords.

    Usage
    -----
    >>> fw = Framework("collisions.hepmc")
    >>> fw.add_module(KinematicSummary())
    >>> fw.add_module(Multiplicity())
    >>> fw.add_module(JetFinder(R=0.4, pt_cut=25))
    >>> for record in fw.run():
    ...     print(record.extras["JetFinder"]["n_jets"])
    """

    def __init__(self, path: str | Path, max_events: int = -1, verbose: bool = True):
        self.path       = Path(path)
        self.max_events = max_events
        self.verbose    = verbose
        self._modules: list[BaseModule] = []

    def add_module(self, module: BaseModule) -> "Framework":
        """Register a module. Returns self for chaining."""
        self._modules.append(module)
        return self

    def run(self) -> Iterator[EventRecord]:
        """
        Generator: yields each processed EventRecord.
        Call list(fw.run()) to materialise all events at once,
        or iterate for a streaming pipeline.
        """
        reader = HepmcReader(self.path)

        if self.verbose:
            print(f"[Framework] Opening {self.path}")
            print(f"[Framework] Modules: {[m.name for m in self._modules]}")

        # begin
        for m in self._modules:
            m.begin()

        t0 = time.perf_counter()
        n  = 0

        try:
            for record in reader:
                for m in self._modules:
                    m.process(record)
                yield record
                n += 1
                if self.verbose and n % 1000 == 0:
                    print(f"[Framework] Processed {n} events …", file=sys.stderr)
                if self.max_events > 0 and n >= self.max_events:
                    break
        finally:
            # end — always called even if the loop is broken early
            for m in self._modules:
                m.end()

            elapsed = time.perf_counter() - t0
            if self.verbose:
                rate = n / elapsed if elapsed > 0 else 0
                print(f"[Framework] Done. {n} events in {elapsed:.2f}s ({rate:.0f} evt/s)")
