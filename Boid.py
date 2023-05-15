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
import copy

class Boid(Agent):
    def __init__(self):
        super().__init__()
        self.max_speed = 0.3      # Speed upper limit (m/s)
        self.max_force = 0.3      # Acceleration upper limit (m/s²)
        # Temp? Use nonzero initial speed.
        self.speed = self.max_speed * 0.25
        # Remember steering components for annotation.
        self.last_separation_force = Vec3()
        self.last_alignment_force = Vec3()
        self.last_cohesion_force = Vec3()
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
        neighbors = self.nearest_neighbors()
        f = self.forward * 0.05
        
        s = 0.8 * self.steer_to_separate(neighbors)
        a = 0.5 * self.steer_to_align(neighbors)
        c = 0.6 * self.steer_to_cohere(neighbors)

        combined_steering = f + s + a + c

        ########################################################################
        # TODO 20230512 WIP
        # Steer to avoid collision with spherical containment (boids inside sphere).
        if not Boid.wrap_vs_avoid:
            min_distance = self.max_speed * 40
            avoidance = self.sphere_avoidance(min_distance)
            if avoidance != Vec3():
#                a = Vec3()
#                c = Vec3()
#                combined_steering = f + s + avoidance
                c = Vec3()
                combined_steering = f + s + a + avoidance
        ########################################################################

        self.last_separation_force = s
        self.last_alignment_force = a
        self.last_cohesion_force = c
        self.last_combined_steering = combined_steering
        self.steer(combined_steering, time_step)

    # Steering force component to move away from neighbors.
    def steer_to_separate(self, neighbors):
        ########################################################################
        # TODO 20230420 just for debugging
        neighbors = self.filter_boids_by_distance(3, neighbors)
        ########################################################################
        steer = Vec3()
        if len(neighbors) > 0:
            direction = Vec3()
            for neighbor in neighbors:
                offset = self.position - neighbor.position
                dist = offset.length()
                if dist > 0:
                    weight = 1 / (dist ** 2)
                    direction += (offset / (dist * weight))
            ####################################################################
            # TODO 20230515 reconsider "pure lateral steering"
#            perp = direction.perpendicular_component(self.forward)
            perp = direction
            ####################################################################
            steer = perp.normalize()
        return steer

    # Steering force component to align path with neighbors.
    def steer_to_align(self, neighbors):
        ########################################################################
        # TODO 20230509 just for debugging
        neighbors = self.filter_boids_by_distance(10, neighbors)
        ########################################################################
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
                ################################################################
                # TODO 20230515 reconsider "pure lateral steering"
#                direction = direction.perpendicular_component(self.forward)
                ################################################################
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
            ####################################################################
            # TODO 20230515 reconsider "pure lateral steering"
#            direction = direction.perpendicular_component(self.forward)
            ####################################################################
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
    def nearest_neighbors(self, n=7):
        def distance_squared_from_me(boid):
            return (boid.position - self.position).length_squared()
        neighbors = sorted(Boid.flock, key=distance_squared_from_me)
        n_neighbors = neighbors[1:n+1]
        return n_neighbors

    # Filter collection of boids by distance.
    def filter_boids_by_distance(self, max_distance, boids=None):
        result = []
        if boids == None:
            boids = Boid.flock
        if max_distance == math.inf:
            result = copy.copy(boids)
        else:
            mdsq = max_distance ** 2
            def near_enough(boid):
                dist = (boid.position - self.position).length_squared()
                return dist < mdsq
            result = list(filter(near_enough, boids))
        return result

    # Draw this Boid's “body” -- currently an irregular tetrahedron.
    def draw(self):
        center = self.position - Boid.temp_camera_aim_boid_draw_offset()
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
        if Boid.enable_annotation and center.length() < 3:
            def relative_force_annotation(offset, color):
                Draw.add_line_segment(center, center + offset, color)
            relative_force_annotation(self.last_separation_force, Vec3(1, 0, 0))
            relative_force_annotation(self.last_alignment_force, Vec3(0, 1, 0))
            relative_force_annotation(self.last_cohesion_force, Vec3(0, 0, 1))
            gray80 = Vec3(0.8, 0.8, 0.8)
            relative_force_annotation(self.last_combined_steering, gray80)

    # TODO 20230418 since at the moment I cannot animate the camera, this is a
    # stop gap where we offset all boid drawing by the position of "some boid"
    @staticmethod
    def temp_camera_aim_boid_draw_offset():
        return (Boid.selected_boid().position
                if Boid.tracking_camera
                else Vec3())

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
        # TODO modularity issue: other key callbacks are in Draw which
        #      does not import Boid. Maybe they should all be defined here?
        Boid.register_single_key_commands()

    # Register single key commands with the Open3D visualizer GUI.
    @staticmethod
    def register_single_key_commands():
        Draw.vis.register_key_callback(ord('S'), Boid.select_next_boid)
        Draw.vis.register_key_callback(ord('A'), Boid.toggle_annotation)
        Draw.vis.register_key_callback(ord('C'), Boid.toggle_tracking_camera)
        Draw.vis.register_key_callback(ord('W'), Boid.toggle_wrap_vs_avoid)
        Draw.vis.register_key_callback(ord('H'), Boid.print_help)

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

    # When a Boid gets more than "radius" from the origin, teleport it to the
    # other side of the world, just inside of its antipodal point.
    @staticmethod
    def sphere_wrap_around_flock(radius):
        # TODO totally ad hoc, catch any escapees in avoidance mode.
        if not Boid.wrap_vs_avoid:
            radius += 5
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

    # Returns currently selected boid, the one tracked by visualizer's camera.
    @staticmethod
    def selected_boid():
        return Boid.flock[Boid.selected_boid_index]
    
    # Select the "next" boid. This gets bound to the "s" key in the interactive
    # visualizer (hence the ignored "vis" arg). So typing s s s can be used to
    # cycle through the boids of a flock.
    @staticmethod
    def select_next_boid(vis = None):
        Boid.selected_boid_index += 1
        Boid.selected_boid_index = Boid.selected_boid_index % len(Boid.flock)

    # Global animation switch.
    enable_annotation = True

    # Toggle global animation switch.
    @staticmethod
    def toggle_annotation(vis = None):
        Boid.enable_annotation = not Boid.enable_annotation
    
    # Global tracking camera mode.
    # TODO 20230514 decided static camera might be the better initial value.
#    tracking_camera = True
    tracking_camera = False

    # Toggle global tracking camera mode.
    @staticmethod
    def toggle_tracking_camera(vis = None):
        Boid.tracking_camera = not Boid.tracking_camera

    # Global tracking camera mode.
    wrap_vs_avoid = False

    # Toggle global tracking camera mode.
    @staticmethod
    def toggle_wrap_vs_avoid(vis = None):
        Boid.wrap_vs_avoid = not Boid.wrap_vs_avoid

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


    # List of Boids in a flock
    # TODO 20230409 assumes there is only one flock. If more are
    #               ever needed there should be a Flock class.
    flock = []
    
    # The selected boid
    selected_boid_index = 0


    ############################################################################
    # TODO 20230510 I don't know where this should go. Some kind of geometric
    # utilities, perhaps Utilities.py? Maybe a class for steering behaviors?
    #
    # Also this is a special case for a preocedural sphere. It would be nice to
    # have for an arbitrary triangle mesh.
    
    # Returns the point of intersection of the agent's "forward" axis (half
    # line) with the given sphere. Returns None if there is no intersection.
    #
    # From https://en.wikipedia.org/wiki/Line–sphere_intersection particularly
    # the two equations under the text “Note that in the specific case where u
    # is a unit vector...”
    def path_sphere_intersection(self, radius, center=Vec3()):
        # Center and radius of sphere
        c = center
        r = radius
        # Origin and tangent (basis) of line
        o = self.position
        u = self.forward

        delta = (u.dot(o - c) ** 2) - (((o - c).length() ** 2) - r ** 2)
        if delta < 0:
#            print('delta negative, no intersection')
            return None
        else:

            d1 = -(u.dot(o - c)) + math.sqrt(delta)
#            d2 = -(u.dot(o - c)) - math.sqrt(delta)

#            if d1 == d2:
#                print('roots equal, one intersection')

            p1 = o + u * d1
#            p2 = o + u * d2

#                q = Boid.temp_camera_aim_boid_draw_offset()
#
#    #                Draw.add_line_segment(o - q, p1 - q, Vec3(1, 0, 1))
#    #    #            Draw.add_line_segment(o - q, p2 - q, Vec3(0, 1, 1))
#
#                if Boid.enable_annotation:
#                    Draw.add_line_segment(o - q, p1 - q, Vec3(1, 0, 1))
#    #                Draw.add_line_segment(o - q, p2 - q, Vec3(0, 1, 1))

            return p1


    # TODO 20230512 WIP for prototyping, duplicate constant from flock.py
    # For initial placememnt and wrap-around.
    sphere_diameter = 60
    sphere_radius = sphere_diameter / 2

    # TODO 20230512 WIP
    # Steer to avoid collision with spherical containment (boids inside sphere).
    def sphere_avoidance(self, min_dist, radius=sphere_radius, center=Vec3()):
        avoidance = Vec3()
        path_intersection = self.path_sphere_intersection(radius, center)
        if not path_intersection == None:
            # Too far away to care?
            dist_squared = (path_intersection - self.position).length_squared()
            if dist_squared < min_dist ** 2:
                toward_center = center - path_intersection
                pure_steering = toward_center.perpendicular_component(self.forward)
                avoidance = pure_steering.normalize()
                self.sphere_avoidance_annotation(avoidance, path_intersection)
        return avoidance

    def sphere_avoidance_annotation(self, avoidance, path_intersection):
        if Boid.enable_annotation:
            q = Boid.temp_camera_aim_boid_draw_offset()
            Draw.add_line_segment(path_intersection - q,
                                  path_intersection - q + avoidance,
                                  Vec3())
            Draw.add_line_segment(self.position - q,
                                  self.position - q + avoidance,
                                  Vec3())
            Draw.add_line_segment(self.position - q,
                                  path_intersection - q,
                                  Vec3(1, 0, 1))

    ############################################################################
