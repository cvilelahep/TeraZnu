"""
modules/kinematic_summary.py — Compute basic kinematic quantities.
"""
from __future__ import annotations
import math
from base_module import BaseModule
from event_record import EventRecord


class KinematicSummary(BaseModule):
    """
    Appends scalar-sum HT, MET, and leading-particle pT to every event.

    record.extras["KinematicSummary"] = {
        "HT":         float,   # scalar sum of final-state pT
        "MET":        float,   # missing transverse energy magnitude
        "MET_phi":    float,   # MET azimuthal angle
        "leading_pt": float,   # highest pT among final-state particles
        "n_final":    int,     # number of final-state particles
    }
    """

    @property
    def name(self) -> str:
        return "KinematicSummary"

    def process(self, record: EventRecord) -> None:
        fs = record.final_state
        if not fs:
            record.extras[self.name] = {}
            return

        HT   = sum(p.pt for p in fs)
        MEx  = -sum(p.px for p in fs)
        MEy  = -sum(p.py for p in fs)
        MET  = math.sqrt(MEx**2 + MEy**2)

        record.extras[self.name] = {
            "HT":         HT,
            "MET":        MET,
            "MET_phi":    math.atan2(MEy, MEx),
            "leading_pt": max(p.pt for p in fs),
            "n_final":    len(fs),
        }
