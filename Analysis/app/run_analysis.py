from __future__ import annotations
import sys
import json
from pathlib import Path

# -- make parent dir importable when running directly --------------------
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from framework import Framework
from modules.neutrino_generator import NeutrinoGenerator
#from modules.kinematic_summary import KinematicSummary
#from modules.multiplicity import Multiplicity
#from modules.jet_finder import JetFinder
#from modules.event_filter import EventFilter

import argparse
parser = argparse.ArgumentParser()
parser.add_argument("--sqrts", help = "Centre of mass energy", default = 91.2)
parser.add_argument("--input", help = "HEPMC event", required = True)
parser.add_argument("--max_events", help = "Maximum number of events to process", default = -1, type = int)
parser.add_argument("--neutrino_events", help = "GENIE gst events", default = None)
parser.add_argument("--calo_halflength", help = "Half-length of hadron calorimeter barrel", default = 2.8+1.8)
parser.add_argument("--calo_inner_radius", help = "Inner radius of hadron calorimeter barrel", default = 2.8)
parser.add_argument("--calo_outer_radius", help = "Outer radius of hadron calorimeter barrel", default = 2.8+1.8)

args = parser.parse_args()

def main():

    hepmc_file = args.input

    if len(sys.argv) < 2:
        print("Usage: python run_analysis.py <file.hepmc> [max_events]")
        sys.exit(1)

    # ── Build the pipeline ────────────────────────────────────────────────
    fw = Framework(hepmc_file, max_events=args.max_events, verbose=True)

    # Neutrino generator (for signal events only)
    fw.add_module(NeutrinoGenerator)

if __name__ == "__main__":
    main()
