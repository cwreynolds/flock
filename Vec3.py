#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
#
# Vec3.py -- new flock experiments
#
# Cartesian 3d vector space utility.
#
# MIT License -- Copyright © 2023 Craig Reynolds
#
#-------------------------------------------------------------------------------

import math
import numpy as np
import Utilities as util

class Vec3:
    """Utility class for 3d vectors and operations on them."""
    
    # Instance constructor.
    def __init__(self, x=0, y=0, z=0):
        # This vector's 3d coordinates.
        self.x = x
        self.y = y
        self.z = z

    # Alternate constructor, aka factory, to construct Vec3 from any array-like.
    @staticmethod  # This decoration seems to be completely optional,
                   # but for the avoidance of doubt
    def from_array(array_like):
        a = np.asarray(array_like)
        return Vec3(a[0], a[1], a[2])
        
    # Return contents of this Vec3 as an np.array.
    def asarray(self):
        return np.array([self.x, self.y, self.z])
        
    def __str__(self):
        return (self.__class__.__name__ + "(" +
                str(self.x) + ", " + str(self.y) + ", " + str(self.z) + ")")

    def __eq__(self, v):
        return (isinstance(v, self.__class__) and
                v.x == self.x and
                v.y == self.y and
                v.z == self.z)
                
    def __ne__(self, v):
        return not (self == v)
        
    def __lt__(self, v):
        return self.length() < v.length()
        
    def __add__(self, v):
        return Vec3(self.x + v.x, self.y + v.y, self.z + v.z)

    def __sub__(self, v):
        return Vec3(self.x - v.x, self.y - v.y, self.z - v.z)

    def __mul__(self, scale):
        return Vec3(self.x * scale, self.y * scale, self.z * scale)
    
    def __rmul__(self, scale):
        return Vec3(self.x * scale, self.y * scale, self.z * scale)

    def __truediv__(self, scale):
        return Vec3(self.x / scale, self.y / scale, self.z / scale)

    def __neg__(self):
        return Vec3(-self.x, -self.y, -self.z)

    # Vector operations dot product, length (norm), normalize.
    def dot(self, v):
        return (self.x * v.x) + (self.y * v.y) + (self.z * v.z)
    def length(self):
        return math.sqrt(self.length_squared())
    def length_squared(self):
        return self.dot(self)
    def normalize(self):
        return self / self.length()

    # Normalize except if input is zero length, then return that.
    def normalize_or_0(self):
        return self if self.is_zero_length() else self.normalize()

    # Normalize and return length
    def normalize_and_length(self):
        original_length = self.length()
        return (self / original_length, original_length)

    # Fast check for unit length.
    def is_unit_length(self):
        return util.within_epsilon(self.length_squared(), 1)

    # Fast check for zero length.
    def is_zero_length(self):
        return util.within_epsilon(self.length_squared(), 0)

    # Returns vector parallel to "this" but no longer than "max_length"
    def truncate(self, max_length):
        len = self.length()
        return self if len <= max_length else self * (max_length / len)

    # return component of vector parallel to a unit basis vector
    def parallel_component(self, unit_basis):
        assert unit_basis.is_unit_length()
        projection = self.dot(unit_basis)
        return unit_basis * projection

    # return component of vector perpendicular to a unit basis vector
    def perpendicular_component(self, unit_basis):
        return self - self.parallel_component(unit_basis)

    # Cross product
    def cross(a, b):
        # (From https://en.wikipedia.org/wiki/Cross_product#Matrix_notation)
        return Vec3(a.y * b.z - a.z * b.y,
                    a.z * b.x - a.x * b.z,
                    a.x * b.y - a.y * b.x)

    # Get angle between two arbitrary direction vectors. (Visualize two vectors
    # placed tail to tail, the angle is measured on the plane containing both.
    # See https://commons.wikimedia.org/wiki/File:Inner-product-angle.svg)
    def angle_between(a, b):
        return math.acos(a.dot(b) / (a.length() * b.length()))

    # Returns a vector describing a rotation around an arbitrary axis by a given
    # angle. The axis must pass through the global origin but any orientation is
    # allowed, as defined by the direction of the first argument. The return
    # value is effectively the axis with its length set to the angle (expressed
    # in radians). See https://en.wikipedia.org/wiki/Axis–angle_representation
    def axis_angle(axis, angle):
        aa = Vec3()
        if angle != 0 and axis.length_squared() > 0:
            aa = axis.normalize() * angle
        return aa

    # Given two vectors, return an axis_angle that rotates the first to the
    # second. (Length of input vectors is irrelevant.)
    def rotate_vec_to_vec(from_vec, to_vec):
        return Vec3.axis_angle(Vec3.cross(from_vec, to_vec),
                               Vec3.angle_between(from_vec, to_vec))


    # Check if two vectors are perpendicular. (What about zero length?)
    def is_perpendicular(self, other):
        # TODO 20230430 Should it check for unit length, or normalize? For now,
        # assert that given vectors are unit length to see if it ever comes up.
        assert self.is_unit_length()
        assert other.is_unit_length()
        return util.within_epsilon(self.dot(other), 0)
    
    # Check if two unit vectors are parallel (or anti-parallel).
    def is_parallel(self, other):
        # TODO 20230430 Should it check for unit length, or normalize? For now,
        # assert that given vectors are unit length to see if it ever comes up.
        assert self.is_unit_length()
        assert other.is_unit_length()
        return util.within_epsilon(abs(self.dot(other)), 1)
    
    # Given a (unit) vector, return some vector that is purpendicular.
    # (There are infinitely many such vectors, one is chosen arbitrarily.)
    def find_perpendicular(self):
        perpendicular = None
        reference = Vec3(1, 0, 0) # Any vector NOT parallet to "self"
        # If "self" is parallel to initial "reference":
        if self.is_parallel(reference):
            # Return fixed perpendicular to initial "reference".
            perpendicular = Vec3(0, 1, 0)
        else:
            # return cross product with non-parallel "reference".
            perpendicular = self.cross(reference).normalize()
        return perpendicular

    # Check if two vectors are within epsilon of being equal.
    def is_equal_within_epsilon(self, other):
        bigger_epsilon = util.epsilon * 10  # Got occasional fail with default.
        return (util.within_epsilon(self.x, other.x, bigger_epsilon) and
                util.within_epsilon(self.y, other.y, bigger_epsilon) and
                util.within_epsilon(self.z, other.z, bigger_epsilon))

    # Rotate X and Y values about the Z axis by given angle.
    # This is used in combination with a LocalSpace transform to get model in
    # correct orientation. A more generalized "rotate about given axis by given
    # angle" might be nice to have for convenience.
    def rotate_xy_about_z(self, angle):
        s = math.sin(angle)
        c = math.cos(angle)
        return Vec3(self.x * c + self.y * s,
                    self.y * c - self.x * s,
                    self.z)

    def rotate_xz_about_y(self, angle):
        s = math.sin(angle)
        c = math.cos(angle)
        return Vec3(self.x * c + self.z * s,
                    self.y,
                    self.z * c - self.x * s)

    # class RandomSequence
    # Vec3 randomUnitVector();
    # does Python allow the trick where RandomSequence is defined one
    # place but RandomSequence::randomUnitVector() is defined elsewhere?
    # oh, maybe yes: https://stackoverflow.com/a/2982/1991373

    # Generate a random point in an axis aligned box, given two opposite corners.
    @staticmethod
    def random_point_in_axis_aligned_box(a, b):
        return Vec3(util.random2(min(a.x, b.x), max(a.x, b.x)),
                    util.random2(min(a.y, b.y), max(a.y, b.y)),
                    util.random2(min(a.z, b.z), max(a.z, b.z)))

    # Generate a random point inside a unit diameter disk centered on origin.
    @staticmethod
    def random_point_in_unit_radius_sphere():
        v = None
        while True:
            v = Vec3.random_point_in_axis_aligned_box(Vec3(-1, -1, -1),
                                                      Vec3(1, 1, 1))
            if v.length() <= 1:
                break
        return v;

    # Generate a random unit vector.
    @staticmethod
    def random_unit_vector():
        v = None
        m = None
        while True:
            v = Vec3.random_point_in_unit_radius_sphere()
            m = v.length()
            if m > 0:
                break
        return v / m;

    # Given any number of Vec3s, return the one with the max length.
    @staticmethod
    def max(*any_number_of_Vec3s):
        longest = Vec3()
        magnitude2 = 0
        for v in any_number_of_Vec3s:
            vm2 = v.length_squared()
            if magnitude2 < vm2:
                magnitude2 = vm2
                longest = v
        return longest

    @staticmethod
    def unit_test():
        v000 = Vec3(0, 0, 0)
        v100 = Vec3(1, 0, 0)
        v010 = Vec3(0, 1, 0)
        v001 = Vec3(0, 0, 1)
        v011 = Vec3(0, 1, 1)
        v101 = Vec3(1, 0, 1)
        v110 = Vec3(1, 1, 0)
        v111 = Vec3(1, 1, 1)
        v123 = Vec3(1, 2, 3)
        v236 = Vec3(2, 3, 6)

        assert str(Vec3(1, 2, 3)) == 'Vec3(1, 2, 3)'
        assert Vec3(1, 2, 3) == Vec3(1, 2, 3)
        assert Vec3(0, 0, 0) != Vec3(1, 0, 0)
        assert Vec3(0, 0, 0) != Vec3(0, 1, 0)
        assert Vec3(0, 0, 0) != Vec3(0, 0, 1)
        assert Vec3(1, 2, 3) == Vec3.from_array([1, 2, 3])
        assert np.array_equal(Vec3(1, 2, 3).asarray(), [1, 2, 3])
        assert Vec3(1, 2, 3).dot(Vec3(4, 5, 6)) == 32
        assert Vec3(2, 3, 6).length() == 7
        assert Vec3(2, 3, 6).normalize() == Vec3(2, 3, 6) / 7
        assert Vec3(3, 0, 0).truncate(2) == Vec3(2, 0, 0)
        assert Vec3(1, 0, 0).truncate(2) == Vec3(1, 0, 0)
        assert Vec3(1, 2, 3) + Vec3(4, 5, 6) == Vec3(5, 7, 9)
        assert Vec3(5, 7, 9) - Vec3(4, 5, 6) == Vec3(1, 2, 3)
        assert -Vec3(1, 2, 3) == Vec3(-1, -2, -3)
        assert Vec3(1, 2, 3) * 2 == Vec3(2, 4, 6)
        assert 2 * Vec3(1, 2, 3) == Vec3(2, 4, 6)
        assert Vec3(2, 4, 6) / 2 == Vec3(1, 2, 3)
        assert Vec3(1, 2, 3) < Vec3(-1, -2, -4)

        (n, l) = v123.normalize_and_length()
        assert (n == v123.normalize()) and (l == v123.length())
        
        assert v000.is_zero_length()
        assert not v111.is_zero_length()

        assert v000.normalize_or_0() == v000
        assert v236.normalize_or_0() == Vec3(2, 3, 6) / 7
        
        assert not v000.is_unit_length()
        assert not v111.is_unit_length()
        assert v123.normalize().is_unit_length()
        
        assert Vec3.max(v000) == v000
        assert Vec3.max(v000, v111) == v111
        assert Vec3.max(v111, v000) == v111
        assert Vec3.max(v123, v111, v236, v000) == v236
        
        for i in range(20):
            r = Vec3.random_point_in_axis_aligned_box(v236, v123)
            assert util.between(r.x, v123.x, v236.x)
            assert util.between(r.y, v123.y, v236.y)
            assert util.between(r.z, v123.z, v236.z)
            
            r = Vec3.random_point_in_unit_radius_sphere()
            assert r.length() <= 1

            r = Vec3.random_unit_vector()
            assert util.within_epsilon(r.length(), 1)

        f33 = 0.3333333333333334
        f66 = 0.6666666666666665
        x_norm = Vec3(1, 0, 0)
        diag_norm = Vec3(1, 1, 1).normalize()
        assert Vec3(2, 4, 8).parallel_component(x_norm) == Vec3(2, 0, 0)
        assert Vec3(2, 4, 8).perpendicular_component(x_norm) == Vec3(0, 4, 8)
        assert x_norm.parallel_component(diag_norm) == Vec3(f33, f33, f33)
        assert x_norm.perpendicular_component(diag_norm) == Vec3(f66, -f33, -f33)
        
        a = Vec3(1, 2, 3).normalize()
        b = Vec3(-9, 7, 5).normalize()
        c = Vec3(1, 0, 0)
        assert a.is_parallel(a)
        assert a.is_parallel(-a)
        assert not a.is_parallel(b)
        assert a.is_perpendicular(a.find_perpendicular())
        assert b.is_perpendicular(b.find_perpendicular())
        assert c.is_perpendicular(c.find_perpendicular())
        assert not a.is_perpendicular(b)
        
        e = Vec3(2, 4, 8)
        f = Vec3(2, 4, 8 - util.epsilon / 2)
        assert e.is_equal_within_epsilon(e)
        assert e.is_equal_within_epsilon(f)
        
        i = Vec3(1, 0, 0)
        j = Vec3(0, 1, 0)
        k = Vec3(0, 0, 1)
        assert i.cross(j) == k
        assert j.cross(k) == i
        assert k.cross(i) == j
        assert i.cross(k) == -j
        assert j.cross(i) == -k
        assert k.cross(j) == -i
        
        pi2 = math.pi / 2
        pi3 = math.pi / 3
        pi4 = math.pi / 4
        pi5 = math.pi / 5
        ang = math.acos(1 / math.sqrt(3))

        assert k.angle_between(k) == 0
        assert i.angle_between(j) == pi2
        assert util.within_epsilon(i.angle_between(Vec3(1, 1, 0)), pi4)

        assert Vec3.axis_angle(v100, math.pi) == v100 * math.pi
        assert Vec3.axis_angle(v111, pi3) == v111.normalize() * pi3

        assert Vec3.rotate_vec_to_vec(i, j) == v001 * pi2
        assert Vec3.is_equal_within_epsilon(Vec3.rotate_vec_to_vec(v100, v110),
                                            Vec3.axis_angle(v001, pi4))
        assert Vec3.is_equal_within_epsilon(Vec3.rotate_vec_to_vec(v111, v001),
                                            Vec3.axis_angle(Vec3(1,-1,0), ang))
        
        spi3 = math.sqrt(3) / 2                         # sin(60°), sin(pi/3)
        cpi3 = 0.5                                      # cos(60°), cos(pi/3)
        spi5 = math.sqrt((5 / 8) - (math.sqrt(5) / 8))  # sin(36°), sin(pi/5)
        cpi5 = (1 + math.sqrt(5)) / 4                   # cos(36°), cos(pi/5)

        assert Vec3.is_equal_within_epsilon(v111.rotate_xy_about_z(pi2),
                                            Vec3(1, -1, 1))
        assert Vec3.is_equal_within_epsilon(v111.rotate_xy_about_z(pi3),
                                            Vec3(cpi3 + spi3, cpi3 - spi3, 1))
        assert Vec3.is_equal_within_epsilon(v111.rotate_xy_about_z(pi5),
                                            Vec3(cpi5 + spi5, cpi5 - spi5, 1))

        assert Vec3.is_equal_within_epsilon(v111.rotate_xz_about_y(pi2),
                                            Vec3(1, 1, -1))
        assert Vec3.is_equal_within_epsilon(v111.rotate_xz_about_y(pi3),
                                            Vec3(cpi3 + spi3, 1, cpi3 - spi3))
        assert Vec3.is_equal_within_epsilon(v111.rotate_xz_about_y(pi5),
                                            Vec3(cpi5 + spi5, 1, cpi5 - spi5))

        v = Vec3(4, 5, 6)
        v += Vec3(1, 2, 3)
        assert v == Vec3(5, 7, 9), 'Vec3: test +='
        v = Vec3(5, 7, 9)
        v -= Vec3(4, 5, 6)
        assert v == Vec3(1, 2, 3), 'Vec3: test -='
        v = Vec3(1, 2, 3)
        v *= 2
        assert v == Vec3(2, 4, 6), 'Vec3: test *='
        v = Vec3(2, 4, 6)
        v /= 2
        assert v == Vec3(1, 2, 3), 'Vec3: test /='

        # assert unmodified:
        assert v000 == Vec3(0, 0, 0)
        assert v100 == Vec3(1, 0, 0)
        assert v010 == Vec3(0, 1, 0)
        assert v001 == Vec3(0, 0, 1)
        assert v011 == Vec3(0, 1, 1)
        assert v101 == Vec3(1, 0, 1)
        assert v110 == Vec3(1, 1, 0)
        assert v111 == Vec3(1, 1, 1)
        assert v123 == Vec3(1, 2, 3)
        assert v236 == Vec3(2, 3, 6)
