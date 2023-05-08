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
from statistics import mean
import math
import itertools
import numpy as np  # temp?

class Boid(Agent):
    def __init__(self):
        super().__init__()
        self.max_speed = 0.3      # Speed upper limit (m/s)
        self.max_force = 0.1      # Acceleration upper limit (m/s²)
        self.max_force = 0.3      # Acceleration upper limit (m/s²)
        # Temp? Use nonzero initial speed.
        self.speed = self.max_speed * 0.25
        # Remember steering components for annotation.
        self.last_separation_force = Vec3()
        self.last_alignment_force = Vec3()
        self.last_coherance_force = Vec3()
        self.last_combined_steering = Vec3()
        # Temp? Pick a random midrange boid color.
        self.color = Vec3.from_array([util.frandom2(0.5, 0.8) for i in range(3)])
        # For wander_steer()
        self.wander_state = Vec3()

    # Basic flocking behavior.
    # TODO 20230427 Hmmm this steer_to_...() function has no return value but
    # does have side effect. Whereas the other steer_to_...() functions DO have
    # return values and no side effect.
    def steer_to_flock(self, time_step):
#        return 0
        neighbors = self.nearest_neighbors()
        f = self.forward * 0.05
        s = self.steer_to_separate(neighbors)
        a = self.steer_to_align(neighbors)
        c = self.steer_to_cohere(neighbors)
        combined_steering = f + (s * 10) + (a * 0.5) + (c * 0.2)
        self.last_separation_force = s
        self.last_alignment_force = a
        self.last_coherance_force = c
        self.last_combined_steering = combined_steering
        self.steer(combined_steering, time_step)

    # Steering force component to move away from neighbors.
    def steer_to_separate(self, neighbors):
        ########################################################################
        # TODO 20230420 just for debugging
        neighbors = self.nearest_neighbors(7, 5)
        ########################################################################
        steer = Vec3()
        if len(neighbors) > 0:
            direction = Vec3()
            for neighbor in neighbors:
                offset = neighbor.position - self.position
                dist = offset.length()
                if dist > 0:
                    weight = 1 / (dist ** 2)
                    direction += (offset / (dist * weight))
            perp = direction.perpendicular_component(self.forward)
            steer = perp.normalize()
        return steer

    # Steering force component to align path with neighbors.
    def steer_to_align(self, neighbors):
        direction = Vec3()
        if len(neighbors) > 0:
            for neighbor in neighbors:
                heading_offset = neighbor.forward - self.forward
                if heading_offset.length_squared() > 0:
                    dist = (neighbor.position - self.position).length()
                    weight = 1 / (dist ** 2) # TODO ?
                    direction += heading_offset.normalize() * weight
            # Return "pure" steering component: perpendicular to forward.
            if direction.length_squared() > 0:
                direction = direction.perpendicular_component(self.forward)
                direction = direction.normalize()
        return direction

    # Steering force component to cohere with neighbors: toward neighbor center.
    def steer_to_cohere(self, neighbors):
        direction = Vec3()
        if len(neighbors) > 0:
            neighbor_center  = Vec3()
            total_weight = 0
            for neighbor in neighbors:
                dist = (neighbor.position - self.position).length()
                weight = 1 / (dist ** 2)
                neighbor_center += neighbor.position * weight
                total_weight += weight
            neighbor_center /= total_weight
            direction = neighbor_center - self.position
            # "Pure" steering component: perpendicular to forward.
            direction = direction.normalize()
            direction = direction.perpendicular_component(self.forward)
        return direction

    # TODO 20230408 implement RandomSequence equvilent
    def wander_steer(self, rs):
        # Brownian-like motion of point on unit radius sphere
        rate = 0.4;
        # self.wander_state += rs.randomUnitVector() * rate
        self.wander_state += util.random_unit_vector() * rate
        self.wander_state.normalize()
        # wander_state moved 2 units forward, then normalized by 1/3, so forward
        # conponent is on [1/3, 1], then scaled by half max_force
        return ((self.wander_state + (self.forward * 2)) *
                (1 / 3) *
                (self.max_force * 0.5))

    # Returns a list of the N Boids nearest this one.
    # Optionally filters by max_distance. N defaults to 7, ala STARFLAG.
    def nearest_neighbors(self, n=7, max_distance=math.inf):
        def distance_from_me(boid):
            return (boid.position - self.position).length()
        def near_enough(boid):
            return ((max_distance == math.inf) or
                    ((boid.position - self.position).length() < max_distance))
        neighbors = list(filter(near_enough, Boid.flock))
        neighbors.sort(key=distance_from_me)
        n_neighbors = neighbors[1:n+1]
        return n_neighbors

    # Draw this Boid's “body” -- currently an irregular tetrahedron.
    def draw(self):
        center = self.position - Boid.camera_aim_boid_draw_offset_qqq()
        nose = center + self.forward * 0.5
        tail = center - self.forward * 0.5
        apex = tail + self.up * 0.25 + self.forward * 0.1
        wingtip0 = tail + self.side * 0.3
        wingtip1 = tail - self.side * 0.3
        # Draw the 4 triangles of a boid's body.
        def draw_tri(a, b, c, color):
            Draw.add_triangle_single_color(a, b, c, color)
        draw_tri(nose, apex,     wingtip1, self.color * 1.00)
        draw_tri(nose, wingtip0, apex,     self.color * 0.95)
        draw_tri(apex, wingtip0, wingtip1, self.color * 0.90)
        draw_tri(nose, wingtip1, wingtip0, self.color * 0.70)
        # Annotation for steering forces
        if center.length() < 3:
            def relative_force_annotation(offset, color):
                Draw.add_line_segment(center, center + offset, color)
            relative_force_annotation(self.last_separation_force, Vec3(1, 0, 0))
            relative_force_annotation(self.last_alignment_force, Vec3(0, 1, 0))
            relative_force_annotation(self.last_coherance_force, Vec3(0, 0, 1))
            gray80 = Vec3(0.8, 0.8, 0.8)
            relative_force_annotation(self.last_combined_steering, gray80)

    # TODO 20230418 since at the moment I cannot animate the camera, this is a
    # stop gap where we offset all boid drawing by the position of "some boid"
    @staticmethod
    def camera_aim_boid_draw_offset_qqq():
        return Boid.flock[0].position
#        return Vec3()

    # Make a new Boid, add it to flock. Defaults to one Boid at origin. Can add
    # "count" Boids, randomly placed within a sphere with "radius" and "center".
    @staticmethod
    def add_boid_to_flock(count=1, radius=0, center=Vec3()):
        for i in range(count):
            boid = Boid()
            random_point = Vec3.random_point_in_unit_radius_sphere()
            
            # TODO 20230418 for testing, probably too much randomness for real.
            boid.ls.randomize_orientation()
            
            boid.ls.p = center + (radius * random_point)
            Boid.flock.append(boid)

    # Apply steer_to_flock() to each boid in flock.
    @staticmethod
    def steer_flock(time_step):
        for boid in Boid.flock:
            boid.steer_to_flock(time_step)

    # Draw each boid in flock.
    @staticmethod
    def draw_flock():
        for boid in Boid.flock:
            boid.draw()

    # When a Boid gets more than "radius" from the original, teleport it to the
    # other side of the world, its antipodal point.
    @staticmethod
    def sphere_wrap_around_flock(radius):
        for boid in Boid.flock:
            bp = boid.position
            distance_from_origin = bp.length()
            if distance_from_origin > radius:
                new_position = (-bp).normalize() * radius * 0.95
                boid.ls.p = new_position

    # Calculate and log various statistics for flock.
    @staticmethod
    def log_stats_for_flock():
        if Draw.frame_counter % 100 == 0 and not Draw.simulation_paused:
            average_speed = mean([b.speed for b in Boid.flock])
            # Loop over all unique pairs of distinct boids: ab==ba, not aa
            min_sep = math.inf
            ave_sep = 0
            pair_count = 0
            # Via https://stackoverflow.com/a/942551/1991373
            for (p, q) in itertools.combinations(Boid.flock, 2):
                dist = (p.position - q.position).length()
                if min_sep > dist:
                    min_sep = dist
                ave_sep += dist
                pair_count += 1
            ave_sep /= pair_count
            #
            max_nn_dist = 0
            for b in Boid.flock:
                n = b.nearest_neighbors(1)[0]
                dist = (b.position - n.position).length()
                if max_nn_dist < dist:
                    max_nn_dist = dist
            print(str(Draw.frame_counter) +
                  ' fps=' + str(int(1 / Draw.frame_duration)) +
                  ', ave_speed=' + str(average_speed)[0:5] +
                  ', min_sep=' + str(min_sep)[0:5] +
                  ', ave_sep=' + str(ave_sep)[0:5] +
                  ', max_nn_dist=' + str(max_nn_dist)[0:5])

    # List of Boids in a flock
    # TODO 20230409 assumes there is only one flock. If more are
    #               ever needed there should be a Flock class.
    flock = []
