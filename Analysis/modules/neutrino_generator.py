from base_module import BaseModule
from event_record import EventRecord
import numpy as np

from hepunits import units as u
class NeutrinoGenerator(BaseModule):
    
    @property
    def name(self) -> str:
        return "NeutrinoGenerator"

    def __init__(self, geometry, cfg):
        self.geometry = geometry
        # For now use linear approximation. In future, get from generator (MadGraph?)
        self.nu_CC_cross_section = cfg["Neutrino"]["nu_CC_cross_section"]*u.cm2/u.GeV # cm2/GeV/nucleon; PDG 2025 world-average
        self.nubar_CC_cross_section = cfg["Neutrino"]["nubar_CC_cross_section"]*u.cm2/u.GeV # cm2/GeV/nucleon; PDG 2025 world-average

        self.target_density = self.geometry.density / (cfg["Constants"]["proton_mass"]*u.kg) # nucleons / cm3
       
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
            x_sec = self.nu_CC_cross_section*energy[i] if pid[i] > 0 else self.nubar_CC_cross_section*energy[i] # cm2 / nucleon
            interaction_probability.append(x_sec*self.target_density*path_length[i])
        
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

