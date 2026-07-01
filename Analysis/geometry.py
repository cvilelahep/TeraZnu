from skspatial.objects import Vector, Point, Line, Cylinder
import numpy as np

def getIntersection(cylinder, pos, mom):
    line = Line(point = pos, direction = mom)
    intersections = cylinder.intersect_line(line)

    ret = []
    for i in intersections:
        if (i - pos).dot(mom) > 0:
            ret.append(i)
    return ret


class Geometry:
    def __init__(self, calo_halflength, calo_inner_radius, calo_outer_radius, density, Z, A, interaction_length):
        self.calo_hl = calo_halflength
        self.calo_ir = calo_inner_radius
        self.calo_or = calo_outer_radius
        self.density = density
        self.Z = Z
        self.A = A
        self.interaction_length = interaction_length

        self.inner_cylinder = Cylinder(point = [0, 0, 0], vector = [0, 0, self.calo_hl*2], radius = self.calo_ir)
        self.outer_cylinder = Cylinder(point = [0, 0, 0], vector = [0, 0, self.calo_hl*2], radius = self.calo_or)

        self.rng = np.random.default_rng(314159)

    def getRandomPointCalo(self, x, y, z, px, py, pz):

        pos = Point([x, y, z])
        mom = Vector([px, py, pz])

        inner_intersection = getIntersection(self.inner_cylinder, pos, mom)
        outer_intersection = getIntersection(self.outer_cylinder, pos, mom)        
        
        if len(inner_intersection) > 1:
            raise RuntimeError("Geometry.getRandomPointCalo ERROR: multiple intersections of inner calo radius")
        if len(outer_intersection) > 1:
            raise RuntimeError("Geometry.getRandomPointCalo ERROR: multiple intersections of inner calo radius")

        # For now, accept only events in the barrel. NOT GOOD, missing out on 40% of nus!
        if abs((outer_intersection[0] - pos)[2]) > self.calo_hl:
            return {"path_length_for_xsec": 0,
                    "calo_interaction_length": 0,
                    "vertex": Point([0, 0, 0])}
        else:
            out_in_vector = Vector(outer_intersection[0] - inner_intersection[0])

            path_length_for_xsec = out_in_vector.norm()
            rand = self.rng.uniform()
            calo_interaction_lengths = path_length_for_xsec*(1-rand)/self.interaction_length
            vertex = inner_intersection[0] + rand*out_in_vector


            return {"path_length_for_xsec": path_length_for_xsec, "calo_interaction_length": calo_interaction_lengths, "vertex": list(vertex)}
