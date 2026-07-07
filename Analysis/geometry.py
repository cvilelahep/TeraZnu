from skspatial.objects import Vector, Point, Line, Cylinder, Plane
import numpy as np
from hepunits import units as u

def getIntersection(cylinder, pos, mom):
    line = Line(point = pos, direction = mom)
    intersections = cylinder.intersect_line(line)

    ret = []
    for i in intersections:
        if (i - pos).dot(mom) > 0:
            ret.append(i)
    return ret

def getPlaneIntersection(plane, pos, mom):
    line = Line(point = pos, direction = mom)
    intersections = plane.intersect_line(line)

    ret = []
    for i in intersections:
        if (i - pos).dot(mom) > 0:
            ret.append(i)
    return ret


class Geometry:
    def __init__(self, cfg):
        self.calo_hl = cfg["hadron_calorimeter"]["halflength"]*u.m
        self.calo_ir = cfg["hadron_calorimeter"]["inner_radius"]*u.m
        self.calo_or = cfg["hadron_calorimeter"]["outer_radius"]*u.m
        self.calo_tower_length = self.calo_or - self.calo_ir
        self.density = cfg["hadron_calorimeter"]["density"]*u.g/u.cm3
        self.Z = cfg["hadron_calorimeter"]["Z"]
        self.A = cfg["hadron_calorimeter"]["A"]
        self.interaction_length = cfg["hadron_calorimeter"]["interaction_length"]*u.cm
        self.max_eta = cfg["hadron_calorimeter"]["max_eta"]

        self.inner_cylinder = Cylinder(point = [0, 0, 0], vector = [0, 0, self.calo_hl*2], radius = self.calo_ir)
        self.outer_cylinder = Cylinder(point = [0, 0, 0], vector = [0, 0, self.calo_hl*2], radius = self.calo_or)

        self.rng = cfg["rng"]

    def getRandomPointCalo(self, x, y, z, px, py, pz):

        pos = Point([x, y, z])
        mom = Vector([px, py, pz])

        inner_intersection = getIntersection(self.inner_cylinder, pos, mom)

        this_outer_radius = self.calo_ir+self.calo_tower_length*self.calo_ir/(inner_intersection[0][2]**2+self.calo_ir**2)**0.5
        outer_intersection = getIntersection(Cylinder(point = [0, 0, 0], vector = [0, 0, self.calo_hl*2], radius = this_outer_radius), pos, mom)

        if len(inner_intersection) > 1:
            raise RuntimeError("Geometry.getRandomPointCalo ERROR: multiple intersections of inner calo radius")
        inner_intersection = inner_intersection[0]
        if len(outer_intersection) > 1:
            raise RuntimeError("Geometry.getRandomPointCalo ERROR: multiple intersections of inner calo radius")
        outer_intersection = outer_intersection[0]

        if abs((outer_intersection - pos)[2]) > self.calo_hl:
            # In the barrel
            sign = +1 if (outer_intersection[0] - pos)[2] > 0 else -1
            inner_plane = Plane([0, 0, sign*(self.calo_hl-self.calo_tower_length*np.arctan2(self.calo_or, self.calo_hl))], [0, 0, sign])
            inner_intersection = inner_plane.intersect_line(Line(point = pos, direction = mom))
            mod_inner_intersection = (inner_intersection[0]**2 + inner_intersection[1]**2 + inner_intersection[2]**2)**0.5

            # Outside acceptance
            if abs(np.arctanh(inner_intersection[2]/mod_inner_intersection)) > self.max_eta:
                return {"path_length_for_xsec": 0., "calo_interaction_length": 0., "vertex": [0, 0, 0]}

            outer_plane = Plane([0, 0, sign*(self.calo_hl + self.calo_tower_length*(np.abs(inner_intersection[2])/mod_inner_intersection-np.arctan2(self.calo_or, self.calo_hl)))], [0, 0, sign])
            outer_intersection = outer_plane.intersect_line(Line(point = pos, direction = mom))

        out_in_vector = Vector(outer_intersection - inner_intersection)
        path_length_for_xsec = out_in_vector.norm()
        rand = self.rng.uniform()
        calo_interaction_lengths = path_length_for_xsec*(1-rand)/self.interaction_length
        vertex = inner_intersection + rand*out_in_vector

        return {"path_length_for_xsec": path_length_for_xsec, "calo_interaction_length": calo_interaction_lengths, "vertex": list(vertex)}
