"""
modules/jet_finder.py — Toy anti-kT / kT jet clustering (no external deps).

A self-contained O(N^3) implementation suitable for moderate multiplicities.
For production use, wire in FastJet via its Python bindings instead.

record.extras["JetFinder"] = {
    "jets": [
        {"pt": float, "eta": float, "phi": float,
         "n_constituents": int, "constituents": [barcode, ...]},
        ...
    ],
    "n_jets": int,
    "algorithm": str,
    "R": float,
    "pt_cut": float,
}
"""
from __future__ import annotations
import math
from base_module import BaseModule
from event_record import EventRecord, Particle


def _delta_r2(phi1, eta1, phi2, eta2) -> float:
    dphi = phi1 - phi2
    # wrap to [-pi, pi]
    while dphi >  math.pi: dphi -= 2 * math.pi
    while dphi < -math.pi: dphi += 2 * math.pi
    return dphi**2 + (eta1 - eta2)**2


class JetFinder(BaseModule):
    """
    Configurable jet clustering module.

    Parameters
    ----------
    R        : cone radius (default 0.4)
    pt_cut   : minimum jet pT in GeV (default 20)
    algorithm: "kt", "anti_kt", or "cambridge" (default "anti_kt")
    eta_max  : maximum |eta| for seed particles (default 5.0)
    """

    def __init__(
        self,
        R: float = 0.4,
        pt_cut: float = 20.0,
        algorithm: str = "anti_kt",
        eta_max: float = 5.0,
    ):
        self.R       = R
        self.pt_cut  = pt_cut
        self.alg     = algorithm
        self.eta_max = eta_max

    @property
    def name(self) -> str:
        return "JetFinder"

    def process(self, record: EventRecord) -> None:
        # seed particles: visible final state within eta acceptance
        _invisible = {12, -12, 14, -14, 16, -16}  # neutrinos
        seeds = [
            p for p in record.final_state
            if p.pid not in _invisible and abs(p.eta) < self.eta_max
        ]

        jets = self._cluster(seeds)
        jets = [j for j in jets if j["pt"] >= self.pt_cut]
        jets.sort(key=lambda j: j["pt"], reverse=True)

        record.extras[self.name] = {
            "jets":      jets,
            "n_jets":    len(jets),
            "algorithm": self.alg,
            "R":         self.R,
            "pt_cut":    self.pt_cut,
        }

    # ── clustering ───────────────────────────────────────────────────────────

    def _kt_power(self, pt: float) -> float:
        if self.alg == "kt":
            return pt**2
        if self.alg == "anti_kt":
            return pt**-2 if pt > 0 else 1e30
        return 1.0  # cambridge/aachen

    def _cluster(self, particles: list[Particle]) -> list[dict]:
        """
        Iterative pairwise merging — naive O(N^3) sequential recombination.
        Returns list of jet dicts with 4-momentum and constituent barcodes.
        """
        # pseudo-jets: [px, py, pz, E, [barcodes]]
        pj = [[p.px, p.py, p.pz, p.energy, [p.barcode]] for p in particles]
        jets = []
        R2 = self.R**2

        while pj:
            # compute pT and angles for each pseudo-jet
            def pt(p):  return math.sqrt(p[0]**2 + p[1]**2)
            def eta(p):
                pmag = math.sqrt(p[0]**2 + p[1]**2 + p[2]**2)
                if pmag == 0: return 0.0
                ct = p[2] / pmag
                if abs(ct) >= 1: return 1e9 * (1 if ct > 0 else -1)
                return -0.5 * math.log((1 - ct) / (1 + ct))
            def phi(p):  return math.atan2(p[1], p[0])

            # beam distances d_{iB} = kt_power(pti)
            d_beam = [self._kt_power(pt(p)) for p in pj]

            # pairwise distances d_{ij}
            best_d  = min(d_beam)
            best_i  = d_beam.index(best_d)
            best_j  = None

            for i in range(len(pj)):
                for j in range(i + 1, len(pj)):
                    kt_min = min(self._kt_power(pt(pj[i])),
                                 self._kt_power(pt(pj[j])))
                    dr2    = _delta_r2(phi(pj[i]), eta(pj[i]),
                                       phi(pj[j]), eta(pj[j]))
                    d_ij   = kt_min * dr2 / R2
                    if d_ij < best_d:
                        best_d = d_ij
                        best_i = i
                        best_j = j

            if best_j is None:
                # promote pseudo-jet best_i → jet
                p = pj.pop(best_i)
                pT = pt(p)
                jets.append({
                    "pt":             pT,
                    "eta":            eta(p),
                    "phi":            phi(p),
                    "n_constituents": len(p[4]),
                    "constituents":   p[4],
                })
            else:
                # merge i and j
                pi, pj_ = pj[best_i], pj[best_j]
                merged = [
                    pi[0] + pj_[0],
                    pi[1] + pj_[1],
                    pi[2] + pj_[2],
                    pi[3] + pj_[3],
                    pi[4] + pj_[4],
                ]
                # remove higher index first
                hi, lo = (best_i, best_j) if best_i > best_j else (best_j, best_i)
                pj.pop(hi); pj.pop(lo)
                pj.append(merged)

        return jets
