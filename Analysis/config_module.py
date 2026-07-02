import tomllib 
import numpy as np

class Config():

    def parseToml(self):
        with open(self.d["toml_config_file"], "rb") as f:
            self.d.update(tomllib.load(f))

    def __init__(self, args):
        self.d = {}

        self.d["hepmc_file"] = args.input
        self.d["seed"] = args.seed
        self.d["rng"] = np.random.default_rng(self.d["seed"])
        
        self.d["toml_config_file"] = args.configuration
        self.parseToml()
        self.d["xsec"] = args.xsec
        self.d["max_events"] = args.max_events
        self.d["neutrino_input"] = args.neutrino_input

    def __getitem__(self, key):
        return self.d[key]
