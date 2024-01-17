#-------------------------------------------------------------------------------
#
# flock.py -- new flock experiments
#
# Flock class, and top level script for running flock simulations.
#
# This file was just a script to run simulations after importing components of
# the flock model (Boid, Vec3, draw) defined as classes in other files. But the
# Boid class started to accumulate "static" methods related to a flock of boids
# (make_flock, run_flock, draw_flock). I decided to formalize that with a Flock
# class, defined here. This also handles mode settings from the Open3D GUI.
#
# This file still functions as a top level script which does:  Flock().run()
#
# MIT License -- Copyright © 2023 Craig Reynolds
#
#-------------------------------------------------------------------------------

import sys
import math
import itertools
import open3d as o3d
from Vec3 import Vec3
from Boid import Boid
from Draw import Draw
from Agent import Agent
import Utilities as util
from statistics import mean
from LocalSpace import LocalSpace
from obstacle import EvertedSphereObstacle
from obstacle import PlaneObstacle
from obstacle import CylinderObstacle
import shape

################################################################################
# TODO 20240104 using parallel threads/processes for simulation step

import time
import threading
import multiprocessing
from multiprocessing import Pool

import functools


def apply_next(boid):
    boid.apply_next_steer(boid.temp_time_step)
    return boid

def plan_next(boid):
    boid.plan_next_steer(boid.temp_time_step)
    return boid

# QQQ

################################################################################

class Flock:
    def __init__(self,
                 boid_count = 200,
                 sphere_diameter = 100,
                 sphere_center = Vec3(),
                 max_simulation_steps = math.inf,
                 fixed_time_step = False,
                 fixed_fps = 60,
                 ###############################################################
                 # TODO 20240105 Flock.multiprocessing flag, neighbor's cache
                 seed = 1234567890,
                 multiprocessing = False):
                 ###############################################################
        self.boid_count = boid_count              # Number of boids in Flock.
        self.sphere_radius = sphere_diameter / 2  # Radius of boid containment.
        self.sphere_center = sphere_center        # Center of boid containment.
        self.max_simulation_steps = max_simulation_steps # exit after n frames.
        self.fixed_time_step = fixed_time_step    # fixed time step vs realtime.
        self.fixed_fps = fixed_fps                # frame rate for fixed fps.
        self.boids = []                # List of boids in flock.
        self.selected_boid_index = 0   # Index of boid tracked by camera.
        self.total_avoid_fail = 0      # count pass through containment sphere.
        self.cumulative_sep_fail = 0   # separation fail: a pair of boids touch.
        self.simulation_paused = False # Simulation stopped, display continues.
        self.single_step = False       # perform one simulation step then pause.
        self.enable_annotation = True
        self.tracking_camera = False
        self.wrap_vs_avoid = False
        self.avoid_blend_mode = True   # obstacle avoid: blend vs hard switch
        self.min_time_to_collide = 0.8 # react to predicted impact (seconds)
        self.fps = util.Blender()
        # Flock's current list of obstacles.
        self.obstacles = []
        # Switchable pre-defined obstacle sets.
        self.obstacle_presets = self.pre_defined_obstacle_sets()
        self.obstacle_selection_counter = 0
        self.total_stalls = 0
        ########################################################################
        # TODO 20240105 Flock.multiprocessing flag, neighbor's cache
        self.multiprocessing = multiprocessing
        # If there is ever a need to have multiple Flock instances at the same
        # time, these steps with global effect should be reconsidered:
        ########################################################################
        Draw.set_random_seeds(seed)
        self.setup()

    ############################################################################
    # TODO 20240104 using parallel threads/processes for simulation step

    # Run boids simulation. (Currently runs until stopped by user.)
    def run(self):
        draw = Draw() ## ?? currently unused but should contain draw state
        Draw.start_visualizer(self.sphere_radius, self.sphere_center)
        Flock.vis_pairs.add_pair(Draw.vis, self)  # Pairing for key handlers.
        self.register_single_key_commands() # For Open3D visualizer GUI.
        self.make_boids(self.boid_count, self.sphere_radius, self.sphere_center)
        self.draw()
        self.cycle_obstacle_selection()
        
#        while self.still_running():
#            if self.run_simulation_this_frame():
#                Draw.clear_scene()
#                self.fly_flock(1 / self.fixed_fps
#                               if self.fixed_time_step or not Draw.enable
#                               else Draw.frame_duration)
#                self.sphere_wrap_around()
#                self.draw()
#                Draw.update_scene()
#                self.log_stats()
#                self.update_fps()

#        with Pool() as pool:
#        with Pool(processes=8) as pool:
        with Pool() as pool:
            while self.still_running():
                if self.run_simulation_this_frame():
                    Draw.clear_scene()
                    self.fly_flock(1 / self.fixed_fps
                                   if self.fixed_time_step or not Draw.enable
                                   else Draw.frame_duration,
                                   pool)
                    self.sphere_wrap_around()
                    self.draw()
                    Draw.update_scene()
                    self.log_stats()
                    self.update_fps()

        Draw.close_visualizer()
        print('Exit at step:', Draw.frame_counter)

    ############################################################################

    # Populate this flock by creating "count" boids with uniformly distributed
    # random positions inside a sphere with the given "radius" and "center".
    # Each boid has a uniformly distributed random orientation.
    def make_boids(self, count, radius, center):
        for i in range(count):
            boid = Boid(self)
            boid.sphere_radius = radius
            boid.sphere_center = center
#            boid.ls.randomize_orientation()
            boid.ls = boid.ls.randomize_orientation()
            boid.ls.p = (center + (radius * 0.95 *
                                   Vec3.random_point_in_unit_radius_sphere()))
            self.boids.append(boid)
        # Initialize per-Boid cached_nearest_neighbors. Randomize time stamp.
        for b in self.boids:
            b.recompute_nearest_neighbors()
            t = util.frandom01() * b.neighbor_refresh_rate
            b.time_since_last_neighbor_refresh = t

    # Draw each boid in flock.
    def draw(self):
        if Draw.enable:
            Draw.update_camera(self.selected_boid().position if
                               self.tracking_camera else Vec3())
            for o in self.obstacles:
                o.draw()
            for boid in self.boids:
                boid.draw(color=(Vec3(0, 1, 0) if
                                 self.is_neighbor_of_selected(boid) else None))

    def is_neighbor_of_selected(self, boid):
        return (self.enable_annotation and
                self.tracking_camera and
                self.selected_boid().is_neighbor(boid))

    ############################################################################
    # TODO 20240104 using parallel threads/processes for simulation step

#    # Fly each boid in flock for one simulation step. Consists of two sequential
#    # steps to avoid artifacts from order of boids. First a "sense/plan" phase
#    # which computes the desired steering based on current state. Then an "act"
#    # phase which actually moves the boids.
#    def fly_flock(self, time_step):
#        for boid in self.boids:
#            boid.plan_next_steer(time_step)
#        for boid in self.boids:
#            boid.apply_next_steer(time_step)
#        for boid in self.boids:
#            if boid.speed < boid.min_speed:
#                self.total_stalls += 1


#        # Fly each boid in flock for one simulation step. Consists of two sequential
#        # steps to avoid artifacts from order of boids. First a "sense/plan" phase
#        # which computes the desired steering based on current state. Then an "act"
#        # phase which actually moves the boids.
#    #    def fly_flock(self, time_step):
#        def fly_flock(self, time_step, pool):
#    #        for boid in self.boids:
#    #            boid.plan_next_steer(time_step)
#    #        for boid in self.boids:
#    #            boid.apply_next_steer(time_step)
#
#
#    #        ### TODO
#    #        ###     ok, this is definitely not the right thing
#    #        ###     for no graphics, it runs at 5 fps versus 50 fps
#    #        ###     but the simulation seems frozen, since maybe per-process memory?
#    #
#    #        pool.map(functools.partial(Boid.plan_next_steer, time_step=time_step),
#    #                 self.boids)
#    #        pool.map(functools.partial(Boid.apply_next_steer, time_step=time_step),
#    #                 self.boids)
#
#
#    #        def map_over_boids_range(function, time_step, start_index, end_index):
#    #            for boid in self.boids[start_index : end_index]:
#    #                function(boid, time_step)
#
#            def map_over_boids_range(function, time_step, start_index, end_index):
#                for i in range(start_index, end_index):
#                    function(self.boids[i], time_step)
#
#    #        print('create threads')
#    #        threads = []
#    #        for i in range(10):
#
#
#    #        batch_size = 20
#    #        batch_size = 10
#    #        batch_size = 40
#    #        batch_size = 100
#            batch_size = 5
#
#
#            threads = []
#            for i in range(0, len(self.boids), batch_size):
#                threads.append(threading.Thread(target=map_over_boids_range,
#                                                args=(Boid.plan_next_steer,
#                                                      time_step, i, i + batch_size)))
#            for t in threads:
#                t.start()
#            for t in threads:
#                t.join()
#
#
#            threads = []
#            for i in range(0, len(self.boids), batch_size):
#                threads.append(threading.Thread(target=map_over_boids_range,
#                                                args=(Boid.apply_next_steer,
#                                                      time_step, i, i + batch_size)))
#            for t in threads:
#                t.start()
#            for t in threads:
#                t.join()
#
#
#
#            for boid in self.boids:
#                if boid.speed < boid.min_speed:
#                    self.total_stalls += 1

#        # Fly each boid in flock for one simulation step. Consists of two sequential
#        # steps to avoid artifacts from order of boids. First a "sense/plan" phase
#        # which computes the desired steering based on current state. Then an "act"
#        # phase which actually moves the boids.
#    #    def fly_flock(self, time_step):
#        def fly_flock(self, time_step, pool):
#    #        for boid in self.boids:
#    #            boid.plan_next_steer(time_step)
#    #        for boid in self.boids:
#    #            boid.apply_next_steer(time_step)
#
#
#            batch_size = 20
#            batch_args = []
#
#            for i in range(0, len(self.boids), batch_size):
#                batch_args.append([time_step, self.boids[i : i + batch_size]])
#
#    #            threads.append(threading.Thread(target=map_over_boids_range,
#    #                                            args=(Boid.apply_next_steer,
#    #                                                  time_step, i, i + batch_size)))
#
#
#            def map_over_boids_slice(function, time_step, boids_slice):
#                for boid in boids_slice:
#                    function(boid, time_step)
#
#
#
#            self.boids = pool.map(functools.partial(Boid.plan_next_steer,
#                                                    time_step=time_step),
#                                  self.boids[i : i + batch_size])
#            self.boids = pool.map(functools.partial(Boid.apply_next_steer,
#                                                    time_step=time_step),
#                                  self.boids[i : i + batch_size])
#
#
#            for boid in self.boids:
#                if boid.speed < boid.min_speed:
#                    self.total_stalls += 1

#        # Fly each boid in flock for one simulation step. Consists of two sequential
#        # steps to avoid artifacts from order of boids. First a "sense/plan" phase
#        # which computes the desired steering based on current state. Then an "act"
#        # phase which actually moves the boids.
#    #    def fly_flock(self, time_step):
#        def fly_flock(self, time_step, pool):
#    #        for boid in self.boids:
#    #            boid.plan_next_steer(time_step)
#    #        for boid in self.boids:
#    #            boid.apply_next_steer(time_step)
#
#
#    #        batch_size = 20
#    #        batch_args = []
#    #
#    #        for i in range(0, len(self.boids), batch_size):
#    #            batch_args.append([time_step, self.boids[i : i + batch_size]])
#    #
#    #
#    #
#    #        def map_over_boids_slice(function, time_step, boids_slice):
#    #            for boid in boids_slice:
#    #                function(boid, time_step)
#
#
#
#
#    #        self.boids = pool.map(functools.partial(Boid.plan_next_steer,
#    #                                                time_step=time_step),
#    #                              self.boids)
#    #        self.boids = pool.map(functools.partial(Boid.apply_next_steer,
#    #                                                time_step=time_step),
#    #                              self.boids)
#
#
#    #        def plan_next(boid):
#    #            boid.plan_next_steer(boid, time_step)
#    #            return boid
#    #
#    #        def apply_next(boid):
#    #            boid.apply_next_steer(boid, time_step)
#    #            return boid
#
#    #        self.boids = pool.map(plan_next, self.boids)
#    #        self.boids = pool.map(apply_next, self.boids)
#
#
#            interleave_boid_and_time_step = []
#            for boid in self.boids:
#    #            interleave_boid_and_time_step.append(boid)
#    #            interleave_boid_and_time_step.append(time_step)
#                interleave_boid_and_time_step.append([boid,time_step])
#
#            interleave_boid_and_time_step = pool.map(plan_next, interleave_boid_and_time_step)
#            interleave_boid_and_time_step = pool.map(apply_next, interleave_boid_and_time_step)
#
#            self.boids = []
#            for pair in interleave_boid_and_time_step:
#                self.boids.append(pair[0])
#
#
#            for boid in self.boids:
#                if boid.speed < boid.min_speed:
#                    self.total_stalls += 1


#        # Fly each boid in flock for one simulation step. Consists of two sequential
#        # steps to avoid artifacts from order of boids. First a "sense/plan" phase
#        # which computes the desired steering based on current state. Then an "act"
#        # phase which actually moves the boids.
#    #    def fly_flock(self, time_step):
#        def fly_flock(self, time_step, pool):
#    #        for boid in self.boids:
#    #            boid.plan_next_steer(time_step)
#    #        for boid in self.boids:
#    #            boid.apply_next_steer(time_step)
#
#
#
#
#    #            interleave_boid_and_time_step = []
#    #            for boid in self.boids:
#    #    #            interleave_boid_and_time_step.append(boid)
#    #    #            interleave_boid_and_time_step.append(time_step)
#    #                interleave_boid_and_time_step.append([boid,time_step])
#    #
#    #            interleave_boid_and_time_step = pool.map(plan_next, interleave_boid_and_time_step)
#    #            interleave_boid_and_time_step = pool.map(apply_next, interleave_boid_and_time_step)
#    #
#    #            self.boids = []
#    #            for pair in interleave_boid_and_time_step:
#    #                self.boids.append(pair[0])
#
#
#            for boid in self.boids:
#                boid.temp_time_step = time_step
#
#
#
#            self.boids = pool.map(plan_next, self.boids)
#            self.boids = pool.map(apply_next, self.boids)
#
#    #        self.boids = []
#    #        for pair in interleave_boid_and_time_step:
#    #            self.boids.append(pair[0])
#
#
#            for boid in self.boids:
#                if boid.speed < boid.min_speed:
#                    self.total_stalls += 1


#        # Fly each boid in flock for one simulation step. Consists of two sequential
#        # steps to avoid artifacts from order of boids. First a "sense/plan" phase
#        # which computes the desired steering based on current state. Then an "act"
#        # phase which actually moves the boids.
#    #    def fly_flock(self, time_step):
#        def fly_flock(self, time_step, pool):
#    #        for boid in self.boids:
#    #            boid.plan_next_steer(time_step)
#    #        for boid in self.boids:
#    #            boid.apply_next_steer(time_step)
#
#            for boid in self.boids:
#                boid.temp_time_step = time_step
#            self.boids = pool.map(plan_next, self.boids, chunksize=25)
#            self.boids = pool.map(apply_next, self.boids, chunksize=25)
#            for boid in self.boids:
#                if boid.speed < boid.min_speed:
#                    self.total_stalls += 1

    ############################################################################
    # TODO 20240105 Flock.multiprocessing flag, neighbor's cache

    # Fly each boid in flock for one simulation step. Consists of two sequential
    # steps to avoid artifacts from order of boids. First a "sense/plan" phase
    # which computes the desired steering based on current state. Then an "act"
    # phase which actually moves the boids.
    def fly_flock(self, time_step, pool):
        if self.multiprocessing:
            for boid in self.boids:
                boid.temp_time_step = time_step
            self.boids = pool.map(plan_next, self.boids, chunksize=25)
            self.boids = pool.map(apply_next, self.boids, chunksize=25)
            for boid in self.boids:
                if boid.speed < boid.min_speed:
                    self.total_stalls += 1
        else:
            for boid in self.boids:
                boid.plan_next_steer(time_step)
            for boid in self.boids:
                boid.apply_next_steer(time_step)
    ############################################################################


    # QQQ
    ############################################################################

    # When a Boid gets more than "radius" from the origin, teleport it to the
    # other side of the world, just inside of its antipodal point.
    def sphere_wrap_around(self):
        radius = self.sphere_radius
        center = self.sphere_center
        for boid in self.boids:
            bp = boid.position
            distance_from_center = (bp - center).length()
            if distance_from_center > radius:
                new_position = (center - bp).normalize() * radius * 0.95
                boid.ls.p = new_position
                boid.recompute_nearest_neighbors()
                if not self.wrap_vs_avoid:
                    self.total_avoid_fail += 1

    # Calculate and log various statistics for flock.
    def log_stats(self):
        if not self.simulation_paused:
            Draw.measure_frame_duration()
            if Draw.frame_counter % 100 == 0:
                average_speed = mean([b.speed for b in self.boids])
                # Loop over all unique pairs of distinct boids: ab==ba, not aa
                min_sep = math.inf
                ave_sep = 0
                pair_count = 0
                # Via https://stackoverflow.com/a/942551/1991373
                for (p, q) in itertools.combinations(self.boids, 2):
                    dist = (p.position - q.position).length()
                    if min_sep > dist:
                        min_sep = dist
                    ave_sep += dist
                    pair_count += 1
                    if dist < 2 * p.body_radius:
                        self.cumulative_sep_fail += 1
                ave_sep /= pair_count
                #
                max_nn_dist = 0
                ################################################################
                # TODO 20240105 Flock.multiprocessing flag, neighbor's cache
                # temporarily removed for testing
                for b in self.boids:
                    n = b.cached_nearest_neighbors[0]
                    dist = (b.position - n.position).length()
                    if max_nn_dist < dist:
                        max_nn_dist = dist
                ################################################################
                print(str(Draw.frame_counter) +
                      ' fps=' + str(round(self.fps.value)) +
                      ', ave_speed=' + str(average_speed)[0:5] +
                      ', min_sep=' + str(min_sep)[0:5] +
                      ', ave_sep=' + str(ave_sep)[0:5] +
                      ', max_nn_dist=' + str(max_nn_dist)[0:5] +
                      ', cumulative_sep_fail/boid=' +
                          (str(self.cumulative_sep_fail / len(self.boids)) +
                          '00')[0:5] +
                      ', avoid_fail=' + str(self.total_avoid_fail) +
                      ', stalls=' + str(self.total_stalls))

#                ################################################################
#                # TODO 20240104 how big is a flock?
#                all_birds_size = 0
#                for boid in self.boids:
#                    all_birds_size += sys.getsizeof(boid)
#                print('all_birds_size =', all_birds_size)
#                ################################################################

    # Keep track of a smoothed (LPF) version of frames per second metric.
    def update_fps(self):
        self.fps.blend(self.fixed_fps if self.fixed_time_step
                                      else int(1 / Draw.frame_duration),
                       0.95)

    # Based on pause/play and single step. Called once per frame from main loop.
    def run_simulation_this_frame(self):
        ok_to_run = self.single_step or not self.simulation_paused
        self.single_step = False
        return ok_to_run

    # Returns currently selected boid, the one that the tracking camera
    # tracks, for which steering force annotation is shown.
    def selected_boid(self):
        return self.boids[self.selected_boid_index]

    # Register single key commands with the Open3D visualizer GUI.
    def register_single_key_commands(self):
        Draw.register_key_callback(ord(' '), Flock.toggle_paused_mode)
        Draw.register_key_callback(ord('1'), Flock.set_single_step_mode)
        Draw.register_key_callback(ord('S'), Flock.select_next_boid)
        Draw.register_key_callback(ord('A'), Flock.toggle_annotation)
        Draw.register_key_callback(ord('C'), Flock.toggle_tracking_camera)
        Draw.register_key_callback(ord('W'), Flock.toggle_wrap_vs_avoid)
        Draw.register_key_callback(ord('E'), Flock.toggle_dynamic_erase)
        Draw.register_key_callback(ord('F'), Flock.toggle_fixed_time_step)
        Draw.register_key_callback(ord('B'), Flock.toggle_avoid_blend_mode)
        Draw.register_key_callback(ord('O'), Flock.cycle_obstacle_selection)
        Draw.register_key_callback(ord('H'), Flock.print_help)

    # Toggle simulation pause mode.
    def toggle_paused_mode(self):
        self = Flock.convert_to_flock(self)
        if self.simulation_paused:
            Draw.reset_timer()
        self.simulation_paused = not self.simulation_paused

    # Take single simulation step then enter pause mode.
    def set_single_step_mode(self):
        self = Flock.convert_to_flock(self)
        self.single_step = True
        self.simulation_paused = True

    # Select the "next" boid. This gets bound to the "s" key in the interactive
    # visualizer. So typing s s s will cycle through the boids of a flock.
    def select_next_boid(self):
        self = Flock.convert_to_flock(self)
        self.selected_boid_index = ((self.selected_boid_index + 1) %
                                    len(self.boids))
        self.single_step_if_paused()

    # Toggle drawing of annotation (lines to represent vectors) in the GUI.
    def toggle_annotation(self):
        self = Flock.convert_to_flock(self)
        self.enable_annotation = not self.enable_annotation

    # Toggle between static camera and boid-tracking camera mode.
    def toggle_tracking_camera(self):
        self = Flock.convert_to_flock(self)
        self.tracking_camera = not self.tracking_camera
        self.single_step_if_paused()

    # Toggle mode for sphere-wrap-around versus sphere-avoidance.
    def toggle_wrap_vs_avoid(self):
        self = Flock.convert_to_flock(self)
        self.wrap_vs_avoid = not self.wrap_vs_avoid

    # Toggle mode for erasing dynamic graphics ("spacetime boid worms").
    def toggle_dynamic_erase(self):
        self = Flock.convert_to_flock(self)
        Draw.clear_dynamic_mesh = not Draw.clear_dynamic_mesh
        if self.tracking_camera and not Draw.clear_dynamic_mesh:
            print('!!! "spacetime boid worms" do not work correctly with ' +
                  'boid tracking camera mode ("C" key). Awaiting fix for ' +
                  'Open3D bug 6009.')

    # Toggle between realtime/as-fast-as-possible versus fixed time step of 1/60
    def toggle_fixed_time_step(self):
        self = Flock.convert_to_flock(self)
        self.fixed_time_step = not self.fixed_time_step

    # Toggle between blend/hard-switch for obstacle avoidance.
    def toggle_avoid_blend_mode(self):
        self = Flock.convert_to_flock(self)
        self.avoid_blend_mode = not self.avoid_blend_mode
        print('    Flock.avoid_blend_mode =', self.avoid_blend_mode)

    # Cycle through various pre-defined combinations of Obstacle types.
    def cycle_obstacle_selection(self):
        self = Flock.convert_to_flock(self)
        # Remove geometry of current Obstacles from Open3D scene.
        if Draw.enable:
            for o in self.obstacles:
                Draw.vis.remove_geometry(o.tri_mesh, False)
        # Set Obstacle list to next preset combination.
        next_set = self.obstacle_selection_counter % len(self.obstacle_presets)
        self.obstacle_selection_counter += 1
        self.obstacles = self.obstacle_presets[next_set]
        # Add geometry of current obstacles to Open3D scene.
        if Draw.enable:
            for o in self.obstacles:
                o.draw()
                if o.tri_mesh: # TODO only need until all Obstacles draw themselves.
                    Draw.vis.add_geometry(o.tri_mesh, False)
        # Print description of current Obstacle set.
        description = '\n  obstacles: '
        if self.obstacles:
            seperator = ''
            for o in self.obstacles:
                description += seperator + str(o)
                seperator = ', '
        else:
            description += 'none'
        print(description + '\n')

    # Builds a list of preset obstacle combinations, each a list of Obstacles.
    def pre_defined_obstacle_sets(self):
        main_sphere = EvertedSphereObstacle(self.sphere_radius, self.sphere_center)
        plane_obstacle = PlaneObstacle()
        
        cep = Vec3(0, self.sphere_radius + 0.1, 0)
        cobs = CylinderObstacle(10, cep, -cep)
        
        scep = Vec3(-1, 1, 1) * self.sphere_radius * 0.8
        squat_cyl_obs = CylinderObstacle(20, scep, -scep)

        diag = Vec3(1,1,1).normalize()
        uncentered_cyl_obs = CylinderObstacle(5, diag * 5, diag * 30)
        
        # 6 symmetric cylinders on main axes.
        c3r = 4
        c3o = 15
        c3h = 20
        cyl3x = CylinderObstacle(c3r, Vec3(-c3h, 0, c3o), Vec3(c3h, 0, c3o))
        cyl3y = CylinderObstacle(c3r, Vec3(c3o, -c3h, 0), Vec3(c3o, c3h, 0))
        cyl3z = CylinderObstacle(c3r, Vec3(0, c3o, -c3h), Vec3(0, c3o, c3h))
        c3o = - c3o
        cyl3p = CylinderObstacle(c3r, Vec3(-c3h, 0, c3o), Vec3(c3h, 0, c3o))
        cyl3q = CylinderObstacle(c3r, Vec3(c3o, -c3h, 0), Vec3(c3o, c3h, 0))
        cyl3r = CylinderObstacle(c3r, Vec3(0, c3o, -c3h), Vec3(0, c3o, c3h))

        # Preset obstacle combinations:
        return [[main_sphere],
                [main_sphere, plane_obstacle],
                [main_sphere, uncentered_cyl_obs],
                [main_sphere, cyl3x, cyl3y, cyl3z, cyl3p, cyl3q, cyl3r],
                [main_sphere, cobs],
                [main_sphere, plane_obstacle, cobs],
                [cobs],
                [squat_cyl_obs],
                [squat_cyl_obs, main_sphere],
                [squat_cyl_obs, plane_obstacle],
                []]

    # Print mini-help on shell.
    def print_help(self):
        self = Flock.convert_to_flock(self)
        print()
        print('  flock single key commands:')
        print('    space: toggle simulation run/pause')
        print('    1:     single simulation step, then pause')
        print('    c:     toggle camera between static and boid tracking')
        print('    s:     select next boid for camera tracking')
        print('    a:     toggle drawing of steering annotation')
        print('    w:     toggle between sphere wrap-around or avoidance')
        print('    e:     toggle erase mode (spacetime boid worms)')
        print('    f:     toggle realtime versus fixed time step of 1/60sec')
        print('    b:     toggle blend vs hard switch for obstacle avoidance')
        print('    o:     cycle through obstacle selections')
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

    # Allows writing global key command handlers as methods on a Flock instance.
    # If the given "self" value is not a Flock instance, this assumes it it a
    # Visualizer instance (passed to key handlers) and looks up the Flock
    # instance associated with that Vis. (Normally only one of each exists.)
    vis_pairs = util.Pairings()
    def convert_to_flock(self):
        if not isinstance(self, Flock):
            self = Flock.vis_pairs.get_peer(self)
        return self

    # Some mode-change key commands need a redraw to show their effect. Ideally
    # it would do just a redraw without simulation, but that turned out to be a
    # little more complicated (since Boid annotation state is not saved) so this
    # is good enough.
    def single_step_if_paused(self):
        if self.simulation_paused:
            self.set_single_step_mode()

    # Simulation continues running until this returns False.
    def still_running(self):
        a = True if not Draw.enable else Draw.vis.poll_events()
        b = Draw.frame_counter < self.max_simulation_steps
        return a and b

    # Perform "before simulation" tasks: log versions, run unit tests.
    def setup(self):
        # Log versions.
        print('Python', sys.version)
        print('Open3D', o3d.__version__)
        # Run unit tests.
        Vec3.unit_test()
        LocalSpace.unit_test()
        Agent.unit_test()
        util.unit_test()
        shape.unit_test()
        print('All unit tests OK.')


if __name__ == "__main__":

    # TODO 20230530 runs OK (if slow) but something wrong in center offset case
#    Flock(400).run()                       # OK
#    Flock(400, 100).run()                  # OK
#    Flock(400, 100, Vec3(100, 0, 0)).run() # containment sphere still at origin
#
#    Flock(200, 60, Vec3(), 200).run()      # Test max_simulation_steps
#    Flock(max_simulation_steps=200, fixed_time_step=True, fixed_fps=30).run()
#    Flock(max_simulation_steps=200, fixed_time_step=True, seed=438538457).run()

    ############################################################################
    # TODO 20240104 using parallel threads/processes for simulation step

#    test_pool()
#    quit()
    
    ############################################################################

    ############################################################################
    # TODO 20240104 using parallel threads/processes for simulation step

#    Draw.enable = False
#    Flock().run()
#    Flock(multiprocessing=True).run()

#    Flock(boid_count=20).run()


#        Draw.enable = False
#    #    Flock().run()
#        Flock(multiprocessing=True).run()

#    Flock().run()

    ############################################################################

#    util.executions_per_second(Vec3.unit_test)

    ############################################################################

    print(1e-13)
    print(util.epsilon)
    Flock().run()
