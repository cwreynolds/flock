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
    const LocalSpace& ls() const { return ls_; }
    Vec3 side() const { return ls().i(); }
    Vec3 up() const { return ls().j(); }
    Vec3 forward() const { return ls().k(); }
    float mass() const { return mass_; }
    float speed() const { return speed_; }
    float maxSpeed() { return max_speed_; }
    float maxForce() { return max_force_; }
    
    void setSpeed(float new_speed) { speed_ = new_speed; }
    void setMaxSpeed(float max_speed) { max_speed_ = max_speed; }
    void setMaxForce(float max_force) { max_force_ = max_force; }
    
    Vec3 getVelocity() const { return forward() * speed(); }
//    Vec3 setVelocity const { return forward() * speed(); }

    // Advance Agent state forward by time_step while applying steering_force.
    void steer(Vec3 steering_force, float time_step)
    {
        // Limit steering force by max force (simulates power or thrust limit).
        Vec3 limit_steering_force = steering_force.truncate(maxForce());
        // Adjust force by mass to get acceleration.
        Vec3 acceleration = limit_steering_force / mass();
        // Update dynamic and gerometric state...
        updateSpeedAndLocalSpace(acceleration * time_step);
    }
    
    void updateSpeedAndLocalSpace(Vec3 acceleration)
    {
        //        // Increment velocity by steering force.
        //        setVelocity(getVelocity() + acceleration);
        
        Vec3 new_velocity = getVelocity() + acceleration;
        float new_speed = new_velocity.length();
        float clipped_speed = clip(new_speed, 0, maxSpeed());
        Vec3 new_forward = new_velocity / new_speed;

        if (clipped_speed > 0)
        {
            // TODO 20230223 -- DO MAGIC
        }
    }
    
    
private:
    LocalSpace ls_;          // Agent's Local cordinate space (rotate translate).
    float mass_ = 1;
    float speed_ = 0;
    float max_speed_ = 10;   // in, say, meters per second?
    float max_force_ = 0.2;  // in, say, meters per second per second?

};
