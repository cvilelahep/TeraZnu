from base_module import BaseModule
from event_record import EventRecord
from geometry import Geometry

from hepunits import units as u

class NeutrinoGenerator(BaseModule):
    
    @property
    def name(self) -> str:
        return "NeutrinoGenerator"

    def __init__(self, geometry):
        self.geometry = geometry
        # For now use linear approximation. In future, get from generator (MadGraph?)
        self.nu_CC_cross_section = 0.667e-38*u.cm2/u.GeV # cm2/GeV/nucleon; PDG 2025 world-average
        self.nubar_CC_cross_section = 0.334e-38*u.cm2/u.GeV # cm2/GeV/nucleon; PDG 2025 world-average

    def process(self, record: EventRecord) -> None:

        print("NeutrinoGenerator called")

        # Arrays for choosing interacting neutrino
        # For calculating interaction probability: path_length, pid, energy    
        path_length = []
        pid = []
        energy = []

        # Useful for later
        nu_vertex = []
        calo_interaction_length = []

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

            print(f"Found neutrino {p.pid} pos ({record.vertices[p.production_vertex].x}, {record.vertices[p.production_vertex].y}, {record.vertices[p.production_vertex].z}) mom ({p.px}, {p.py}, {p.pz})")
            print(nu_candidate_vtx)

