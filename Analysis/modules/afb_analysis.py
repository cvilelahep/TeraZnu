from base_module import BaseModule
from event_record import EventRecord
import numpy as np

from iminuit import Minuit
from iminuit.cost import UnbinnedNLL

from hepunits import units as u

import matplotlib.pyplot as plt

SM_Afb = {12: 0.1468*3/4,
          14: 0.1468*3/4,
          16: 0.1468*3/4,
          11: 0.01617,
          13: 0.01617,
          15: 0.01617}

def integralFunAfb(costheta, afb):
    return 3./8*(costheta + 1./3*costheta**3 + 8./6*afb*costheta**2) # constant term omitted
def funAfb(costheta, afb, minval = -1, maxval = 1, sign = 1):
    norm = 1
    if minval != -1 or maxval != 1:
        norm = integralFunAfb(maxval, sign*afb) - integralFunAfb(minval, sign*afb)

    return 3./8*(1 + costheta**2 + 8./3*sign*afb*costheta)/norm

class AfbAnalysis(BaseModule):
    
    @property
    def name(self) -> str:
        return "AfbAnalysis"

    def __init__(self, cfg):
        self.lumi = cfg["FCC"]["luminosity"]/u.fb
        self.sqrts = cfg["FCC"]["sqrts"]*u.GeV
        self.N_IP = cfg["FCC"]["N_IP"]
        self.xsec = cfg["xsec"]*u.fb

        self.max_costheta = cfg["hadron_calorimeter"]["max_costheta"]

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
                          nu_record["interaction_prob"]])
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

        vertex_norm = np.sqrt(np.square(self.data[:,0]) + np.square(self.data[:,1]) +  np.square(self.data[:,2]))
        cos_theta = np.divide(self.data[:,2], vertex_norm)

        def pdf_nu(costheta, afb):
            return funAfb(costheta, afb, minval = -self.max_costheta, maxval = self.max_costheta, sign = 1)
        def pdf_nubar(costheta, afb):
            return funAfb(costheta, afb, minval = -self.max_costheta, maxval = self.max_costheta, sign = -1)

        cost = UnbinnedNLL(cos_theta[flavour_mask[14]], pdf_nu) + UnbinnedNLL(cos_theta[flavour_mask[-14]], pdf_nubar)
        m = Minuit(cost, afb = 0)
        m.migrad()
        m.hesse()

        print("MINUIT")
        print(m.values, m.errors)

        plt.figure()
        x = np.arange(-self.max_costheta, self.max_costheta, 0.01)
        bins = 30
        bin_range = (-1.5, 1.5)
        bin_width = (bin_range[1]-bin_range[0])/bins

        # define costhetamax
        flav_count = 0
        for f, mask in flavour_mask.items():
            plt.hist(cos_theta[mask], range = bin_range, bins = bins, weights = self.data[:,5][mask]*self.N_norm/self.counter, histtype = "step", label = f, color = f"C{flav_count}")
            nuAfb = bin_width*np.sum(self.data[:,5][mask]*self.N_norm/self.counter)*funAfb(x, SM_Afb[abs(f)], minval = -self.max_costheta, maxval = self.max_costheta, sign = np.sign(f)) # PDG Theory value
            plt.plot(x, nuAfb, label = f"SM prediction: {SM_Afb[abs(f)]:.2f}", color = f"C{flav_count}", linestyle = "-")

            nuAfb_best_fit = bin_width*np.sum(self.data[:,5][mask]*self.N_norm/self.counter)*funAfb(x, m.values["afb"], minval = -self.max_costheta, maxval = self.max_costheta, sign = np.sign(f)) # PDG Theory value
            plt.plot(x, nuAfb_best_fit, label = f"Best-fit point: {m.values["afb"]:.2f}", color = f"C{flav_count}", linestyle = ":")
            
            flav_count += 1
        plt.xlabel(r"cos$\theta$")
        plt.legend()

        plt.show()
        
