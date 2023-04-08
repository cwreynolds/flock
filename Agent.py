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

################################################################################
# TODO move to a new Utilities.py

# Constrain a given value "x" to be between two bounds: "bound0" and "bound1"
# (without regard to order). Returns x if it is between the bounds, otherwise
# returns the nearer bound.
def clip(x, bound0, bound1):
    clipped = x
    minimum = min(bound0, bound1)
    maximum = max(bound0, bound1)
    if clipped < minimum:
        clipped = minimum
    if clipped > maximum:
        clipped = maximum
    return clipped
################################################################################


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
    def get_velocity(self): return self.forward() * self.speed

    # Advance Agent state forward by time_step while applying steering_force.
    def steer(self, steering_force, time_step):
        assert isinstance(steering_force, Vec3), "steering_force must be Vec3."
        # Limit steering force by max force (simulates power or thrust limit).
        limit_steering_force = steering_force.truncate(self.max_force)
        # Adjust force by mass to get acceleration.
        acceleration = limit_steering_force / self.mass
        # Update dynamic and gerometric state...
        self.updateSpeedAndLocalSpace(acceleration * time_step);

    def updateSpeedAndLocalSpace(self, acceleration):
        new_velocity = self.get_velocity() + acceleration
        new_speed = new_velocity.length()
        
        # TODO 20230407 what if new_speed is zero?
        #               maybe this should be inside speed>0 block?
        self.speed = clip(new_speed, 0, self.max_speed)
        new_forward = new_velocity / new_speed;

        if (self.speed > 0):
            new_side = new_forward.cross(self.up()).normalize()
            new_up = new_side.cross(new_forward).normalize()
            new_position = self.position() + (new_forward * self.speed)

            # TODO assert perpendicular...
            # ...

            # Set new geometric state.
            # TODO should these be setters or like in c++ ls().setIJKP()
            self.ls.x = new_side
            self.ls.y = new_up
            self.ls.z = new_forward
            self.ls.p = new_position

    @staticmethod  # This decoration seems to be completely optional,
                   # but for the avoidance of doubt
    def unit_test():
        a = Agent()
        force = Vec3(0.1, 0.1, 1)
        time_step = 1 / 60
        a.steer(force, time_step)
        a.steer(force, time_step)
        a.steer(force, time_step)
        ref_position = Vec3(0.005, 0.005, 0.10041450153584738)
    
        ok = True
        ref_ls = LocalSpace()
        ok &= (Agent().side()     == ref_ls.i)
        ok &= (Agent().up()       == ref_ls.j)
        ok &= (Agent().forward()  == ref_ls.k)
        ok &= (Agent().position() == ref_ls.p)
        ok &= (Agent().get_velocity() == Vec3())
        ok &= (a.position() == ref_position)
        return ok
