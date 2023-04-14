#-------------------------------------------------------------------------------
#
# Boid.py -- new flock experiments
#
# Boid class, specialization of Agent.
#
# MIT License -- Copyright © 2023 Craig Reynolds
#
#-------------------------------------------------------------------------------

from Agent import Agent
from Draw import Draw
from Vec3 import Vec3
import Utilities as util

class Boid(Agent):
    def __init__(self):
        super().__init__()
        self.wander_state = Vec3()

#        def steer_to_flock(self, time_step):
#            # TODO 20230410 very temp
#    #        self.steer(self.wander_steer(None), time_step)
#    #        self.steer(self.wander_steer(None) * 0.1, time_step)
#            self.steer(self.wander_steer(None) * 0.01, time_step)

#        def steer_to_flock(self, time_step):
#            neighbors = self.nearest_neighbors()
#            # TODO 20230410 very temp
#    #        self.steer(self.wander_steer(None) * 0.01, time_step)
#    #        self.steer(self.wander_steer(None), time_step)
#    #        self.steer(self.forward(), time_step)
#            self.steer(self.forward(), time_step)

#        def steer_to_flock(self, time_step):
#            neighbors = self.nearest_neighbors()
#    #        combined_steering = (self.forward() * 0.1 +
#    #                             self.steer_to_separate(neighbors))
#            combined_steering = (self.forward() * 0.01 +
#                                 self.steer_to_separate(neighbors).perpendicular_component(self.forward()))
#    #        print('combined_steering =', combined_steering)
#            self.steer(combined_steering, time_step)

    def steer_to_flock(self, time_step):
        neighbors = self.nearest_neighbors()
#        combined_steering = (self.forward() * 0.1 +
#                             self.steer_to_separate(neighbors))

#        f = self.forward() * 0.01
        f = self.forward * 0.01
        s = self.steer_to_separate(neighbors)
#        s = s.perpendicular_component(self.forward())
        s = s.perpendicular_component(self.forward)
        combined_steering = f + s
#        print('combined_steering =', combined_steering)
        self.steer(combined_steering, time_step)




    def steer_to_separate(self, neighbors):
        direction = Vec3()
        for neighbor in neighbors:
#            offset = self.position() - neighbor.position()
            offset = self.position - neighbor.position
            direction += offset.normalize()
        direction = direction.normalize()
        # print('direction =', direction)
        return direction










    # TODO 20230408 implement RandomSequence equvilent
    def wander_steer(self, rs):
        # Brownian-like motion of point on unit radius sphere
#        rate = 0.2;
        rate = 0.4;
        # self.wander_state += rs.randomUnitVector() * rate
        self.wander_state += util.random_unit_vector() * rate
        self.wander_state.normalize()
#        return (self.wander_state + self.forward()) * (self.max_force * 0.5)
#        return (self.wander_state + self.forward() * 1.5) * (self.max_force * 0.5)

        # wander_state moved 2 units forward, then normalized by 1/3, so forward
        # conponent is on [1/3, 1], then scaled by half max_force
#        return ((self.wander_state + (self.forward() * 2)) *
        return ((self.wander_state + (self.forward * 2)) *
                (1 / 3) *
                (self.max_force * 0.5))

    # Returns a list of the N(=7) Boids nearest this one.
    def nearest_neighbors(self, n=7):
        def distance_from_me(b):
#            return (b.position() - self.position()).length()
            return (b.position - self.position).length()
        neighbors = Boid.flock.copy()
        neighbors.sort(key=distance_from_me)
        n_neighbors = neighbors[1:n+1]
#        d = []
#        for b in n_neighbors:
#            d.append(distance_from_me(b))
#        print(d)
        return n_neighbors

    # Draw this Boid's “body” -- currently an irregular tetrahedron.
    def draw(self):
#        center = self.position()
        center = self.position
#        nose = self.forward() * +0.5
#        tail = self.forward() * -0.5
#        top = self.up() * 0.25 + self.forward() * 0.1
        nose = self.forward * +0.5
        tail = self.forward * -0.5
        top = self.up * 0.25 + self.forward * 0.1
#        wingtip0 = tail + (self.side() * +0.3)
#        wingtip1 = tail + (self.side() * -0.3)
        wingtip0 = tail + (self.side * +0.3)
        wingtip1 = tail + (self.side * -0.3)
        color = Vec3(util.frandom2(0.6, 0.8),
                     util.frandom2(0.6, 0.8),
                     util.frandom2(0.6, 0.8))
        Draw.add_triangle_single_color(center + nose,       # bottom
                                       center + wingtip1,
                                       center + wingtip0,
                                       color * 0.7)
        Draw.add_triangle_single_color(center + nose,       # left
                                       center + wingtip0,
                                       center + tail + top,
                                       color * 0.95)
        Draw.add_triangle_single_color(center + nose,       # right
                                       center + tail + top,
                                       center + wingtip1,
                                       color)
        Draw.add_triangle_single_color(center + tail + top, # back
                                       center + wingtip0,
                                       center + wingtip1,
                                       color * 0.9)

    # Make a new Boid, add it to flock. Defaults to one Boid at origin. Can add
    # "count" Boids, randomly placed within a sphere with "radius" and "center".
    @staticmethod
    def add_boid_to_flock(count=1, radius=0, center=Vec3()):
        for i in range(count):
            boid = Boid()
            random_point = util.random_point_in_unit_radius_sphere()
            boid.ls.p = center + (radius * random_point)
            
#            # TEMP for first triangle test
#            for k in range(10):
#                boid.wander_steer(None)
            
            Boid.flock.append(boid)
#            boid.draw()

    @staticmethod
    def steer_flock(time_step):
        for boid in Boid.flock:
            boid.steer_to_flock(time_step)

    @staticmethod
    def draw_flock():
        for boid in Boid.flock:
            boid.draw()

    @staticmethod
    # When a Boid gets more than "radius" from the original, teleport it to the
    # other side of the world, its antipodal point.
    def sphere_wrap_around_flock(radius):
        for boid in Boid.flock:
#            bp = boid.position()
            bp = boid.position
            distance_from_origin = bp.length()
            if distance_from_origin > radius:
                new_position = (-bp).normalize() * radius * 0.95
                boid.ls.p = new_position
                

    # List of Boids in a flock
    # TODO 20230409 assumes there is only one flock. If more are
    #               ever needed there should be a Flock class.
    flock = []


