#-------------------------------------------------------------------------------
#
# shape.py -- new flock experiments
#
# Geometric utilities to help describe 3d shapes, particularly for the ray-shape
# intersection calculations used in obstacle avoidance.
#
# MIT License -- Copyright © 2023 Craig Reynolds
#
#-------------------------------------------------------------------------------

import math
from Vec3 import Vec3
#from Draw import Draw
#import Utilities as util


# Given a ray and a cylinder, find the intersection nearest the ray's origin
# (endpoint), or None.
#
# TODO Currently ignores the endpoints, assuming the cylinder is infinitely long.
#
# Using the derivation by Nominal Animal:
#     https://en.wikipedia.org/wiki/User:Nominal_animal
#     https://math.stackexchange.com/a/1732445/516283
#     https://www.nominal-animal.net
#
def ray_cylinder_intersection(ray_endpoint, ray_tangent,
                              cyl_endpoint, cyl_tangent,
                              cyl_radius, cyl_length):
    intersection = None
    def sq(s):
        return s * s

    # Rename to match https://en.wikipedia.org/wiki/User:Nominal_animal
    b = cyl_endpoint  # The 3d origin/end/endpoint of the cylinder on its axis.
    a = cyl_tangent   # Unit 3d vector parallel to cylinder axis.
    r = cyl_radius    # Scalar cylinder radius.
    h = cyl_length    # Scalar length from endpoint along axis to other end.
    
    o = ray_endpoint  # The 3d origin/end/endpoint of ray.
    n = ray_tangent   # Unit 3d vector parallel to ray.
    
    b = b - o         # Offset b by the ray's origin/end/endpoint
    
    assert a.is_unit_length()
    assert n.is_unit_length()

    na = n.cross(a)
    r2 = r * r
    
    radicand = (na.dot(na) * r2) - sq(b.dot(na))

    # If any (real valued) intersections exist (both same if radicand==0)
    if radicand >= 0:
        radical = math.sqrt(radicand)
        ba = b.cross(a)
#        nana = na.dot(na)
#        d1 = (na.dot(ba) + radical) / nana
#        d2 = (na.dot(ba) - radical) / nana
        nana = na.dot(na)
        naba = na.dot(ba)
        d1 = (naba + radical) / nana
        d2 = (naba - radical) / nana
        if d1 >= 0:
            intersection = o + n * d1
        if d2 >= 0 and d2 < d1:
            intersection = o + n * d2
    return intersection
