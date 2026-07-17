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
from modules.histogrammer import Histogrammer
from modules.afb_analysis import AfbAnalysis

from config_module import Config

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--sqrts", help = "Centre of mass energy in GeV", default = 91.2)
    parser.add_argument("--input", help = "HEPMC event", required = True)
    parser.add_argument("--xsec", help = "Cross section of HEPMC events in fb", type = float, required = True)
    parser.add_argument("--configuration", help = "Configuration file with detector and accelerator parameter", required = True, type = str)
    parser.add_argument("--max_events", help = "Maximum number of events to process", default = -1, type = int)
    parser.add_argument("--neutrino_input", help = "GENIE gst events", default = None)
    parser.add_argument("--seed", help = "Random number seed", type = int, default = 314159)

    args = parser.parse_args()

    cfg = Config(args)

    geometry = Geometry(cfg)

    # ── Build the pipeline ────────────────────────────────────────────────
    fw = Framework(cfg["hepmc_file"], max_events=cfg["max_events"], verbose=True)

    # Neutrino generator (for signal events only)
    fw.add_module(NeutrinoGenerator(geometry, cfg))

    # Histogrammer
    #fw.add_module(Histogrammer(cfg))

    # Afb analysis
    fw.add_module(AfbAnalysis(cfg))

    for record in fw.run():
        pass
    
if __name__ == "__main__":
    main()
