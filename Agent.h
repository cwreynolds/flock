//------------------------------------------------------------------------------
//
// Agent.h -- new flock experiments
//
// A steerable agent base class.
//
// MIT License -- Copyright © 2023 Craig Reynolds
//
//------------------------------------------------------------------------------

#pragma once
#include "Vec3.h"
#include "LocalSpace.h"

class Agent
{
public:
    // Constructors
    Agent() {}
    
    // Accessors
    float maxSpeed() { return max_speed_; }
    float maxForce() { return max_force_; }
    void setMaxSpeed(float max_speed) { max_speed_ = max_speed; }
    void setMaxForce(float max_force) { max_force_ = max_force; }

    // TODO 20230222 should this take a time step?
    void steer(Vec3 steering_force, float time_step)
    {
        
    }
    
private:
    LocalSpace ls;
    float max_speed_ = 10;   // in, say, meters per second?
    float max_force_ = 0.2;  // in, say, meters per second²?

};
