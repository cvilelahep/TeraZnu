from base_module import BaseModule
from event_record import EventRecord

class NeutrinoGenerator(BaseModule):
    # For now use linear approximation. In future, get from generator (MadGraph?)
    nu_CC_cross_section = 0.667e-38 # cm2/GeV/nucleon; PDG 2025 world-average
    nubar_CC_cross_section = 0.334e-38 # cm2/GeV/nucleon; PDG 2025 world-average
    
    def __init__(self, calorimeter_model: dict = {}):
        self.calorimeter_model = calorimeter_model

    @property
    def name(self) -> str:
        return "NeutrinoGenerator"

    def process(self, record: EventRecord) -> None:

        path_lengths = []
        pids = []
        energies = []

        # Loop through vertices:
        for i_v, v in record.vertices.items:
            print(i_v, v)
            for i_p, p in enumerate(v.particles_out):
                if not (p.status == 1): # Final state
                    continue
                if abs(p.pid) not in [12, 14, 16]: # Neutrino
                    continue
                print(f"Found neutrino {p.pid} pos ({v.x}, {v.y}, {v.z}) mom ({p.px}, {p.py}, {p.pz})")
