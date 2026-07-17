from base_module import BaseModule
from event_record import EventRecord
import numpy as np

from hepunits import units as u

import matplotlib.pyplot as plt

class Histogrammer(BaseModule):
    
    @property
    def name(self) -> str:
        return "Histogrammer"

    def __init__(self, cfg):
        self.lumi = cfg["FCC"]["luminosity"]/u.fb
        self.sqrts = cfg["FCC"]["sqrts"]*u.GeV
        self.N_IP = cfg["FCC"]["N_IP"]
        self.xsec = cfg["xsec"]*u.fb

        self.N_norm = self.N_IP*self.lumi*self.xsec

        self.counter = 0

        self.data = []

    def process(self, record: EventRecord):
        self.counter += 1

        try:
            nu_record = record.extras["NeutrinoGenerator"]
        except KeyError:
            return
        
        self.data.append([nu_record["vertex"][0],
                          nu_record["vertex"][1],
                          nu_record["vertex"][2],
                          nu_record["pid"],
                          nu_record["energy"],
                          nu_record["interaction_prob"],
                          nu_record["momentum"][0],
                          nu_record["momentum"][1],
                          nu_record["momentum"][2]])
    def end(self):
        self.data = np.array(self.data)
        
        flavour_mask = {}
        n_tot = 0.
        for f in set(self.data[:,3]):
            flavour_mask[f] = self.data[:,3] == f
            n_f = np.sum(self.data[:,5][flavour_mask[f]])*self.N_norm/self.counter
            n_tot += n_f
            print(f"Number of {f}: {n_f}")
        print(f"Total: {n_tot}")

        plt.figure()
        for f, mask in flavour_mask.items():
            plt.scatter(self.data[:,0][mask], self.data[:,1][mask], label = f, s = 0.01, alpha = 1)
        plt.xlabel("Neutrino vertex x [mm]")
        plt.ylabel("Neutrino vertex x [mm]")
        plt.legend()

        plt.figure()
        for f, mask in flavour_mask.items():
            plt.scatter(self.data[:,2][mask], self.data[:,1][mask], label = f, s = 0.01, alpha = 1)
        plt.xlabel("Neutrino vertex z [mm]")
        plt.ylabel("Neutrino vertex x [mm]")
        plt.legend()

        plt.figure()
        for f, mask in flavour_mask.items():
            plt.hist(self.data[:,4][mask], range = (41000, 47000), bins = 20, weights = self.data[:,5][mask]*self.N_norm/self.counter, label = f, histtype = "step")
        plt.xlabel("Neutrino energy [MeV]")
        plt.legend()

        plt.figure()
        phi = np.arctan2(self.data[:,1], self.data[:,0])
        for f, mask in flavour_mask.items():
            plt.hist(phi[mask], range = (-3.5, 3.5), bins = 70, weights = self.data[:,5][mask]*self.N_norm/self.counter, histtype = "step", label = f)
        plt.xlabel(r"$\phi$")
        plt.legend()

        vertex_norm = np.sqrt(np.square(self.data[:,0]) + np.square(self.data[:,1]) +  np.square(self.data[:,2]))
        cos_theta = np.divide(self.data[:,2], vertex_norm)

        for f, mask in flavour_mask.items():
            plt.figure()
            plt.hist2d(phi[mask], cos_theta[mask], range = ((-3.5, 3.5), (-1.5, 1.5)), bins = (70, 30), weights = self.data[:,5][mask]*self.N_norm/self.counter)
            plt.xlabel(r"$\phi$")
            plt.ylabel(r"cos$\theta$")
            plt.title(f"{f}")
            plt.colorbar()
        
        plt.figure()
        for f,mask in flavour_mask.items():
            plt.hist(self.data[:,5][mask], range = (0., 20e-10), bins = 80, histtype = "step", weights = self.data[:,5][mask]*self.N_norm/self.counter, label = f)
        plt.xlabel("Neutrino interaction probability")
        plt.legend()

        plt.show()
        
