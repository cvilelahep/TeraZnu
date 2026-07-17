"""
examples/run_analysis.py — End-to-end example using the framework.

Run with:
    python examples/run_analysis.py path/to/events.hepmc [max_events]
"""
from __future__ import annotations
import sys
import json
from pathlib import Path

# -- make parent dir importable when running directly --------------------
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from framework import Framework
from modules.kinematic_summary import KinematicSummary
from modules.multiplicity import Multiplicity
from modules.jet_finder import JetFinder
from modules.event_filter import EventFilter


def main():
    if len(sys.argv) < 2:
        print("Usage: python run_analysis.py <file.hepmc> [max_events]")
        sys.exit(1)

    hepmc_file = sys.argv[1]
    max_events = int(sys.argv[2]) if len(sys.argv) > 2 else -1

    # ── Build the pipeline ────────────────────────────────────────────────
    fw = Framework(hepmc_file, max_events=max_events, verbose=True)

    # 1. basic kinematics (no deps)
    fw.add_module(KinematicSummary())

    # 2. particle counts
    fw.add_module(Multiplicity())

    # 3. jet finding — uses anti-kT R=0.4, 25 GeV pT cut
    fw.add_module(JetFinder(R=0.4, pt_cut=25.0, algorithm="anti_kt"))

    # 4. event filter — requires ≥2 jets and MET > 50 GeV
    #    (runs AFTER jet finder and kinematic summary, so their results are available)
    cuts = {
        "n_jets>=2": lambda r: r.extras.get("JetFinder", {}).get("n_jets", 0) >= 2,
        "MET>50GeV": lambda r: r.extras.get("KinematicSummary", {}).get("MET", 0.0) > 50.0,
    }
    fw.add_module(EventFilter(cuts))

    # ── Run and collect summary stats ─────────────────────────────────────
    ht_values  = []
    jet_counts = []
    n_passed   = 0

    for record in fw.run():
        kin  = record.extras.get("KinematicSummary", {})
        jets = record.extras.get("JetFinder", {})
        filt = record.extras.get("EventFilter", {})

        if kin:
            ht_values.append(kin["HT"])
        if jets:
            jet_counts.append(jets["n_jets"])
        if filt.get("passed"):
            n_passed += 1
    plt.show()

    # ── Print summary ─────────────────────────────────────────────────────
    if ht_values:
        print(f"\n── Kinematic summary ──────────────────────────────")
        print(f"  Mean HT : {sum(ht_values) / len(ht_values):.1f} GeV")
        print(f"  Max HT  : {max(ht_values):.1f} GeV")

    if jet_counts:
        print(f"\n── Jet summary ────────────────────────────────────")
        print(f"  Mean N_jets : {sum(jet_counts) / len(jet_counts):.2f}")
        print(f"  Max  N_jets : {max(jet_counts)}")

    print(f"\n── Selection ──────────────────────────────────────")
    print(f"  Events passing all cuts : {n_passed}")


if __name__ == "__main__":
    main()
