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
import Utilities as util
from Vec3 import Vec3
from LocalSpace import LocalSpace

class Agent:
    """A steerable agent base class."""

    # Initialize new instance.
    def __init__(self):
        self.ls = LocalSpace()    # Local coordinate space (pos, orient).
        self.mass = 1             # Mass, normally ignored as 1.
        self.speed = 0            # Current forward speed (m/s).
        # TODO 20230411 no idea if these values are plausible for these units
        #                I mean they are meter-long birds?!
        #                Note that average bird flying sdpeed is ~10-16 m/s
        self.max_speed = 1.0      # Speed upper limit (m/s)
        self.max_force = 0.3      # Acceleration upper limit (m/s²)
        #
        self.name = (self.__class__.__name__.lower() +
                     '_' + str(Agent.serial_number))
        Agent.serial_number += 1

    # Instance counter for default names.
    serial_number = 0

    # Define setters/getters for side, up, forward, and position.
    @property
    def side(self):
        return self.ls.i
    @side.setter
    def side(self, new_forward):
        self.ls.i = new_forward
    @property
    def up(self):
        return self.ls.j
    @up.setter
    def up(self, new_up):
        self.ls.j = new_up
    @property
    def forward(self):
        return self.ls.k
    @forward.setter
    def forward(self, new_forward):
        self.ls.k = new_forward
    @property
    def position(self):
        return self.ls.p
    @position.setter
    def position(self, new_position):
        self.ls.p = new_position

    # Get current velocity vector.
    @property
    def velocity(self):
        return self.forward * self.speed

    # Advance Agent state forward by time_step while applying steering_force.
    def steer(self, steering_force, time_step):
        assert isinstance(steering_force, Vec3), "steering_force must be Vec3."
        # Limit steering force by max force (simulates power or thrust limit).
        limit_steering_force = steering_force.truncate(self.max_force)
        # Adjust force by mass to get acceleration.
        acceleration = limit_steering_force / self.mass
        # Update dynamic and gerometric state...
        self.update_speed_and_local_space(acceleration * time_step);

    def update_speed_and_local_space(self, acceleration):
        new_velocity = self.velocity + acceleration
        new_speed = new_velocity.length()
        
        # TODO 20230407 what if new_speed is zero?
        #               maybe this should be inside speed>0 block?
        self.speed = util.clip(new_speed, 0, self.max_speed)
        new_forward = new_velocity / new_speed;
        
        # Update  geometric state when moving.
        if (self.speed > 0):
            # Reorthonormalize to corrospond to new_forward
            new_side = self.up.cross(new_forward).normalize()
            new_up = new_forward.cross(new_side).normalize()
            new_position = self.position + (new_forward * self.speed)
            # Set new geometric state.
            self.ls.set_state_ijkp(new_side, new_up, new_forward, new_position)
            # Assert that the LocalSpace is rigid, unscaled, and orthogonal
            assert self.ls.is_orthonormal()

    def __str__(self):
        return self.name + ': speed=' + str(self.speed) + str(self.ls)

    @staticmethod  # This decoration seems to be completely optional,
                   # but for the avoidance of doubt
    def unit_test():
        ok = True
        a = Agent()
        force = Vec3(0.1, 0.1, 1)
        time_step = 1 / 60
        ref_ls = LocalSpace()
        ref_position = Vec3(0.007426106572325057,
                            0.007426106572325057,
                            0.07426106572325057)
        ok &= (a.side     == ref_ls.i)
        ok &= (a.up       == ref_ls.j)
        ok &= (a.forward  == ref_ls.k)
        ok &= (a.position   == ref_ls.p)
        ok &= (a.velocity == Vec3())
        for i in range(5):
            a.steer(force, time_step)
            #print(a.position())
        ok &= (a.position == ref_position)
        return ok