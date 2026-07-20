import shutil
from pathlib import Path

particle_dict = {"nue": "ve",
                 "numu": "vm",
                 "nutau": "vt",
                 "e": "e-",
                 "mu": "mu-",
                 "tau": "tau-"}
antiparticle_dict = {"nue": "ve~",
                     "numu": "vm~",
                     "nutau": "vt~",
                     "e": "e+",
                     "mu": "mu+",
                     "tau": "tau+"}

def make_card(params):
    job_name = params["job_name"]
    n_events = params["n_events"]
    
    flavour = params["flavour"]
    sqrts = params["sqrts"]
    ebeam = sqrts/2.

    if flavour not in ["nue", "numu", "nutau", "e", "mu", "tau"]:
        raise RuntimeError("Unknown flavour, must be nue numu or nutau")
    
    file_path = Path(job_name).with_suffix(".mgin")

    particle = particle_dict[flavour]
    antiparticle = antiparticle_dict[flavour]

    sin_text = ["import model sm",
                f"generate e- e+ > {particle} {antiparticle}",
                f"output {job_name}",
                "y",
                "launch",
                "0",
                f"set nevents {n_events}",
                f"set ebeam1 {ebeam}",
                f"set ebeam2 {ebeam}",
                "set lpp1 3",
                "set lpp2 -3",
                "set pdlabel1 isronlyll",
                "set pdlabel2 isronlyll",
                "done"]
    
    file_path.write_text("\n".join(sin_text))

for flav in ["nue", "e", "numu", "mu", "nutau", "tau"]:
    for sqrts in [87.9, 91.2, 93.9]:
        make_card({"job_name": f"test_{flav}_100k_{sqrts:.1f}_ISR",
                   "n_events": 100000,
                   "flavour": flav,
                   "sqrts": sqrts,
                   "circe2_file": "FCCee-2025-Z.circe",
                   "circe2_design": "FCCee/2025/Z/PA"})
    
