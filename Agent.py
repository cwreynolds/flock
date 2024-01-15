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
        #                Note that average bird flying speed is ~10-16 m/s
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

    ############################################################################
    # TODO 20240113 Matthew's bug report
    
#    # Advance Agent state forward by time_step while applying steering_force.
#    # (TODO the use of Vec3.truncate() below (like util.clip() in update_...())
#    # is likely a problem for automatic differentiation. Perhaps we need another
#    # way to accomplish that, like say velocity dependent wind resistance?)
#    def steer(self, steering_force, time_step):
#        assert isinstance(steering_force, Vec3), "steering_force must be Vec3."
#        # Limit steering force by max force (simulates power or thrust limit).
#        limit_steering_force = steering_force.truncate(self.max_force)
#        # Adjust force by mass to get acceleration.
#        acceleration = limit_steering_force / self.mass
#        # Update dynamic and gerometric state...
#        self.update_speed_and_local_space(acceleration * time_step);

#    # Applies given acceleration to Agent's dynamic and geometric state.
#    def update_speed_and_local_space(self, acceleration):
#        new_velocity = self.velocity + acceleration
#        new_speed = new_velocity.length()
#        
#        # TODO 20230407 what if new_speed is zero?
#        #               maybe this should be inside speed>0 block?
#        self.speed = util.clip(new_speed, 0, self.max_speed)
#        new_forward = new_velocity / new_speed;
#        
#        # Update geometric state when moving.
#        if (self.speed > 0):
#            # Reorthonormalize to correspond to new_forward
#            ref_up = self.up_reference(acceleration)
#            new_side = ref_up.cross(new_forward).normalize()
#            new_up = new_forward.cross(new_side).normalize()
#            new_position = self.position + (new_forward * self.speed)
#            # Set new geometric state.
#            new_ls = LocalSpace(new_side, new_up, new_forward, new_position)
#            if new_ls.is_orthonormal():
#                self.ls = new_ls
#            else:
#                print('Ignore bad ls in Agent.update_speed_and_local_space')

    # Advance Agent state forward by time_step while applying steering_force.
    # (TODO the use of Vec3.truncate() below (like util.clip() in update_...())
    # is likely a problem for automatic differentiation. Perhaps we need another
    # way to accomplish that, like say velocity dependent wind resistance?)
    def steer(self, steering_force, time_step):
        assert isinstance(steering_force, Vec3), "steering_force must be Vec3."
        # Limit steering force by max force (simulates power or thrust limit).
        limit_steering_force = steering_force.truncate(self.max_force)
        # Adjust force by mass to get acceleration.
        acceleration = limit_steering_force / self.mass
#        # Update dynamic and gerometric state...
#        self.update_speed_and_local_space(acceleration * time_step);
        # Update dynamic and geometric state...
        self.update_speed_and_local_space(acceleration, time_step);

    # Applies given acceleration to Agent's dynamic and geometric state.

#    def update_speed_and_local_space(self, acceleration):
#        new_velocity = self.velocity + acceleration

    def update_speed_and_local_space(self, acceleration, time_step):
        new_velocity = self.velocity + (acceleration * time_step)
        new_speed = new_velocity.length()
        
        # TODO 20230407 what if new_speed is zero?
        #               maybe this should be inside speed>0 block?
        self.speed = util.clip(new_speed, 0, self.max_speed)
        new_forward = new_velocity / new_speed;
        
        # Update geometric state when moving.
        if (self.speed > 0):
            # Reorthonormalize to correspond to new_forward
            
#            ref_up = self.up_reference(acceleration)
            ref_up = self.up_reference(acceleration * time_step) # TODO arg ignored
            
            new_side = ref_up.cross(new_forward).normalize()
            new_up = new_forward.cross(new_side).normalize()
            
#            new_position = self.position + (new_forward * self.speed)
#            new_position = self.position + (new_forward * self.speed * time_step)
            # TODO Matthew's version:
            clipped_velocity = new_forward * self.speed
            new_position = self.position + clipped_velocity * time_step
             
            # Set new geometric state.
            new_ls = LocalSpace(new_side, new_up, new_forward, new_position)
            if new_ls.is_orthonormal():
                self.ls = new_ls
            else:
                print('Ignore bad ls in Agent.update_speed_and_local_space')

    ############################################################################

    # Very basic roll control: use global UP as reference up
    def up_reference(self, acceleration):
        return Vec3(0, 1, 0)

    # Given an arbitrary steering force, return the component purely lateral
    # (perpendicular) to our forward basis. This is the part that steers/turns
    # our heading but leaves speed unchanged.
    def pure_lateral_steering(self, raw_steering):
        return raw_steering.perpendicular_component(self.forward)

    def __str__(self):
        return self.name + ': speed=' + str(self.speed) + str(self.ls)

    def __eq__(self, other):
        if isinstance(other, Agent):
            return self.name == other.name
        else:
            return NotImplemented

    @staticmethod
    def unit_test():
        a = Agent()
        force = Vec3(0.1, 0.1, 1)
        time_step = 1 / 60
        ref_ls = LocalSpace()
        ref_position = Vec3(0.007426106572325057,
                            0.007426106572325057,
                            0.07426106572325057)
        assert a.side     == ref_ls.i, 'check initial side basis'
        assert a.up       == ref_ls.j, 'check initial up basis'
        assert a.forward  == ref_ls.k, 'check initial forward basis'
        assert a.position == ref_ls.p, 'check initial position'
        assert a.velocity == Vec3(),   'check initial velocity'
        for i in range(5):
            a.steer(force, time_step)
            #print(a.position())

        ########################################################################
        # TODO 20240113 Matthew's bug report
#        assert a.position == ref_position, 'position after 5 steer() calls'
        ########################################################################
