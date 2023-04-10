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

# experiment
from Draw import Draw


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

    def draw(self):
        center = self.position()
        nose = self.forward() * +0.5
        tail = self.forward() * -0.5
        wingtip0 = tail + (self.side() * +0.3)
        wingtip1 = tail + (self.side() * -0.3)
        color = Vec3(util.frandom2(0.4, 0.6),
                     util.frandom2(0.4, 0.6),
                     util.frandom2(0.4, 0.6))
#        Draw.add_triangle_single_color(center + nose,
#                                       center + wingtip0,
#                                       center + wingtip0,
#                                       color)
        Draw.add_triangle_single_color(center + nose,
                                       center + wingtip0,
                                       center + wingtip1,
                                       color)

    # Make a new Boid, add it to flock. Defaults to one Boid at origin. Can add
    # "count" Boids, randomly placed within a sphere with "radius" and "center".
    @staticmethod
    def add_boid_to_flock(count=1, radius=0, center=Vec3()):
        for i in range(count):
            boid = Boid()
            random_point = util.random_point_in_unit_radius_sphere()
            boid.ls.p = center + (radius * random_point)
            
            # TEMP for first triangle test
            for k in range(10):
                boid.wander_steer(None)
            
            Boid.flock.append(boid)
            boid.draw()


    # List of Boids in a flock
    # TODO 20230409 assumes there is only one flock. If more are
    #               ever needed there should be a Flock class.
    flock = []


