#-------------------------------------------------------------------------------
#
# Boid.py -- new flock experiments
#
# Boid class, specialization of Agent.
#
# Each boid in a flock is an instance of this class. The flock is represented as
# a class level attribute, the list Boid.flock. This class also contains several
# static methods related to the flock, such as Boid.draw_flock(). It might make
# sense for "flock" to be its own class. Certainly so if we ever need more than
# one.
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
        Boid.flock = flock # used for comunication by global GUI
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

    # Basic flocking behavior.
    # TODO 20230427 Hmmm this steer_to_...() function has no return value but
    # does have side effect. Whereas the other steer_to_...() functions DO have
    # return values and no side effect. Maybe it should be called something else
    # like fly() or fly_with_flock() ?
    def steer_to_flock(self, time_step):
        neighbors = self.nearest_neighbors(time_step)
        f = self.forward * 0.1
        s = 0.8 * self.steer_to_separate(neighbors)
        a = 0.5 * self.steer_to_align(neighbors)
        c = 0.6 * self.steer_to_cohere(neighbors)
        combined_steering = f + s + a + c

        # TODO 20230512 WIP
        # Steer to avoid collision with spherical containment (boids inside sphere).
        if not Boid.wrap_vs_avoid:
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
        distance = (self.flock.selected_boid().position - self.position).length()
        if (Boid.enable_annotation and Boid.tracking_camera and distance < 3):
            def relative_force_annotation(offset, color):
                Draw.add_line_segment(center, center + offset, color)
            relative_force_annotation(self.last_separation_force, Vec3(1, 0, 0))
            relative_force_annotation(self.last_alignment_force, Vec3(0, 1, 0))
            relative_force_annotation(self.last_cohesion_force, Vec3(0, 0, 1))
            relative_force_annotation(self.last_combined_steering,
                                      Vec3(0.5, 0.5, 0.5))

    # Register single key commands with the Open3D visualizer GUI.
    @staticmethod
    def register_single_key_commands():
        Draw.vis.register_key_callback(ord('S'), Boid.select_next_boid)
        Draw.vis.register_key_callback(ord('A'), Boid.toggle_annotation)
        Draw.vis.register_key_callback(ord('C'), Boid.toggle_tracking_camera)
        Draw.vis.register_key_callback(ord('W'), Boid.toggle_wrap_vs_avoid)
        Draw.vis.register_key_callback(ord('E'), Boid.toggle_dynamic_erase)
        Draw.vis.register_key_callback(ord('H'), Boid.print_help)

    # Select the "next" boid. This gets bound to the "s" key in the interactive
    # visualizer (hence the ignored "vis" arg). So typing s s s can be used to
    # cycle through the boids of a flock.
    @staticmethod
    def select_next_boid(vis = None):
        Boid.flock.select_next_boid()

    # Global animation switch.
    enable_annotation = True

    # Toggle global animation switch.
    @staticmethod
    def toggle_annotation(vis = None):
        Boid.enable_annotation = not Boid.enable_annotation
    
    # Global tracking camera mode.
    tracking_camera = False

    # Toggle global tracking camera mode.
    @staticmethod
    def toggle_tracking_camera(vis = None):
        Boid.tracking_camera = not Boid.tracking_camera

    # Global mode for sphere-wrap-around (True) versus sphere-avoidance (false).
    wrap_vs_avoid = False

    # Toggle mode for sphere-wrap-around versus sphere-avoidance.
    @staticmethod
    def toggle_wrap_vs_avoid(vis = None):
        Boid.wrap_vs_avoid = not Boid.wrap_vs_avoid

    # Toggle mode for erasing dynamic graphics.
    @staticmethod
    def toggle_dynamic_erase(vis = None):
        Draw.clear_dynamic_mesh = not Draw.clear_dynamic_mesh
        if Boid.tracking_camera and not Draw.clear_dynamic_mesh:
            print('!!! "spacetime boid worms" do not work correctly with ' +
                  'boid tracking camera mode ("C" key). Awaiting fix for ' +
                  'Open3D bug 6009.')

    # Print mini-help on shell.
    @staticmethod
    def print_help(vis = None):
        print()
        print('  flock single key commands:')
        print('    space: toggle simulation run/pause')
        print('    1:     single simulation step, then pause')
        print('    c:     toggle camera between static and boid tracking')
        print('    s:     select next boid for camera tracking')
        print('    a:     toggle drawing of steering annotation')
        print('    w:     toggle between sphere wrap-around or avoidance')
        print('    e:     toggle erase mode (spacetime boid worms)')
        print('    h:     print this message')
        print('    esc:   exit simulation.')
        print()
        print('  mouse view controls:')
        print('    Left button + drag         : Rotate.')
        print('    Ctrl + left button + drag  : Translate.')
        print('    Wheel button + drag        : Translate.')
        print('    Shift + left button + drag : Roll.')
        print('    Wheel                      : Zoom in/out.')
        print()
        print('  annotation (in camera tracking mode, “c” to toggle):')
        print('    red:     separation force.')
        print('    green:   alignment force.')
        print('    blue:    cohesion force.')
        print('    gray:    combined steering force.')
        print('    magenta: ray for obstacle avoidance.')
        print()

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
                if Boid.enable_annotation:
                    c = Vec3(0.9, 0.5, 0.9) # magenta
                    Draw.add_line_segment(self.position, path_intersection, c)
        return avoidance
