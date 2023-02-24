//------------------------------------------------------------------------------
//
// Vec3.h -- new flock experiments
//
// Cartesian 3d vector space utility.
//
// MIT License -- Copyright © 2023 Craig Reynolds
//
//------------------------------------------------------------------------------


#pragma once
#include <cmath>
#include "Utilities.h"

class Vec3
{
public:
    // Constructors
    Vec3() {}
    Vec3(float x, float y, float z) : x_(x), y_(y), z_(z) {}
    
    // Accessors
    float x() const { return x_; }
    float y() const { return y_; }
    float z() const { return z_; }

    typedef const Vec3& V;  // just to help fit definitions below on one line.

    // Vector operations dot product, length (norm), normalize.
    float dot(V v) const { return x() * v.x() + y() * v.y() + z() * v.z(); }
    float length() const { return std::sqrt(lengthSquared()); }
    float lengthSquared() const { return sq(x()) + sq(y()) + sq(z()); }
    Vec3 normalize() const { return *this / length(); }
    
    // Basic operators + - * / == != < += *=
    Vec3 operator+(V v) const { return {x() + v.x(), y() + v.y(), z() + v.z()};}
    Vec3 operator-(V v) const { return {x() - v.x(), y() - v.y(), z() - v.z()};}
    Vec3 operator-() const { return *this * -1; }
    Vec3 operator*(float s) const { return {x() * s, y() * s, z() * s}; }
    Vec3 operator/(float s) const { return {x() / s, y() / s, z() / s}; }
    bool operator==(V v) const { return x()==v.x() && y()==v.y() && z()==v.z();}
    bool operator!=(V v) const { return x()!=v.x() || y()!=v.y() || z()!=v.z();}
    bool operator<(V v) const {return length() < v.length();}
    Vec3 operator+=(V rhs) { return *this = *this + rhs; }
    Vec3 operator-=(V rhs) { return *this = *this - rhs; }
    Vec3 operator*=(float s) { return *this = *this * s; }
    Vec3 operator/=(float s) { return *this = *this / s; }
    
    // Returns vector parallel to "this" but no longer than "max_length"
    Vec3 truncate(float max_length) const
    {
        float m = length();
        return ((m > max_length) ? (*this * (max_length / m)) : *this);
    }

    // TODO 20230221 reconsider name, etc.
    Vec3 rotateXyAboutZ(float angle) const
    {
        float s = std::sin(angle);
        float c = std::cos(angle);
        return Vec3(x() * c + y() * s, y() * c - x() * s, z());
    }
    
    static bool unitTest()
    {
        return ((Vec3(1, 2, 3) == Vec3(1, 2, 3)) &&
                (Vec3(0, 0, 0) != Vec3(1, 0, 0)) &&
                (Vec3(0, 0, 0) != Vec3(0, 1, 0)) &&
                (Vec3(0, 0, 0) != Vec3(0, 0, 1)) &&
                (Vec3(1, 2, 3).dot(Vec3(4, 5, 6)) == 32) &&
                (Vec3(2, 3, 6).length() == 7) &&
                (Vec3(2, 3, 6).normalize() == Vec3(2, 3, 6) / 7) &&
                (Vec3(1, 2, 3) + Vec3(4, 5, 6) == Vec3(5, 7, 9)) &&
                (Vec3(5, 7, 9) - Vec3(4, 5, 6) == Vec3(1, 2, 3)) &&
                (-Vec3(1, 2, 3) == Vec3(-1, -2, -3)) &&
                (Vec3(1, 2, 3) * 2 == Vec3(2, 4, 6)) &&
                (Vec3(2, 4, 6) / 2 == Vec3(1, 2, 3)) &&
                (Vec3(1, 2, 3) < Vec3(-1, -2, -4)) &&
                ((Vec3(4, 5, 6) += Vec3(1, 2, 3)) == Vec3(5, 7, 9)) &&
                ((Vec3(5, 7, 9) -= Vec3(4, 5, 6)) == Vec3(1, 2, 3)) &&
                ((Vec3(1, 2, 3) *= 2) == Vec3(2, 4, 6)) &&
                ((Vec3(2, 4, 6) /= 2) == Vec3(1, 2, 3)) &&
                (Vec3(3, 0, 0).truncate(2) == Vec3(2, 0, 0)));
    }
private:
    float x_ = 0;
    float y_ = 0;
    float z_ = 0;
};


// Serialize Vec3 object to stream.
inline std::ostream& operator<<(std::ostream& os, const Vec3& v)
{
    os << "(" << v.x() << ", " << v.y() <<", " << v.z() << ")";
    return os;
}


//~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

// Small vectors with integer coordinates and lengths:

//    int max = 51;
//    for (int k = 1; k < max; k++)
//    {
//        for (int j = 1; j < max; j++)
//        {
//            for (int i = 1; i < max; i++)
//            {
//                Vec3 v(i, j, k);
//                float m = v.length();
//                if (m == int(m) && i != j && j != k && k != i)
//                {
//                    std::cout << "v = " << v << ", m = " << m << std::endl;;
//                }
//            }
//        }
//    }

//~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~



//    //
//    //  Vec2.h
//    //  texsyn
//    //
//    //  Created by Craig Reynolds on 12/19/19.
//    //  Copyright © 2019 Craig Reynolds. All rights reserved.
//    //
//
//    #pragma once
//    #include "Utilities.h"
//
//    class Vec2
//    {
//    public:
//        // Constructors
//        Vec2() {}
//        // Modified to count and report, but otherwise tolerate, "abnormal" floats.
//        Vec2(float x, float y) : x_(paper_over_abnormal_values(x)),
//        y_(paper_over_abnormal_values(y)) {}
//        // Accessors
//        float x() const { return x_; }
//        float y() const { return y_; }
//        // Vector operations dot product, length (norm), normalize.
//        float dot(const Vec2& v) const {return x() * v.x() + y() * v.y(); }
//        float length() const { return std::sqrt(sq(x()) + sq(y())); }
//        float lengthSquared() const { return sq(x()) + sq(y()); }
//        Vec2 normalize() const { return *this / length(); }
//        // Basic operators + - * / == != < += *=
//        Vec2 operator+(Vec2 v) const { return { x() + v.x(), y() + v.y() }; }
//        Vec2 operator-(Vec2 v) const { return { x() - v.x(), y() - v.y() }; }
//        Vec2 operator-() const { return *this * -1; }
//        Vec2 operator*(float s) const { return { x() * s, y() * s}; }
//        Vec2 operator/(float s) const { return { x() / s, y() / s}; }
//        bool operator==(const Vec2 v) const { return x() == v.x() && y() == v.y(); }
//        bool operator!=(const Vec2 v) const { return x() != v.x() || y() != v.y(); }
//        bool operator<(const Vec2 v) const {return length() < v.length();}
//        Vec2 operator+=(const Vec2& rhs) { return *this = *this + rhs; }
//        Vec2 operator-=(const Vec2& rhs) { return *this = *this - rhs; }
//        Vec2 operator*=(float s) { return *this = *this * s; }
//        Vec2 operator/=(float s) { return *this = *this / s; }
//        // Rotation about origin by angle in radians (or by precomputed sin/cos).
//        Vec2 rotate(float a) const { return rotate(std::sin(a), std::cos(a)); }
//        inline Vec2 rotate(float sin, float cos) const
//        { return Vec2(x() * cos + y() * sin, y() * cos - x() * sin); }
//        // 90° (π/2) rotation
//        Vec2 rotate90degCW() const { return Vec2(y(), -x()); }
//        Vec2 rotate90degCCW() const { return Vec2(-y(), x()); }
//        // Compute a 32 bit hash value for a Vec2.
//        size_t hash() { return hash_mashup(hash_float(x_), hash_float(y_)); }
//        // Angle of this vector with +Y axis.
//        float atan2() const { return std::atan2(x(), y()); }
//    private:
//        float x_ = 0;
//        float y_ = 0;
//    };
//
//    // Generate a random point inside a unit diameter disk centered on origin.
//    inline Vec2 RandomSequence::randomPointInUnitDiameterCircle()
//    {
//        Vec2 v;
//        float h = 0.5;
//        do { v = {frandom01() - h, frandom01() - h}; } while (v.length() > h);
//        return v;
//    }
//
//    // Generate a random unit vector.
//    inline Vec2 RandomSequence::randomUnitVector()
//    {
//        Vec2 v;
//        do { v = randomPointInUnitDiameterCircle(); } while (v.length() == 0);
//        return v.normalize();
//    }
//
//    inline Vec2 RandomSequence::randomPointInAxisAlignedRectangle(Vec2 a, Vec2 b)
//    {
//        return Vec2(random2(std::min(a.x(), b.x()), std::max(a.x(), b.x())),
//                    random2(std::min(a.y(), b.y()), std::max(a.y(), b.y())));
//    }
//
//    // Is distance between vectors no more than epsilon?
//    inline bool withinEpsilon(Vec2 a, Vec2 b, float epsilon)
//    {
//        return (a - b).length() <= epsilon;
//    }
//
//    // Serialize Vec2 object to stream.
//    inline std::ostream& operator<<(std::ostream& os, const Vec2& v)
//    {
//        os << "(" << v.x() << ", " << v.y() << ")";
//        return os;
//    }
//
