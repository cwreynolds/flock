#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
#
# Vec3.py -- new flock experiments
# not sure if this should be a Python class, since [x, y, z] is a perfectly fine
# representation. But if not a class it ought to be a package of utilities,
# since Open3D does not provide abstractions like this.
#
# Cartesian 3d vector space utility.
#
# MIT License -- Copyright © 2023 Craig Reynolds
#
#-------------------------------------------------------------------------------

import math

class Vec3:
    """Utility class for 3d vectors and operations on them."""
    
    # Instance constructor.
    def __init__(self, x=0, y=0, z=0):
        # This vector's 3d coordinates.
        self.x = x
        self.y = y
        self.z = z
    
    # TODO 20230402 should constructor take (x, y, z) or ([x, y, z])
    # does this work?
    @classmethod
    def from_list(cls, list):
        return Vec3(list[0], list[1], list[2])
        
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
        return (self.x * self.x) + (self.y * self.y) + (self.z * self.z)
    def normalize(self):
        return self / self.length()
        
    # Returns vector parallel to "this" but no longer than "max_length"
    def truncate(self, max_length):
        truncated = self
        magnitude = self.length()
        if magnitude > max_length:
            truncated = self * (max_length / magnitude)
        return truncated
        
    # Cross product
    def cross(a, b):
        # (From https://en.wikipedia.org/wiki/Cross_product#Matrix_notation)
        return Vec3(a.y * b.z - a.z * b.y,
                    a.z * b.x - a.x * b.z,
                    a.x * b.y - a.y * b.x)

    @staticmethod  # This decoration seems to be completely optional,
                   # but for the avoidance of doubt
    def unit_test():
        ok = True
        ok &= (str(Vec3(1, 2, 3)) == 'Vec3(1, 2, 3)')
        ok &= (Vec3(1, 2, 3) == Vec3(1, 2, 3))
        ok &= (Vec3(0, 0, 0) != Vec3(1, 0, 0))
        ok &= (Vec3(0, 0, 0) != Vec3(0, 1, 0))
        ok &= (Vec3(0, 0, 0) != Vec3(0, 0, 1))
        ok &= (Vec3(1, 2, 3).dot(Vec3(4, 5, 6)) == 32)
        ok &= (Vec3(2, 3, 6).length() == 7)
        ok &= (Vec3(2, 3, 6).normalize() == Vec3(2, 3, 6) / 7)
        ok &= (Vec3(3, 0, 0).truncate(2) == Vec3(2, 0, 0))
        ok &= (Vec3(1, 0, 0).truncate(2) == Vec3(1, 0, 0))
        ok &= (Vec3(1, 2, 3) + Vec3(4, 5, 6) == Vec3(5, 7, 9))
        ok &= (Vec3(5, 7, 9) - Vec3(4, 5, 6) == Vec3(1, 2, 3))
        ok &= (-Vec3(1, 2, 3) == Vec3(-1, -2, -3))
        ok &= (Vec3(1, 2, 3) * 2 == Vec3(2, 4, 6))
        ok &= (2 * Vec3(1, 2, 3) == Vec3(2, 4, 6))
        ok &= (Vec3(2, 4, 6) / 2 == Vec3(1, 2, 3))
        ok &= (Vec3(1, 2, 3) < Vec3(-1, -2, -4))
        
        i = Vec3(1, 0, 0)
        j = Vec3(0, 1, 0)
        k = Vec3(0, 0, 1)
        ok &= (i.cross(j) == k)
        ok &= (j.cross(k) == i)
        ok &= (k.cross(i) == j)
        ok &= (i.cross(k) == -j)
        ok &= (j.cross(i) == -k)
        ok &= (k.cross(j) == -i)

        v = Vec3(4, 5, 6)
        v += Vec3(1, 2, 3)
        ok &= (v == Vec3(5, 7, 9))
        
        v = Vec3(5, 7, 9)
        v -= Vec3(4, 5, 6)
        ok &= (v == Vec3(1, 2, 3))
        
        v = Vec3(1, 2, 3)
        v *= 2
        ok &= (v == Vec3(2, 4, 6))
        
        v = Vec3(2, 4, 6)
        v /= 2
        ok &= (v == Vec3(1, 2, 3))

        return ok



#-------------------------------------------------------------------------------
# previous c++ code for reference

# #pragma once
# #include <cmath>
# #include "Utilities.h"

#    class Vec3
#    {
#    public:
#        # Constructors
#        Vec3() {}
#        Vec3(float x, float y, float z) : x_(x), y_(y), z_(z) {}
#
#        # Accessors
#        float x() const { return x_; }
#        float y() const { return y_; }
#        float z() const { return z_; }
#
#        typedef const Vec3& V;  # just to help fit definitions below on one line.
#
#        # Vector operations dot product, length (norm), normalize.
#        float dot(V v) const { return x() * v.x() + y() * v.y() + z() * v.z(); }
#        float length() const { return std::sqrt(lengthSquared()); }
#        float lengthSquared() const { return sq(x()) + sq(y()) + sq(z()); }
#        Vec3 normalize() const { return *this / length(); }
#
#        # Basic operators + - * / == != < += *=
#        Vec3 operator+(V v) const { return {x() + v.x(), y() + v.y(), z() + v.z()};}
#        Vec3 operator-(V v) const { return {x() - v.x(), y() - v.y(), z() - v.z()};}
#        Vec3 operator-() const { return *this * -1; }
#        Vec3 operator*(float s) const { return {x() * s, y() * s, z() * s}; }
#        Vec3 operator/(float s) const { return {x() / s, y() / s, z() / s}; }
#        bool operator==(V v) const { return x()==v.x() && y()==v.y() && z()==v.z();}
#        bool operator!=(V v) const { return x()!=v.x() || y()!=v.y() || z()!=v.z();}
#        bool operator<(V v) const {return length() < v.length();}
#        Vec3 operator+=(V rhs) { return *this = *this + rhs; }
#        Vec3 operator-=(V rhs) { return *this = *this - rhs; }
#        Vec3 operator*=(float s) { return *this = *this * s; }
#        Vec3 operator/=(float s) { return *this = *this / s; }
#
#        # Cross product
#        Vec3 cross(const Vec3& b) const
#        {
#            float a1 = x();
#            float a2 = y();
#            float a3 = z();
#            float b1 = b.x();
#            float b2 = b.y();
#            float b3 = b.z();
#            # (From https:#en.wikipedia.org/wiki/Cross_product#Matrix_notation)
#            return Vec3(a2 * b3 - a3 * b2, a3 * b1 - a1 * b3, a1 * b2 - a2 * b1);
#        }
#
#        # Returns vector parallel to "this" but no longer than "max_length"
#        Vec3 truncate(float max_length) const
#        {
#            float m = length();
#            return ((m > max_length) ? (*this * (max_length / m)) : *this);
#        }
#
#        # TODO 20230221 reconsider name, etc.
#        Vec3 rotateXyAboutZ(float angle) const
#        {
#            float s = std::sin(angle);
#            float c = std::cos(angle);
#            return Vec3(x() * c + y() * s, y() * c - x() * s, z());
#        }
#
#        static bool unitTest()
#        {
#            return ((Vec3(1, 2, 3) == Vec3(1, 2, 3)) &&
#                    (Vec3(0, 0, 0) != Vec3(1, 0, 0)) &&
#                    (Vec3(0, 0, 0) != Vec3(0, 1, 0)) &&
#                    (Vec3(0, 0, 0) != Vec3(0, 0, 1)) &&
#                    (Vec3(1, 2, 3).dot(Vec3(4, 5, 6)) == 32) &&
#                    (Vec3(2, 3, 6).length() == 7) &&
#                    (Vec3(2, 3, 6).normalize() == Vec3(2, 3, 6) / 7) &&
#                    (Vec3(1, 2, 3) + Vec3(4, 5, 6) == Vec3(5, 7, 9)) &&
#                    (Vec3(5, 7, 9) - Vec3(4, 5, 6) == Vec3(1, 2, 3)) &&
#                    (-Vec3(1, 2, 3) == Vec3(-1, -2, -3)) &&
#                    (Vec3(1, 2, 3) * 2 == Vec3(2, 4, 6)) &&
#                    (Vec3(2, 4, 6) / 2 == Vec3(1, 2, 3)) &&
#                    (Vec3(1, 2, 3) < Vec3(-1, -2, -4)) &&
#                    ((Vec3(4, 5, 6) += Vec3(1, 2, 3)) == Vec3(5, 7, 9)) &&
#                    ((Vec3(5, 7, 9) -= Vec3(4, 5, 6)) == Vec3(1, 2, 3)) &&
#                    ((Vec3(1, 2, 3) *= 2) == Vec3(2, 4, 6)) &&
#                    ((Vec3(2, 4, 6) /= 2) == Vec3(1, 2, 3)) &&
#                    (Vec3(3, 0, 0).truncate(2) == Vec3(2, 0, 0)));
#        }
#    private:
#        float x_ = 0;
#        float y_ = 0;
#        float z_ = 0;
#    };
#
#
#    # Serialize Vec3 object to stream.
#    inline std::ostream& operator<<(std::ostream& os, const Vec3& v)
#    {
#        os << "(" << v.x() << ", " << v.y() <<", " << v.z() << ")";
#        return os;
#    }
#
#
#    inline Vec3 RandomSequence::randomPointInAxisAlignedBox(Vec3 a, Vec3 b)
#    {
#        return Vec3(random2(std::min(a.x(), b.x()), std::max(a.x(), b.x())),
#                    random2(std::min(a.y(), b.y()), std::max(a.y(), b.y())),
#                    random2(std::min(a.z(), b.z()), std::max(a.z(), b.z())));
#    }
#
#    #inline Vec2 RandomSequence::randomPointInAxisAlignedRectangle(Vec2 a, Vec2 b)
#    #{
#    #    return Vec2(random2(std::min(a.x(), b.x()), std::max(a.x(), b.x())),
#    #                random2(std::min(a.y(), b.y()), std::max(a.y(), b.y())));
#    #}
#
#
#    # Generate a random point inside a unit diameter disk centered on origin.
#    inline Vec3 RandomSequence::randomPointInUnitRadiusSphere()
#    {
#        Vec3 v;
#    #    float h = 0.5;
#    #    do { v = {frandom01() - h, frandom01() - h}; } while (v.length() > h);
#        do
#        {
#    #        v = {frandom2(-1, 1), frandom2(-1, 1), frandom2(-1, 1)};
#            v = randomPointInAxisAlignedBox(Vec3(-1, -1, -1), Vec3(1, 1, 1));
#        }
#        while (v.length() > 1);
#        return v;
#    }
#
#    # Generate a random unit vector.
#    inline Vec3 RandomSequence::randomUnitVector()
#    {
#        Vec3 v;
#    #    float m = v.length();
#        float m = 0;
#        do
#        {
#            v = randomPointInUnitRadiusSphere();
#            m = v.length();
#        }
#        while (m == 0);
#        return v / m;
#    }

