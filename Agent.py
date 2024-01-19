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
        # Update dynamic and geometric state...
        self.update_speed_and_local_space(acceleration, time_step);

    # Applies given acceleration to Agent's dynamic and geometric state.
    def update_speed_and_local_space(self, acceleration, time_step):
        new_velocity = self.velocity + (acceleration * time_step)
        new_speed = new_velocity.length()
        self.speed = util.clip(new_speed, 0, self.max_speed)
        # Update geometric state when moving.
        if (self.speed > 0):
            new_forward = new_velocity / new_speed;
            # Reorthonormalize to correspond to new_forward
            ref_up = self.up_reference(acceleration * time_step)
            new_side = ref_up.cross(new_forward).normalize()
            new_up = new_forward.cross(new_side).normalize()
            clipped_velocity = new_forward * self.speed
            new_position = self.position + clipped_velocity * time_step
            # Set new geometric state.
            self.ls.set_state_ijkp(new_side, new_up, new_forward, new_position)
            assert self.ls.is_orthonormal()

    # Very basic roll control: use global UP as reference up
    def up_reference(self, acceleration):
        return Vec3(0, 1, 0)

    # Given an arbitrary steering force, return the component purely lateral
    # (perpendicular) to our forward basis. This is the part that steers/turns
    # our heading but leaves speed unchanged.
    def pure_lateral_steering(self, raw_steering):
        return raw_steering.perpendicular_component(self.forward)

    # Makes three lightweight verifications of basic Agent "flying." One is
    # "from first principles" and tests for agreement between a closed form
    # discrete Newtonian model of motion under constant acceleration. Two other
    # more generalized 3d motions are tested for continuing to produce the same
    # results recorded earlier in the source code.
    @staticmethod
    def unit_test():
        # Use default Agent at its identity transform initial state. Accelerate
        # it straight forward along the z axis and verify it behaves as Newton
        # says it should.
        # Classic case: https://en.wikipedia.org/wiki/Newton%27s_laws_of_motion
        # Discrete case: https://math.stackexchange.com/a/2880227/516283
        agent0 = Agent()
        agent0.max_speed = 1000  # Disable speed ceiling for this sub-test.
        n = 100
        scalar_acceleration = 0.1
        z_acceleration = Vec3(0, 0, scalar_acceleration)
        predict_pos = Vec3(0, 0, ((n * (n + 1)) / 2) * scalar_acceleration)
        # Accelerate 0.1 m/s² in z direction for n steps of 1 second long.
        for i in range(n):
            agent0.steer(z_acceleration, 1)
        # Assert the Agent's position is where we predicted it should be.
        e = util.epsilon * 1000;  # ~1e-12
        assert Vec3.is_equal_within_epsilon(agent0.position, predict_pos, e)

        # Simple "historical repeatability" test. Verify that Agent's final
        # position matches a precomputed reference frozen in the source.
        agent1 = Agent()
        force = Vec3(0.1, 0.1, 1)
        time_step = 1 / 60
        ref_ls = LocalSpace()
        ref_position = Vec3(0.00012376844287208429,  # recorded 20240117
                            0.00012376844287208429,
                            0.0012376844287208429)
        assert agent1.side     == ref_ls.i, 'check initial side basis'
        assert agent1.up       == ref_ls.j, 'check initial up basis'
        assert agent1.forward  == ref_ls.k, 'check initial forward basis'
        assert agent1.position == ref_ls.p, 'check initial position'
        assert agent1.velocity == Vec3(),   'check initial velocity'
        for i in range(5):
            agent1.steer(force, time_step)
            #print(agent1.position)
        assert agent1.position == ref_position, 'position after 5 steer() calls'

        # TODO 20230119 I do not trust the test below. It gets a significantly
        #               different result than on the c++ side
        
#        # Slightly more complicated "historical repeatability" test. Steering
#        # force is expressed in Agent's local space then transformed into
#        # global space.
#        agent2 = Agent()
#        local_force = Vec3(0.1, 0.5, 1)
#        for i in range(5):
#            agent2.steer(force, time_step)
#            global_force = agent2.ls.globalize(local_force)
#            agent2.steer(global_force, time_step)
#            # print(agent2.position)
#        ref_position2 = Vec3(0.000157790528647075, # recorded 20240117
#                             0.000921239641353907,
#                             0.00071099761041107)
#        print('(agent2.position - ref_position2).length() =', (agent2.position - ref_position2).length())
#        assert Vec3.is_equal_within_epsilon(agent2.position, ref_position2, e)
