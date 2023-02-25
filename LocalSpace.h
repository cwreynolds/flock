//------------------------------------------------------------------------------
//
// LocalSpace.h -- new flock experiments
//
// Local space () for a boid/agent.
// Essentially a 4x4 homogeneous transformation with [0 0 0 1] as last column.
//
// MIT License -- Copyright © 2023 Craig Reynolds
//
//------------------------------------------------------------------------------

#pragma once
//#include <cmath>
#include "Vec3.h"

class LocalSpace
{
public:
    // Constructors
    LocalSpace() {}
    LocalSpace(Vec3 i, Vec3 j, Vec3 k, Vec3 p) : i_(i), j_(j), k_(k), p_(p) {}

    // Accessors
    Vec3 i() const { return i_; }
    Vec3 j() const { return j_; }
    Vec3 k() const { return k_; }
    Vec3 p() const { return p_; }
    
    // Setters
    void setI(Vec3 i) { i_ = i; }
    void setJ(Vec3 j) { j_ = j; }
    void setK(Vec3 k) { k_ = k; }
    void setP(Vec3 p) { p_ = p; }
    void setIJKP(Vec3 i, Vec3 j, Vec3 k, Vec3 p) { i_=i; j_=j; k_=k; p_=p; }

private:
    // Basis vectors of local coordinate axes, ijk → xyz:
    Vec3 i_ = Vec3(1, 0, 0);
    Vec3 j_ = Vec3(0, 1, 0);
    Vec3 k_ = Vec3(0, 0, 1);
    // Position of local center:
    Vec3 p_ = Vec3(0, 0, 0);
};

// Serialize LocalSpace object to stream.
inline std::ostream& operator<<(std::ostream& os, const LocalSpace& ls)
{
    os << "[i=" << ls.i();
    os << ", j=" << ls.j();
    os << ", k=" << ls.k();
    os << ", p=" << ls.p();
    os << "]";
    return os;
}
