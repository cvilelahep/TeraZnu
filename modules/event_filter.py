"""
modules/event_filter.py — Tag events passing user-defined selection criteria.

record.extras["EventFilter"] = {
    "passed": bool,
    "flags":  {"cut_name": bool, ...},   # which individual cuts passed
}
"""
from __future__ import annotations
from typing import Callable
from base_module import BaseModule
from event_record import EventRecord


class EventFilter(BaseModule):
    """
    Apply a sequence of named boolean cuts to each event.

    Each cut is a callable (EventRecord) -> bool.
    An event passes if ALL cuts return True.

    Parameters
    ----------
    cuts : dict[str, Callable[[EventRecord], bool]]
        Ordered mapping of cut name → predicate.

    Example
    -------
    >>> from modules.event_filter import EventFilter
    >>> cuts = {
    ...     "n_jets>=2":  lambda r: r.extras.get("JetFinder", {}).get("n_jets", 0) >= 2,
    ...     "MET>50GeV":  lambda r: r.extras.get("KinematicSummary", {}).get("MET", 0) > 50,
    ... }
    >>> filt = EventFilter(cuts)
    """

    def __init__(self, cuts: dict[str, Callable[[EventRecord], bool]]):
        self._cuts    = cuts
        self._n_total = 0
        self._n_pass  = 0

    @property
    def name(self) -> str:
        return "EventFilter"

    def process(self, record: EventRecord) -> None:
        self._n_total += 1
        flags: dict[str, bool] = {}
        passed = True
        for label, fn in self._cuts.items():
            try:
                ok = bool(fn(record))
            except Exception as exc:
                ok = False
                flags[f"{label}__error"] = str(exc)  # type: ignore[assignment]
            flags[label] = ok
            if not ok:
                passed = False

        if passed:
            self._n_pass += 1

        record.extras[self.name] = {"passed": passed, "flags": flags}

    def end(self) -> None:
        eff = self._n_pass / self._n_total if self._n_total else 0.0
        print(
            f"[EventFilter] {self._n_pass}/{self._n_total} events passed "
            f"({100 * eff:.1f} %)"
        )
