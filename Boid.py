#-------------------------------------------------------------------------------
#
# Boid.py -- new flock experiments
#
# Boid class, specialization of Agent.
#
# MIT License -- Copyright © 2023 Craig Reynolds
#
#-------------------------------------------------------------------------------

from Vec3 import Vec3
from Agent import Agent
import Utilities as util


class Boid(Agent):
    def __init__(self):
        super().__init__()
        self.wander_state = Vec3()

    # TODO 20230408 implement RandomSequence equvilent
    def wander_steer(self, rs):
        # Brownian-like motion of point on unit radius sphere
        rate = 0.2;
#        self.wander_state += rs.randomUnitVector() * rate
        self.wander_state += util.random_unit_vector() * rate
        self.wander_state.normalize()
        return (self.wander_state + self.forward()) * (self.max_force * 0.5)
