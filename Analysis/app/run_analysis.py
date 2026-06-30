from __future__ import annotations
import sys
import json
from pathlib import Path
from hepunits import units as u
# -- make parent dir importable when running directly --------------------
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from framework import Framework
from geometry import Geometry
from modules.neutrino_generator import NeutrinoGenerator
#from modules.kinematic_summary import KinematicSummary
#from modules.multiplicity import Multiplicity
#from modules.jet_finder import JetFinder
#from modules.event_filter import EventFilter

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--sqrts", help = "Centre of mass energy in GeV", default = 91.2)
    parser.add_argument("--input", help = "HEPMC event", required = True)
    parser.add_argument("--max_events", help = "Maximum number of events to process", default = -1, type = int)
    parser.add_argument("--neutrino_events", help = "GENIE gst events", default = None)
    parser.add_argument("--calo_halflength", help = "Half-length of hadron calorimeter barrel in m", default = 2.8+1.8)
    parser.add_argument("--calo_inner_radius", help = "Inner radius of hadron calorimeter barrel in m", default = 2.8)
    parser.add_argument("--calo_outer_radius", help = "Outer radius of hadron calorimeter barrel in m", default = 2.8+1.8)

    args = parser.parse_args()

    hepmc_file = args.input

    geometry = Geometry(args.calo_halflength*u.m, args.calo_inner_radius*u.m, args.calo_outer_radius*u.m, 11.34*u.g/u.cm3, Z=82, A=208, interaction_length = 19.93*u.cm)

    # ── Build the pipeline ────────────────────────────────────────────────
    fw = Framework(hepmc_file, max_events=args.max_events, verbose=False)

    # Neutrino generator (for signal events only)
    fw.add_module(NeutrinoGenerator(geometry))

    for record in fw.run():
        pass
    
if __name__ == "__main__":
    main()
