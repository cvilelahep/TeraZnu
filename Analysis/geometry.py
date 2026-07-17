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

        if "outer_radius" in cfg["hadron_calorimeter"]:
            self.calo_or = cfg["hadron_calorimeter"]["outer_radius"]*u.m
            self.calo_tower_length = None
        elif "tower_length" in cfg["hadron_calorimeter"]:
            self.calo_or = None
            self.calo_tower_length = cfg["hadron_calorimeter"]["tower_length"]*u.m
        if self.calo_or is not None and self.calo_tower_length is not None:
            raise RuntimeError("Geometry configuration error. Only one of calorimeter outer radius and tower length can be defined, not both.")
        
        self.density = cfg["hadron_calorimeter"]["density"]*u.g/u.cm3
        self.Z = cfg["hadron_calorimeter"]["Z"]
        self.A = cfg["hadron_calorimeter"]["A"]
        self.interaction_length = cfg["hadron_calorimeter"]["interaction_length"]*u.cm

        if "max_eta" in cfg["hadron_calorimeter"]:
            self.max_eta = cfg["hadron_calorimeter"]["max_eta"]
            self.endcap_min_radius = None
            cfg["hadron_calorimeter"]["max_costheta"] = np.cos(2*np.arctan(np.exp(-self.max_eta)))
        elif "endcap_min_radius" in cfg["hadron_calorimeter"]:
            self.endcap_min_radius = cfg["hadron_calorimeter"]["endcap_min_radius"]
            self.max_eta = None
            cfg["hadron_calorimeter"]["max_costheta"] = np.cos(np.arctan2(cfg["hadron_calorimeter"]["endcap_min_radius"], 
                                                                          cfg["hadron_calorimeter"]["halflength"]))

        if self.endcap_min_radius is not None and self.max_eta is not None:
            raise RuntimeError("Geometry configuration error. Only one of calorimeter minimum endcap radius and max eta can be defined, not both.")

        self.inner_cylinder = Cylinder(point = [0, 0, 0], vector = [0, 0, self.calo_hl*2], radius = self.calo_ir)

        self.rng = cfg["rng"]

    def getRandomPointCalo(self, x, y, z, px, py, pz):

        pos = Point([x, y, z])
        mom = Vector([px, py, pz])

        inner_intersection = getIntersection(self.inner_cylinder, pos, mom)

        if self.calo_tower_length is not None:
            this_outer_radius = self.calo_ir+self.calo_tower_length*self.calo_ir/(inner_intersection[0][2]**2+self.calo_ir**2)**0.5
        else:
            this_outer_radius = self.calo_or
        outer_intersection = getIntersection(Cylinder(point = [0, 0, 0], vector = [0, 0, self.calo_hl*2], radius = this_outer_radius), pos, mom)

        if len(inner_intersection) > 1:
            raise RuntimeError("Geometry.getRandomPointCalo ERROR: multiple intersections of inner calo radius")
        inner_intersection = inner_intersection[0]
        if len(outer_intersection) > 1:
            raise RuntimeError("Geometry.getRandomPointCalo ERROR: multiple intersections of inner calo radius")
        outer_intersection = outer_intersection[0]

        if abs((outer_intersection - pos)[2]) > self.calo_hl:
            # In the barrel
            sign = +1 if (outer_intersection - pos)[2] > 0 else -1
            if self.calo_tower_length is not None:
                inner_plane_position = sign*(self.calo_hl-self.calo_tower_length*np.arctan2(self.calo_ir+self.calo_tower_length, self.calo_hl))
            else:
                inner_plane_position = sign*(self.calo_hl - self.calo_or + self.calo_ir)
            inner_plane = Plane([0, 0, inner_plane_position], [0, 0, sign])
            inner_intersection = inner_plane.intersect_line(Line(point = pos, direction = mom))
            mod_inner_intersection = (inner_intersection[0]**2 + inner_intersection[1]**2 + inner_intersection[2]**2)**0.5

            if self.calo_tower_length is not None:
                outer_plane_position = sign*(self.calo_hl + self.calo_tower_length*(np.abs(inner_intersection[2])/mod_inner_intersection-np.arctan2(self.calo_ir+self.calo_tower_length, self.calo_hl)))
            else:
                outer_plane_position = sign*self.calo_hl
            outer_plane = Plane([0, 0, outer_plane_position], [0, 0, sign])
            outer_intersection = outer_plane.intersect_line(Line(point = pos, direction = mom))

            # Outside acceptance
            if self.max_eta:
                if abs(np.arctanh(inner_intersection[2]/mod_inner_intersection)) > self.max_eta:
                    return {"path_length_for_xsec": 0., "calo_interaction_length": 0., "vertex": [0, 0, 0]}            
            elif self.endcap_min_radius:
                if (inner_intersection[0]**2 + inner_intersection[1]**2)**0.5 < self.endcap_min_radius:
                    return {"path_length_for_xsec": 0., "calo_interaction_length": 0., "vertex": [0, 0, 0]}

        out_in_vector = Vector(outer_intersection - inner_intersection)
        path_length_for_xsec = out_in_vector.norm()
        rand = self.rng.uniform()
        calo_interaction_lengths = path_length_for_xsec*(1-rand)/self.interaction_length
        vertex = inner_intersection + rand*out_in_vector

        return {"path_length_for_xsec": path_length_for_xsec, "calo_interaction_length": calo_interaction_lengths, "vertex": list(vertex)}
