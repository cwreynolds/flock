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
# This file a]still functions as a top level script which does:  Flock().run()
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

class Flock:

    def __init__(self, boid_count=200, sphere_diameter=60, sphere_center=Vec3()):
        self.boid_count = boid_count
        self.sphere_radius = sphere_diameter / 2
        self.sphere_center = sphere_center
        self.boids = []
        self.selected_boid_index = 0
        self.total_avoid_fail = 0  # count pass through spherical containment.
        self.total_sep_fail = 0    # separation fail: a pair of boids touch.
        self.enable_annotation = True
        self.tracking_camera = False
        self.wrap_vs_avoid = False
        Flock.most_recent = self  # used for handlers in global GUI.
        self.setup()

    # Run boids simulation. (Currently runs until stopped by user.)
    def run(self):
        draw = Draw() ## ?? currently unused but should contain draw state
        Draw.start_visualizer(self.sphere_radius, self.sphere_center)
        self.register_single_key_commands() # For Open3D visualizer GUI.
        self.make_boids(self.boid_count, self.sphere_radius, self.sphere_center)
        self.draw()
        while Draw.still_running():
            if Draw.run_simulation_this_frame():
                Draw.clear_scene()
                self.fly_flock(Draw.frame_duration)
                self.sphere_wrap_around()
                self.draw()
                Draw.update_scene()
                self.log_stats()
        Draw.close_visualizer()

    # Populate this flock by creating "count" boids with a uniformly distributed
    # random positions inside a sphere with the given "radius" and "center".
    # Each boid has a uniformly distributed random orientation.
    def make_boids(self, count, radius, center):
        for i in range(count):
            boid = Boid(self)
            boid.sphere_radius = radius
            boid.sphere_center = center
            boid.ls.randomize_orientation()
            random_point = Vec3.random_point_in_unit_radius_sphere()
            boid.ls.p = center + (radius * random_point)
            self.boids.append(boid)
        # Initialize per-Boid cached_nearest_neighbors. Randomize time stamp.
        for b in self.boids:
            b.recompute_nearest_neighbors()
            t = util.frandom01() * b.neighbor_refresh_rate
            b.time_since_last_neighbor_refresh = t

    # Draw each boid in flock.
    def draw(self):
        Draw.temp_camera_lookat = (self.selected_boid().position
                                   if self.tracking_camera
                                   else Vec3())
        for boid in self.boids:
            boid.draw()

    # Apply fly_with_flock() to each boid in flock.
    def fly_flock(self, time_step):
        for boid in self.boids:
            boid.fly_with_flock(time_step)

    # When a Boid gets more than "radius" from the origin, teleport it to the
    # other side of the world, just inside of its antipodal point.
    def sphere_wrap_around(self):
        radius = self.sphere_radius
        center = self.sphere_center
        # TODO totally ad hoc, catch any escapees in avoidance mode.
        if not self.wrap_vs_avoid:
            radius += 5
        for boid in self.boids:
            bp = boid.position
            distance_from_center = (bp - center).length()
            if distance_from_center > radius:
                new_position = (center - bp).normalize() * radius * 0.95
                boid.ls.p = new_position
                if not self.wrap_vs_avoid:
                    self.total_avoid_fail += 1

    # Calculate and log various statistics for flock.
    def log_stats(self):
        if Draw.frame_counter % 100 == 0 and not Draw.simulation_paused:
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
                if dist < 2:
                    self.total_sep_fail += 1
            ave_sep /= pair_count
            #
            max_nn_dist = 0
            for b in self.boids:
                n = b.cached_nearest_neighbors[0]
                dist = (b.position - n.position).length()
                if max_nn_dist < dist:
                    max_nn_dist = dist
            print(str(Draw.frame_counter) +
                  ' fps=' + str(int(1 / Draw.frame_duration)) +
                  ', ave_speed=' + str(average_speed)[0:5] +
                  ', min_sep=' + str(min_sep)[0:5] +
                  ', ave_sep=' + str(ave_sep)[0:5] +
                  ', max_nn_dist=' + str(max_nn_dist)[0:5] +
                  ', sep_fail/boid=' + str(self.total_sep_fail  /
                                           len(self.boids)) +
                  ', avoid_fail=' + str(self.total_avoid_fail))

    # Register single key commands with the Open3D visualizer GUI.
    def register_single_key_commands(self):
        Draw.vis.register_key_callback(ord('S'), Flock.select_next_boid)
        Draw.vis.register_key_callback(ord('A'), Flock.toggle_annotation)
        Draw.vis.register_key_callback(ord('C'), Flock.toggle_tracking_camera)
        Draw.vis.register_key_callback(ord('W'), Flock.toggle_wrap_vs_avoid)
        Draw.vis.register_key_callback(ord('E'), Flock.toggle_dynamic_erase)
        Draw.vis.register_key_callback(ord('H'), Flock.print_help)

    # Returns currently selected boid, the one that the tracking camera
    # tracks, for which steering force annotation is shown.
    def selected_boid(self):
        return self.boids[self.selected_boid_index]

    # Select the "next" boid. This gets bound to the "s" key in the interactive
    # visualizer. So typing s s s will cycle through the boids of a flock.
    def select_next_boid(self):
        self = Flock.use_most_recent_instance_if_not_flock(self)
        self.selected_boid_index = ((self.selected_boid_index + 1) %
                                    len(self.boids))

    # Toggle drawing of annotation (lines to represent vectors) in the GUI.
    def toggle_annotation(self):
        self = Flock.use_most_recent_instance_if_not_flock(self)
        self.enable_annotation = not self.enable_annotation

    # Toggle between static camera and boid-tracking camera mode.
    def toggle_tracking_camera(self):
        self = Flock.use_most_recent_instance_if_not_flock(self)
        self.tracking_camera = not self.tracking_camera

    # Toggle mode for sphere-wrap-around versus sphere-avoidance.
    def toggle_wrap_vs_avoid(self):
        self = Flock.use_most_recent_instance_if_not_flock(self)
        self.wrap_vs_avoid = not self.wrap_vs_avoid

    # Toggle mode for erasing dynamic graphics ("spacetime boid worms").
    def toggle_dynamic_erase(self):
        self = Flock.use_most_recent_instance_if_not_flock(self)
        Draw.clear_dynamic_mesh = not Draw.clear_dynamic_mesh
        if self.tracking_camera and not self.clear_dynamic_mesh:
            print('!!! "spacetime boid worms" do not work correctly with ' +
                  'boid tracking camera mode ("C" key). Awaiting fix for ' +
                  'Open3D bug 6009.')

    # Print mini-help on shell.
    def print_help(self):
        self = Flock.use_most_recent_instance_if_not_flock(self)
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

    # Allows writing global key command handlers as instance methods. If the
    # "self" value is not a Flock instance, this substitutes the most recently
    # created Flock instance.
    def use_most_recent_instance_if_not_flock(self):
        return self if isinstance(self, Flock) else Flock.most_recent

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
        print('All unit tests OK.')


if __name__ == "__main__":

    # TODO 20230530 runs OK (if slow) but something wrong in center offset case
#    Flock(400).run()                        # OK
#    Flock(400, 100).run()                   # OK
#    Flock(400, 100, Vec3(100, 0, 0)).run()  # containment sphere still at origin
    
    Flock().run()
