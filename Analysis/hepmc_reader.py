from __future__ import annotations
from event_record import EventRecord, Particle, Vertex
import pyhepmc
class HepmcReader:
    def __init__(self, path: str):
        self.path = path


    def __iter__(self):
        with pyhepmc.open(self.path) as f_hepmc:
            while(event := f_hepmc.read()): 
                record = EventRecord()
                
                for v in event.vertices:
                    barcode = v.id
                    x = v.position.x
                    y = v.position.y
                    z = v.position.z
                    t = v.position.t
                
                    record.vertices[barcode] = Vertex(barcode,x, y, z, t)
                
                for p in event.particles:
                    barcode = p.id
                    prod_vertex = p.production_vertex.id
                    if p.end_vertex:
                        end_vertex = p.end_vertex.id
                    else:
                        end_vertex = None
                    pdg = p.pid
                    status = p.status
                    px = p.momentum.x
                    py = p.momentum.y
                    pz = p.momentum.z
                    E = p.momentum.t
                    m = p.generated_mass
                
                    record.particles[barcode] = Particle(barcode, pdg, status, px, py, pz, E, m, prod_vertex, end_vertex)
                
                    if prod_vertex in record.vertices:
                        record.vertices[prod_vertex].particles_out.append(barcode)
                    if end_vertex is not None and end_vertex in record.vertices:
                        record.vertices[end_vertex].particles_in.append(barcode)
                
                yield record
