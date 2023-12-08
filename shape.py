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

# Returns the point of intersection of a ray (half-line) and sphere. Used
# for finding intersection of an Agent's "forward" axis with a spherical
# containment. Returns None if there is no intersection. Returns nearest
# intersection if there are two, eg Agent outside sphere flying toward it.
#
# Formulation from https://en.wikipedia.org/wiki/Line–sphere_intersection
# particularly the two equations under the text "Note that in the specific
# case where U is a unit vector..."
#
def ray_sphere_intersection(ray_origin, ray_tangent, sphere_radius, sphere_center):
    intersection = None
    # Center and radius of sphere.
    c = sphere_center
    r = sphere_radius
    # Origin/endpoint and tangent (basis) of ray.
    o = ray_origin
    u = ray_tangent
    # Following derivation in Wikipedia.
    delta = (u.dot(o - c) ** 2) - (((o - c).length() ** 2) - r ** 2)
    # Does the line containing the ray intersect the sphere?
    if delta >= 0:
        # Find the 2 intersections of the line containing the ray.
        sqrt_delta = math.sqrt(delta)
        u_dot_oc = -(u.dot(o - c))
        d1 = u_dot_oc + sqrt_delta
        d2 = u_dot_oc - sqrt_delta
        p1 = o + u * d1
        p2 = o + u * d2
        # Select point on ("forward") ray, if both, use one nearer origin.
        if d1 >= 0:
            intersection = p1
        if d2 >= 0 and d2 < d1:
            intersection = p2
    return intersection

# Returns the point of intersection of a ray (half-line) and a plane. Or it
# returns None if there is no intersection because the line and plane are
# parallel. A ray represents an Agent's position and forward axis. Based
# upon: https://en.wikipedia.org/wiki/Line–plane_intersection#Algebraic_form
def ray_plane_intersection(ray_origin, ray_tangent, plane_origin, plane_normal):
    intersection = None
    numerator = (plane_origin - ray_origin).dot(plane_normal)
    denominator = ray_tangent.dot(plane_normal)
    if denominator != 0:
        d = numerator / denominator
        if d > 0:  # True if intersection is "forward" of the ray_origin
            intersection = ray_origin + ray_tangent * d
    return intersection

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
    radicand = (na.dot(na) * sq(r)) - sq(b.dot(na))

    # If any (real valued) intersections exist (both same if radicand==0)
    if radicand >= 0:
        radical = math.sqrt(radicand)
        ba = b.cross(a)
        nana = na.dot(na)
        naba = na.dot(ba)
        d1 = (naba + radical) / nana
        d2 = (naba - radical) / nana
        if d1 >= 0:
            intersection = o + n * d1
        if d2 >= 0 and d2 < d1:
            intersection = o + n * d2
    return intersection


def unit_test():
    zzz = Vec3()
    ooo = Vec3(1, 1, 1)
    ozz = Vec3(1, 0, 0)
    zoz = Vec3(0, 1, 0)
    mzz = Vec3(-1, 0, 0)
    ddd = ooo.normalize()

    # Unit tests for ray_sphere_intersection()
    def rsi(result, ao, at, sr, sc, description):
        i = ray_sphere_intersection(ao, at, sr, sc)
        assert i == result, ('ray_sphere_intersection() unit test -- '
                             + description + ' -- expecting ' + str(result)
                             + ' but got ' + str(i))
    rsi(ozz, ozz * 2, mzz, 1, zzz,
        'ray endpoint outside sphere (+x), pointing toward sphere')
    rsi(mzz, mzz * 2, ozz, 1, zzz,
        'ray endpoint outside sphere (-x), pointing toward sphere')
    rsi(None, mzz, zoz, 0.5, zzz,
       'clean miss, agent outside, +x of sphere, pointing up')
    rsi(ozz, ozz, zoz, 1, zzz,
        'intersect at point, ray origin on +x edge of sphere pointing up')
    rsi(ozz * 2, mzz, ozz, 2, zzz,
       'typical case inside r=2 sphere, ray at -1 on x axis pointing +x')
    rsi(ozz * math.sqrt(3), mzz, ozz, 2, zoz,
        'radius 2 sphere at (0,1,0), ray at (-1,0,0) pointing +x')
        
    # Unit tests for ray_plane_intersection()
    def rpi(result, ro, rt, po, pn):
        i = ray_plane_intersection(ro, rt, po, pn)
        assert i == result, 'test Vec3.ray_plane_intersection()'
    rpi(None, mzz, mzz, zzz, ozz)
    rpi(zzz, ozz * 2, ozz *-1, zzz, ozz)
    rpi(ozz * 3, zzz, ozz, ooo, ddd * -1)


    # Unit tests for ray_cylinder_intersection()
    def rci(result, re, rt, ce, ct, cr, cl, description):
        i = ray_cylinder_intersection(re, rt, ce, ct, cr, cl)
        assert i == result, ('shape.ray_cylinder_intersection() unit test -- '
                             + description + ' -- expecting ' + str(result)
                             + ' but got ' + str(i))
    rci(Vec3(1, 0, 0),
        Vec3(2, 0, 0),
        Vec3(-1, 0, 0),
        Vec3(0, -1, 0),
        Vec3(0, 1, 0),
        1,
        2,
        'ray endpoint outside cylinder (+x), pointing toward cylinder')

