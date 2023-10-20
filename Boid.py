#-------------------------------------------------------------------------------
#
# Boid.py -- new flock experiments
#
# Boid class, specialization of Agent.
#
# A Flock is a collection of Boid instances. Boid.fly_with_flock() is its main
# entry point. Boids are normally created by a Flock. Each Boid is created with
# a link back to its Flock, for finding neighbors, etc.
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
from obstacle import Collision
from obstacle import EvertedSphereObstacle

class Boid(Agent):

    def __init__(self, flock=None):
        super().__init__()
        self.max_speed = 0.3     # Speed upper limit (m/s)
        self.max_force = 0.6     # Acceleration upper limit (m/s²)
        self.speed = self.max_speed * 0.6
        self.body_radius = 0.5   # "assume a spherical boid" -- unit diameter
        self.flock = flock
        self.sphere_radius = 0
        self.sphere_center = Vec3()
        # Set during sense/plan phase, saved for steer phase.
        self.next_steer = Vec3()
        # Low pass filter for steering vector.
        self.steer_memory = util.Blender()
        # Low pass filter for roll control ("up" target).
        self.up_memory = util.Blender()
        # Cache of nearest neighbors, updating "ocasionally".
        self.cached_nearest_neighbors = []
        # Seconds between neighbor refresh (Set to zero to turn off caching.)
        self.neighbor_refresh_rate = 0.5
        self.time_since_last_neighbor_refresh = 0
        # For wander_steer()
        self.wander_state = Vec3()
        # Temp? Pick a random midrange boid color.
        self.color = Vec3.from_array([util.frandom2(0.5, 0.8) for i in range(3)])
        # Tunable parameters
        # (TODO maybe these should be on the class rather than instance?)
        # (TODO Also add max_speed, max_force, and Flock.min_time_to_collide?)
        self.weight_forward  = 0.20
        self.weight_separate = 1.00
        self.weight_align    = 0.30
        self.weight_cohere   = 0.60
        self.weight_avoid    = 0.80
        self.max_dist_separate = 4
        self.max_dist_align    = 6
        self.max_dist_cohere   = 100  # TODO 20231017 should this be ∞ or
                                      # should the behavior just ignore it?
        # TODO 20231019 are these 3 useful? Or should it just assume 1/dist is
        #               used to weight all neighbors in all three behaviors?
        self.exponent_separate = 1
        self.exponent_align    = 1
        self.exponent_cohere   = 1
        ########################################################################
        # TODO 20231020 neighbor angle
        # Cosine of threshold angle (max angle from forward to be seen)
#        self.angle_separate = 0      # 90°
#        self.angle_align    = 0.707  # 45°
#        self.angle_cohere   = 0      # 90°
        self.angle_separate = -1     # 180°
        self.angle_align    = -1     # 180°
        self.angle_cohere   = -1     # 180°
        ########################################################################

    # Determine and store desired steering for this simulation step
    def plan_next_steer(self, time_step):
        self.next_steer = self.steer_to_flock(time_step)

    # Apply desired steering for this simulation step
    def apply_next_steer(self, time_step):
        self.steer(self.next_steer, time_step)

    # Basic flocking behavior. Performs one simulation step (an animation frame)
    # for one boid in a flock.
    def steer_to_flock(self, time_step):
        neighbors = self.nearest_neighbors(time_step)
        f = self.weight_forward * self.forward
        s = self.weight_separate * self.steer_to_separate(neighbors)
        a = self.weight_align * self.steer_to_align(neighbors)
        c = self.weight_cohere * self.steer_to_cohere(neighbors)
        o = self.weight_avoid * self.steer_to_avoid(time_step)
        combined_steering = self.smoothed_steering(f + s + a + c + o)
        self.annotation(s, a, c, o, combined_steering)
        return combined_steering


    ############################################################################
    # TODO 20231020 neighbor angle

    # Steering force component to move away from neighbors.
    def steer_to_separate(self, neighbors):
        direction = Vec3()
        for neighbor in neighbors:
            offset = self.position - neighbor.position
            dist = offset.length()
            weight = 1 / (dist ** self.exponent_separate)
            weight *= 1 - util.unit_sigmoid_on_01(dist / self.max_dist_separate)
            
            weight *= self.angle_weight(neighbor, self.angle_separate)
            
            direction += offset * weight
        return direction.normalize_or_0()

    # Steering force component to align path with neighbors.
    def steer_to_align(self, neighbors):
        direction = Vec3()
        for neighbor in neighbors:
            heading_offset = neighbor.forward - self.forward
            dist = (neighbor.position - self.position).length()
            weight = 1 / (dist ** self.exponent_align)
            weight *= 1 - util.unit_sigmoid_on_01(dist / self.max_dist_align)
            
            weight *= self.angle_weight(neighbor, self.angle_align)

            direction += heading_offset.normalize() * weight
        return direction.normalize_or_0()

    # Steering force component to cohere with neighbors: toward neighbor center.
    def steer_to_cohere(self, neighbors):
        direction = Vec3()
        neighbor_center = Vec3()
        total_weight = 0
        for neighbor in neighbors:
            dist = (neighbor.position - self.position).length()
            weight = 1 / (dist ** self.exponent_cohere)
            weight *= 1 - util.unit_sigmoid_on_01(dist / self.max_dist_cohere)
            
            weight *= self.angle_weight(neighbor, self.angle_cohere)

            neighbor_center += neighbor.position * weight
            total_weight += weight
        neighbor_center /= total_weight
        direction = neighbor_center - self.position
        return direction.normalize()

    ############################################################################

    # Steering force component to avoid obstacles.
    def steer_to_avoid(self, time_step):
        weight = 0
        avoidance = Vec3()
        if not self.flock.wrap_vs_avoid:
            collisions = self.predict_future_collisions()
            if collisions and time_step > 0:
                first_collision = collisions[0]
                poi = first_collision.point_of_impact
                normal = first_collision.normal_at_poi
                pure_steering = normal.perpendicular_component(self.forward)
                avoidance = pure_steering.normalize()
                min_dist = self.speed * self.flock.min_time_to_collide / time_step
                # Near enough to require avoidance steering?
                near = min_dist > first_collision.dist_to_collision
                if self.flock.avoid_blend_mode:
                    # Smooth weight transition from 80% to 120% of min dist.
                    d = util.remap_interval(first_collision.dist_to_collision,
                                            min_dist * 0.8, min_dist * 1.2, 1, 0)
                    weight = util.unit_sigmoid_on_01(d)
                else:
                    weight = 1 if near else 0
                self.avoid_obstacle_annotation(poi, near, weight)
            if weight < 0.1:
                avoidance = self.prototype_fly_away_from_obstacle()
                weight = 1
        return avoidance * weight

    # TODO 20231014 prototype_fly_away_from_obstacle
    # Prototype of non-predictive "repulsion" from "large" obstacles like walls.
    # Here the default EvertedSphereObstacle is assumed.
    def prototype_fly_away_from_obstacle(self):
        avoidance = Vec3()
        p = self.position
        r = self.flock.sphere_radius
        c = self.flock.sphere_center
        offset_to_sphere_center = c - p
        distance_to_sphere_center = offset_to_sphere_center.length()
        dist_from_wall = r - distance_to_sphere_center
        if dist_from_wall < r * 0.7:  # outer 75% of sphere
            normal = offset_to_sphere_center / distance_to_sphere_center
            if normal.dot(self.forward) < 0.9:
                weight = (distance_to_sphere_center / r) ** 3
                avoidance = normal * weight
                # Draw.add_line_segment(p, p + avoidance, Vec3(1, 1, 0))
        return avoidance

    # Draw a ray from Boid to its point of impact. Magenta for strong avoidance,
    # shades to background gray (85%) for gentle avoidance.
    def avoid_obstacle_annotation(self, poi, near, weight):
        # magenta = Vec3(0.9, 0.7, 0.9) # old color before 20230910
        magenta = Vec3(1, 0, 1)
        gray85 = Vec3(0.85, 0.85, 0.85)
        color = util.interpolate(weight, gray85, magenta)
        if weight > 0.1:
            Draw.add_line_segment(self.position, poi, color)

    # Wander aimlessly via slowly varying steering force. Currently unused.
    def steer_to_wander(self, rs):
        # Brownian-like motion of point on unit radius sphere
        rate = 0.4;
        # TODO 20230408 implement RandomSequence equivalent for determinism.
        self.wander_state += util.random_unit_vector() * rate
        self.wander_state.normalize()
        # wander_state moved 2 units forward, then normalized by 1/3, so forward
        # conponent is on [1/3, 1], then scaled by half max_force
        return ((self.wander_state + (self.forward * 2)) *
                (1 / 3) *
                (self.max_force * 0.5))

    ############################################################################
    # TODO 20231020 neighbor angle
    
    def angle_weight(self, neighbor, cos_angle_threshold):
        offset = self.position - neighbor.position
        projection = offset.normalize().dot(self.forward)
        within_angle =  projection > self.angle_separate
#        return 1 if within_angle else 0
        return 1 if within_angle else 0.01

    ############################################################################

    # Returns a list of the N Boids nearest this one.
    # (n=3 increased frame rate from ~30 to ~50 fps. No other obvious changes.)
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
    # (TODO 20231012 no longer used, could be removed.)
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

    # Ad hoc low-pass filtering of steering force. Blends this step's newly
    # determined "raw" steering into a per-boid accumulator, then returns that
    # smoothed value to use for actually steering the boid this simulation step.
    def smoothed_steering(self, steer):
        return self.steer_memory.blend(steer, 0.6) # Ad hoc smoothness param.

    # Draw this Boid's “body” -- currently an irregular tetrahedron.
    def draw(self):
        center = self.position
        nose = center + self.forward * self.body_radius
        tail = center - self.forward * self.body_radius
        bd = self.body_radius * 2  # body diameter (defaults to 1)
        apex = tail + self.up * 0.25 * bd + self.forward * 0.1 * bd
        wingtip0 = tail + self.side * 0.3 * bd
        wingtip1 = tail - self.side * 0.3 * bd
        # Draw the 4 triangles of a boid's body.
        def draw_tri(a, b, c, color):
            Draw.add_colored_triangle(a, b, c, color)
        draw_tri(nose, apex,     wingtip1, self.color * 1.00)
        draw_tri(nose, wingtip0, apex,     self.color * 0.95)
        draw_tri(apex, wingtip0, wingtip1, self.color * 0.90)
        draw_tri(nose, wingtip1, wingtip0, self.color * 0.70)

    # Draw optional annotation of this Boid's current steering forces
    def annotation(self, separation, alignment, cohesion, avoidance, combined):
        center = self.position
        def relative_force_annotation(offset, color):
            Draw.add_line_segment(center, center + offset, color)
        if (self.flock.enable_annotation and self.flock.tracking_camera and
                   (self.flock.selected_boid().position - center).length() < 3):
            relative_force_annotation(separation, Vec3(1, 0, 0))
            relative_force_annotation(alignment,  Vec3(0, 1, 0))
            relative_force_annotation(cohesion,   Vec3(0, 0, 1))
            relative_force_annotation(avoidance,  Vec3(1, 0, 1))
            relative_force_annotation(combined,   Vec3(0.5, 0.5, 0.5))

    # Bird-like roll control: blends vector toward path curvature center with
    # global up. Overrides method in base class Agent
    def up_reference(self, acceleration):
        new_up = acceleration + Vec3(0, 0.01, 0)  # slight bias toward global up
        self.up_memory.blend(new_up, 0.999)
        self.up_memory.value = self.up_memory.value.normalize()
        return self.up_memory.value

    # Returns a list of future collisions sorted by time, with soonest first.
    def predict_future_collisions(self):
        collisions = []
        for obstacle in self.flock.obstacles:
            point_of_impact = obstacle.ray_intersection(self.position, self.forward)
            #
            # TODO 20230903 Quite occasionally, this seems to return None.
            #               Need to figure out why.
            #
            if point_of_impact:
                dist_to_collision = (point_of_impact - self.position).length()
                time_to_collision = dist_to_collision / self.speed
                normal_at_poi = obstacle.normal_at_poi(point_of_impact)
                collisions.append(Collision(time_to_collision,
                                            dist_to_collision,
                                            point_of_impact,
                                            normal_at_poi))
        return sorted(collisions, key=lambda x: x.time_to_collision)
