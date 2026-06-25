"""
modules/multiplicity.py — Count particles by species.
"""
from __future__ import annotations
from collections import Counter
from base_module import BaseModule
from event_record import EventRecord

# Common PID → label map (PDG codes)
_PID_LABEL = {
    11: "e-", -11: "e+", 12: "nu_e", -12: "nu_e_bar",
    13: "mu-", -13: "mu+", 14: "nu_mu", -14: "nu_mu_bar",
    15: "tau-", -15: "tau+", 16: "nu_tau", -16: "nu_tau_bar",
    22: "gamma",
    211: "pi+", -211: "pi-", 111: "pi0",
    321: "K+", -321: "K-", 311: "K0",
    2212: "p", -2212: "p_bar", 2112: "n", -2112: "n_bar",
    21: "g",
}


class Multiplicity(BaseModule):
    """
    Count final-state particles by PID and by named species.

    record.extras["Multiplicity"] = {
        "pid_counts":     Counter({pid: n, ...}),
        "species_counts": Counter({"e-": n, "mu+": m, ...}),
        "total":          int,
        "charged":        int,   # crude estimate via known charged PIDs
    }
    """

    _CHARGED_PIDS = {
        11, -11, 13, -13, 15, -15,
        211, -211, 321, -321,
        2212, -2212,
    }

    @property
    def name(self) -> str:
        return "Multiplicity"

    def process(self, record: EventRecord) -> None:
        fs = record.final_state
        pid_counts     = Counter(p.pid for p in fs)
        species_counts = Counter(
            _PID_LABEL.get(p.pid, f"pdg_{p.pid}") for p in fs
        )
        charged = sum(n for pid, n in pid_counts.items() if pid in self._CHARGED_PIDS)

        record.extras[self.name] = {
            "pid_counts":     pid_counts,
            "species_counts": species_counts,
            "total":          len(fs),
            "charged":        charged,
        }
