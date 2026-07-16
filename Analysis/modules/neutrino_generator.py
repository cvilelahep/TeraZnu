from base_module import BaseModule
from event_record import EventRecord
import numpy as np
import uproot

from hepunits import units as u
class NeutrinoGenerator(BaseModule):
    
    @property
    def name(self) -> str:
        return "NeutrinoGenerator"

    def cross_section(self, pdg, energy, cc):
        try:
            splines = getattr(self, "xsec_splines")
            cc_string = "cc" if cc else "nc"

            e_bin = np.digitize(energy, splines[cc_string][pdg][0]*u.GeV)
            return splines[cc_string][pdg][1][e_bin]*1e-38*u.cm2

        except AttributeError:
            if pdg > 0:
                if cc:
                    return self.nu_CC_cross_section*energy
                else:
                    return self.nu_NC_cross_section*energy
            else:
                if cc:
                    return self.nubar_CC_cross_section*energy
                else:
                    return self.nubar_NC_cross_section*energy


    def __init__(self, geometry, cfg):
        self.geometry = geometry
        # For now use linear approximation. In future, get from generator (MadGraph?)
        self.nu_CC_cross_section = cfg["hadron_calorimeter"]["A"]*cfg["Neutrino"]["nu_CC_cross_section"]*u.cm2/u.GeV # cm2/GeV/nucleus; PDG 2025 world-average
        self.nubar_CC_cross_section = cfg["hadron_calorimeter"]["A"]*cfg["Neutrino"]["nubar_CC_cross_section"]*u.cm2/u.GeV # cm2/GeV/nucleus; PDG 2025 world-average
        if "cross_section_spline_file" in cfg["Neutrino"].keys():
            if (cfg["hadron_calorimeter"]["A"] == 56) and (cfg["hadron_calorimeter"]["Z"] == 26):
                self.xsec_splines = {}
                self.xsec_splines["cc"] = {}
                self.xsec_splines["nc"] = {}

                nuc_name = "Fe56"
                with uproot.open(cfg["Neutrino"]["cross_section_spline_file"]) as f:
                    for barness, sign in [["bar_", -1], ["", 1]]:
                        for p_id, p_flav in [[12, "e"], [14, "mu"]]:
                            self.xsec_splines["cc"][sign*p_id] = f[f"nu_{p_flav}_{barness}{nuc_name}"]["tot_cc"].values()
                            self.xsec_splines["nc"][sign*p_id] = f[f"nu_{p_flav}_{barness}{nuc_name}"]["tot_nc"].values() 
            else:
                print("Neutrino generator WARNING: nucleus not defined in spline file. Using simplified cross section model")

        self.target_density = self.geometry.density / (cfg["hadron_calorimeter"]["A"]*cfg["Constants"]["dalton"]*u.kg) # nuclei / cm3
       
        self.rng = cfg["rng"]

    def process(self, record: EventRecord) -> None:

        # Arrays for choosing interacting neutrino
        # For calculating interaction probability: path_length, pid, energy    
        path_length = []
        pid = []
        energy = []

        # For the record
        nu_vertex = []
        calo_interaction_length = []
        nu_mom = []

        # Loop through vertices:
        for i_p, p in record.particles.items():
            if not (p.status == 1): # Final state
                continue
            if abs(p.pid) not in [12, 14, 16]: # Neutrino
                continue

            nu_candidate_vtx = self.geometry.getRandomPointCalo(record.vertices[p.production_vertex].x, record.vertices[p.production_vertex].y, record.vertices[p.production_vertex].z, p.px, p.py, p.pz)

            path_length.append(nu_candidate_vtx["path_length_for_xsec"])
            pid.append(p.pid)
            energy.append(p.energy)

            nu_vertex.append(nu_candidate_vtx["vertex"])
            calo_interaction_length.append(nu_candidate_vtx["calo_interaction_length"])
            nu_mom.append([p.px, p.py, p.pz])

        interaction_probability = []
        for i in range(len(path_length)):
            this_x_sec = self.cross_section(pid[i], energy[i], True) # cm2 / nucleus
            interaction_probability.append(this_x_sec*self.target_density*path_length[i])

        cumulative = np.cumsum(interaction_probability)

        # No neutrinos in the acceptance. Do nothing.
        if cumulative[-1] == 0:
            return
        
        # Randomly pick interacting neutrino according to probability
        cumulative /= cumulative[-1]
        rand = self.rng.uniform()
        i_nu = np.digitize(rand, cumulative)

        # Add neutrino interaction to event record
        nu_gen_record = {}

        nu_gen_record["interaction_prob"] = np.sum(interaction_probability)
        nu_gen_record["vertex"] = nu_vertex[i_nu]
        nu_gen_record["momentum"] = nu_mom[i_nu]
        nu_gen_record["energy"] = energy[i_nu]
        nu_gen_record["pid"] = pid[i_nu]

        # TO-DO (with neutrino simulation)
        # Add hadronic energy
        # Add puch-through energy
        # Add muon kinematics
        # Add dual read-out calo measurements
        record.extras[self.name] = nu_gen_record

