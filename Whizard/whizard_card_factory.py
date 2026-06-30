import shutil
from pathlib import Path


def make_card(params):
    job_name = params["job_name"]
    n_events = params["n_events"]
    
    flavour = params["flavour"]
    sqrts = params["sqrts"]
    circe2_file = params["circe2_file"]
    circe2_design = params["circe2_design"]

    if flavour not in ["nue", "numu", "nutau", "e", "mu", "tau"]:
        raise RuntimeError("Unknown flavour, must be nue numu or nutau")
    
    
    dir_path = Path(job_name)
    if dir_path.exists():
        shutil.rmtree(dir_path)

    dir_path.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(circe2_file, dir_path / circe2_file)
    file_path = (dir_path / job_name).with_suffix(".sin")

    if "nu" in flavour:
        particle = flavour
        antiparticle = flavour+"bar"
    else:
        particle = flavour+"-"
        antiparticle = flavour+"+"

    sin_text = [f"process proc = \"e-\", \"e+\" => \"{particle}\",  \"{antiparticle}\"",
                "compile",
                f"sqrts = {sqrts} GeV",
                "beams = \"e-\", \"e+\" => circe2 => isr",
                f"$circe2_file = \"{circe2_file}\"",
                f"$circe2_design = \"{circe2_design}\"",
                "?circe2_polarized = false",
                "integrate(proc)",
                "simulate(proc) {",
                f"n_events = {n_events}",
                f"$sample = \"{job_name}\"",
                "sample_format = hepmc",
                "}",
                "compile_analysis"]
    
    file_path.write_text("\n".join(sin_text))


#for flav in ["nue", "numu", "nutau", "e", "mu", "tau"]:
for flav in ["numu", "mu"]:
    for sqrts in [87.9, 93.9]:
        make_card({"job_name": f"test_{flav}_100k_{sqrts:.1f}_ISR_PA",
                   "n_events": 100000,
                   "flavour": flav,
                   "sqrts": sqrts,
                   "circe2_file": "FCCee-2025-Z.circe",
                   "circe2_design": "FCCee/2025/Z/PA"})
    
