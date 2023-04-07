#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
#
# Agent.py -- new flock experiments
#
# A steerable agent base class.
#
# MIT License -- Copyright © 2023 Craig Reynolds
#
#-------------------------------------------------------------------------------

import math
from Vec3 import Vec3
from LocalSpace import LocalSpace

class Agent:
    """A steerable agent base class."""

    # Initialize new instance.
    def __init__(self):
        self.ls = LocalSpace()    # Local coordinate space (pos, orient).
        self.mass = 1             # Mass, normally ignored as 1.
        self.speed = 0            # Current forward speed (m/s).
        self.max_speed = 10       # Speed upper limit (m/s)
        self.max_force = 3        # Acceleration upper limit (m/s²)

    # Agent-specific names for components of local space
    def side(self):     return self.ls.i
    def up(self):       return self.ls.j
    def forward(self):  return self.ls.k
    def position(self): return self.ls.p

    # Current velocity vector
    def getVelocity(self): return self.forward() * self.speed


    @staticmethod  # This decoration seems to be completely optional,
                   # but for the avoidance of doubt
    def unit_test():
        ok = True
        ref_ls = LocalSpace()
        ok &= (Agent().side()     == ref_ls.i)
        ok &= (Agent().up()       == ref_ls.j)
        ok &= (Agent().forward()  == ref_ls.k)
        ok &= (Agent().position() == ref_ls.p)
        ok &= (Agent().getVelocity() == Vec3())
        return ok



#    class Agent
#    {
#    public:
#
#
#        // Advance Agent state forward by time_step while applying steering_force.
#        void steer(Vec3 steering_force, float time_step)
#        {
#            // Limit steering force by max force (simulates power or thrust limit).
#            Vec3 limit_steering_force = steering_force.truncate(maxForce());
#            // Adjust force by mass to get acceleration.
#            Vec3 acceleration = limit_steering_force / mass();
#            // Update dynamic and gerometric state...
#            updateSpeedAndLocalSpace(acceleration * time_step);
#        }
#        
#        // TODO need time_step or pre multiply?
#        void updateSpeedAndLocalSpace(Vec3 acceleration)
#        {
#            Vec3 new_velocity = getVelocity() + acceleration;
#            float new_speed = new_velocity.length();
#            setSpeed(clip(new_speed, 0, maxSpeed()));
#            Vec3 new_forward = new_velocity / new_speed;
#            
#            if (getSpeed() > 0)
#            {
#    //            Vec3 new_side = new_forward.cross(up());
#    //            Vec3 new_up = new_side.cross(new_forward);
#                Vec3 new_side = new_forward.cross(up()).normalize();
#                Vec3 new_up = new_side.cross(new_forward).normalize();
#
#                Vec3 new_position = position() + (new_forward * getSpeed());
#
#    //            assert(new_side.length() == 1);
#    //            assert(new_up.length() == 1);
#    //            assert(new_forward.length() == 1);
#                
#                // TODO assert perpendicular...
#                // ...
#
#                // Set new geometric state.
#                ls().setIJKP(new_side, new_up, new_forward, new_position);
#            }
#        }
#        
#    };













################################################################################


#    //------------------------------------------------------------------------------
#    //
#    // Agent.h -- new flock experiments
#    //
#    // A steerable agent base class.
#    //
#    // MIT License -- Copyright © 2023 Craig Reynolds
#    //
#    //------------------------------------------------------------------------------
#
#    #pragma once
#    #include "Vec3.h"
#    #include "LocalSpace.h"
#
#    class Agent
#    {
#    public:
#        // Constructors
#        Agent() {}
#        
#        // Accessors
#        LocalSpace& ls() { return ls_; }
#        const LocalSpace& ls() const { return ls_; }
#        Vec3 side() const { return ls().i(); }
#        Vec3 up() const { return ls().j(); }
#        Vec3 forward() const { return ls().k(); }
#        Vec3 position() const { return ls().p(); }
#        float mass() const { return mass_; }
#        float getSpeed() const { return speed_; }
#        float maxSpeed() { return max_speed_; }
#        float maxForce() { return max_force_; }
#        
#        void setSpeed(float new_speed) { speed_ = new_speed; }
#        void setMaxSpeed(float max_speed) { max_speed_ = max_speed; }
#        void setMaxForce(float max_force) { max_force_ = max_force; }
#        
#        Vec3 getVelocity() const { return forward() * getSpeed(); }
#
#        // Advance Agent state forward by time_step while applying steering_force.
#        void steer(Vec3 steering_force, float time_step)
#        {
#            // Limit steering force by max force (simulates power or thrust limit).
#            Vec3 limit_steering_force = steering_force.truncate(maxForce());
#            // Adjust force by mass to get acceleration.
#            Vec3 acceleration = limit_steering_force / mass();
#            // Update dynamic and gerometric state...
#            updateSpeedAndLocalSpace(acceleration * time_step);
#        }
#        
#        // TODO need time_step or pre multiply?
#        void updateSpeedAndLocalSpace(Vec3 acceleration)
#        {
#            Vec3 new_velocity = getVelocity() + acceleration;
#            float new_speed = new_velocity.length();
#            setSpeed(clip(new_speed, 0, maxSpeed()));
#            Vec3 new_forward = new_velocity / new_speed;
#            
#            if (getSpeed() > 0)
#            {
#    //            Vec3 new_side = new_forward.cross(up());
#    //            Vec3 new_up = new_side.cross(new_forward);
#                Vec3 new_side = new_forward.cross(up()).normalize();
#                Vec3 new_up = new_side.cross(new_forward).normalize();
#
#                Vec3 new_position = position() + (new_forward * getSpeed());
#
#    //            assert(new_side.length() == 1);
#    //            assert(new_up.length() == 1);
#    //            assert(new_forward.length() == 1);
#                
#                // TODO assert perpendicular...
#                // ...
#
#                // Set new geometric state.
#                ls().setIJKP(new_side, new_up, new_forward, new_position);
#            }
#        }
#        
#    private:
#        LocalSpace ls_;               // Local coordinate space (pos, orient).
#        float mass_ = 1;              // Mass, normally ignored as 1.
#        float speed_ = 0;             // Current forward speed (m/s).
#        float max_speed_ = 10;        // Speed upper limit (m/s)
#        float max_force_ = 3;         // Acceleration upper limit (m/s²)
#    };
