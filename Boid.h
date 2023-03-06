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
#include "Vec3.h"

class Boid : public Agent
{
public:
    // Constructors
    Boid() {}
    
    Vec3 wanderSteer(RandomSequence& rs)
    {
        // Brownian-like motion of point on unit radius sphere
        float rate = 0.2;
        wander_state_ += rs.randomUnitVector() * rate;
        wander_state_.normalize();
        return (wander_state_ + forward()) * (maxForce() * 0.5);
    }

private:
    Vec3 wander_state_;
};
