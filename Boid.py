#-------------------------------------------------------------------------------
#
# Boid.py -- new flock experiments
#
# Boid class, specialization of Agent.
#
# A Flock is a collection of Boid instances. Boid.fly_with_flock() is its main
# method. Boids are nromally created by a Flock. Each boid is given a link back
# to its Flock, for finding neighbors, etc.
#
# MIT License -- Copyright © 2023 Craig Reynolds
#
#-------------------------------------------------------------------------------

from Agent import Agent
from Draw import Draw
from Vec3 import Vec3
import Utilities as util
import copy
import math

class Boid(Agent):

    def __init__(self, flock=None):
        super().__init__()
        self.max_speed = 0.3     # Speed upper limit (m/s)
        self.max_force = 0.6     # Acceleration upper limit (m/s²)
        self.speed = self.max_speed * 0.6
        self.flock = flock
        self.sphere_radius = 0
        self.sphere_center = Vec3()
        # Remember steering components for annotation.
        self.last_separation_force = Vec3()
        self.last_alignment_force = Vec3()
        self.last_cohesion_force = Vec3()
        self.last_combined_steering = Vec3()
        # For wander_steer()
        self.wander_state = Vec3()
        # Low pass filter for steering vector.
        self.smoothed_steering_state = Vec3()
        # Cache of nearest neighbors, updating "ocasionally".
        self.cached_nearest_neighbors = []
        self.neighbor_refresh_rate = 0.5  # seconds between neighbor refresh
        self.time_since_last_neighbor_refresh = 0
        # Temp? Pick a random midrange boid color.
        self.color = Vec3.from_array([util.frandom2(0.5, 0.8) for i in range(3)])

    # Basic flocking behavior. Performs one simulation step (an animation frame)
    # for one boid in a flock.
    def fly_with_flock(self, time_step):
        neighbors = self.nearest_neighbors(time_step)
        f = self.forward * 0.1
        s = 0.8 * self.steer_to_separate(neighbors)
        a = 0.5 * self.steer_to_align(neighbors)
        c = 0.6 * self.steer_to_cohere(neighbors)
        combined_steering = f + s + a + c

        # TODO 20230512 WIP
        # Steer to avoid collision with spherical containment (boids inside sphere).
        if not self.flock.wrap_vs_avoid:
            avoidance = Vec3()
            if time_step > 0:
                min_time_to_collide = 1.5 # seconds
                min_distance = self.speed * min_time_to_collide / time_step
                avoidance = self.sphere_avoidance(min_distance,
                                                  self.sphere_radius,
                                                  self.sphere_center)
            # Very ad hoc (also bad for differentiation)
            if avoidance != Vec3():
                c = Vec3()
                combined_steering = f + s + a + avoidance

        combined_steering = self.smoothed_steering(combined_steering)
        self.last_separation_force = s
        self.last_alignment_force = a
        self.last_cohesion_force = c
        self.last_combined_steering = combined_steering
        self.steer(combined_steering, time_step)
        
    # Steering force component to move away from neighbors.
    def steer_to_separate(self, neighbors):
        # TODO experimental, ignore neighbors more than 3 units away.
        neighbors = self.filter_boids_by_distance(3, neighbors)
        steer = Vec3()
        if len(neighbors) > 0:
            direction = Vec3()
            for neighbor in neighbors:
                offset = self.position - neighbor.position
                dist = offset.length()
                if dist > 0:
                    weight = 1 / (dist ** 2)
                    direction += (offset / (dist * weight))
            steer = direction.normalize()
        return steer

    # Steering force component to align path with neighbors.
    def steer_to_align(self, neighbors):
        # TODO experimental, ignore neighbors more than 10 units away.
        neighbors = self.filter_boids_by_distance(10, neighbors)
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
    def nearest_neighbors(self, time_step, n=7):
        self.time_since_last_neighbor_refresh += time_step
        if self.time_since_last_neighbor_refresh > self.neighbor_refresh_rate:
            self.recompute_nearest_neighbors(n)
        return self.cached_nearest_neighbors

    # Recomputes a list of the N Boids nearest this one.
    def recompute_nearest_neighbors(self, n=7):
        def distance_squared_from_me(boid):
            return (boid.position - self.position).length_squared()
        neighbors = sorted(self.flock.boids, key=distance_squared_from_me)
        self.cached_nearest_neighbors = neighbors[1:n+1]
        self.time_since_last_neighbor_refresh = 0

    # Filter collection of boids by distance.
    def filter_boids_by_distance(self, max_distance, boids=None):
        result = []
        if boids == None:
            boids = self.flock.boids
        if max_distance == math.inf:
            result = copy.copy(boids)
        else:
            mdsq = max_distance ** 2
            def near_enough(boid):
                dist = (boid.position - self.position).length_squared()
                return dist < mdsq
            result = list(filter(near_enough, boids))
        return result

    # Ad hoc low-pass filtering of steering force. Blends this step's raw
    # steering into a per-boid accumulator, then returns that smoothed value
    # to use for steering the boid this simulation step.
    def smoothed_steering(self, raw_steering):
        # TODO completely ad hoc smoothing "rate".
        s = util.interpolate(0.8, raw_steering, self.smoothed_steering_state)
        self.smoothed_steering_state = s
        return s

    # Draw this Boid's “body” -- currently an irregular tetrahedron.
    def draw(self):
        center = self.position
        nose = center + self.forward * 0.5
        tail = center - self.forward * 0.5
        apex = tail + self.up * 0.25 + self.forward * 0.1
        wingtip0 = tail + self.side * 0.3
        wingtip1 = tail - self.side * 0.3
        # Draw the 4 triangles of a boid's body.
        def draw_tri(a, b, c, color):
            Draw.add_colored_triangle(a, b, c, color)
        draw_tri(nose, apex,     wingtip1, self.color * 1.00)
        draw_tri(nose, wingtip0, apex,     self.color * 0.95)
        draw_tri(apex, wingtip0, wingtip1, self.color * 0.90)
        draw_tri(nose, wingtip1, wingtip0, self.color * 0.70)
        # Annotation for steering forces
        annote = (self.flock.enable_annotation and
                  self.flock.tracking_camera and
                  (self.flock.selected_boid().position - center).length() < 3)
        if annote:
            def relative_force_annotation(offset, color):
                Draw.add_line_segment(center, center + offset, color)
            relative_force_annotation(self.last_separation_force, Vec3(1, 0, 0))
            relative_force_annotation(self.last_alignment_force, Vec3(0, 1, 0))
            relative_force_annotation(self.last_cohesion_force, Vec3(0, 0, 1))
            relative_force_annotation(self.last_combined_steering,
                                      Vec3(0.5, 0.5, 0.5))

    # Steer to avoid collision with spherical containment (assumes boids are
    # inside sphere). Eventually it would be nice to provide avoidance for
    # arbitrary triangle meshes via ray tracing (eg see
    # https://github.com/isl-org/Open3D/issues/6149#issuecomment-1549407410)
    def sphere_avoidance(self, min_dist, radius, center):
        avoidance = Vec3()
        path_intersection = Vec3.ray_sphere_intersection(self.position,
                                                         self.forward,
                                                         radius, center)
        if path_intersection:
            # Too far away to care?
            dist_squared = (path_intersection - self.position).length_squared()
            if dist_squared < min_dist ** 2:
                toward_center = center - path_intersection
                pure_steering = toward_center.perpendicular_component(self.forward)
                avoidance = pure_steering.normalize()
                if self.flock.enable_annotation:
                    c = Vec3(0.9, 0.5, 0.9) # magenta
                    Draw.add_line_segment(self.position, path_intersection, c)
        return avoidance
