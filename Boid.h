//------------------------------------------------------------------------------
//
// Boid.h -- new flock experiments
//
// Boid class, specialization of Agent.
//
// MIT License -- Copyright © 2023 Craig Reynolds
//
//------------------------------------------------------------------------------

#pragma once
#include "Agent.h"

class Boid : public Agent
{
public:
    // Constructors
    Boid() {}
    //    Boid(Vec3 i, Vec3 j, Vec3 k, Vec3 p) : i_(i), j_(j), k_(k), p_(p) {}
    
    // Accessors
    //    Vec3 i() const { return i_; }
    //    Vec3 j() const { return j_; }
    //    Vec3 k() const { return k_; }
    //    Vec3 p() const { return p_; }
    
private:
//    LocalSpace ls;
};

//    // Serialize Boid object to stream.
//    inline std::ostream& operator<<(std::ostream& os, const Boid& ls)
//    {
//        os << "[i=" << ls.i();
//        os << ", j=" << ls.j();
//        os << ", k=" << ls.k();
//        os << ", p=" << ls.p();
//        os << "]";
//        return os;
//    }

