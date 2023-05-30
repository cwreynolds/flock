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
# class, defined here.
#
# This file continues to function as a top level script running:  Flock().run()
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
        self.total_sep_fail = 0     # separation fail: pair of boids touch.
        self.setup()

    # Run boids simulation. (Currently runs until stopped by user.)
    def run(self):
        draw = Draw() ## ?? currently unused but should contain draw state
        Draw.start_visualizer()
        self.make_boids(self.boid_count, self.sphere_radius, self.sphere_center)
        self.draw()
        while Draw.still_running():
            if Draw.run_simulation_this_frame():
                Draw.clear_scene()
                self.steer_flock(Draw.frame_duration)
                self.sphere_wrap_around(self.sphere_radius)
                self.draw()
                Draw.update_scene()
                self.log_stats()
        Draw.close_visualizer()

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
        # TODO modularity issue: other key callbacks are in Draw which
        #      does not import Boid. Maybe they should all be defined here?
        Boid.register_single_key_commands()

    # Returns currently selected boid, the one that the tracking camera
    # tracks, for which steering force annotation is shown.
    def selected_boid(self):
        return self.boids[self.selected_boid_index]

    # Select the "next" boid. This gets bound to the "s" key in the interactive
    # visualizer (hence the ignored "vis" arg). So typing s s s can be used to
    # cycle through the boids of a flock.
    def select_next_boid(self):
        self.selected_boid_index = ((self.selected_boid_index + 1) %
                                    len(self.boids))

    # Draw each boid in flock.
    def draw(self):
        Draw.temp_camera_lookat = (self.selected_boid().position
                                   if Boid.tracking_camera
                                   else Vec3())
        for boid in self.boids:
            boid.draw()

    # Apply steer_to_flock() to each boid in flock.
    def steer_flock(self, time_step):
        for boid in self.boids:
            boid.steer_to_flock(time_step)

    # When a Boid gets more than "radius" from the origin, teleport it to the
    # other side of the world, just inside of its antipodal point.
    def sphere_wrap_around(self, radius):
        # TODO totally ad hoc, catch any escapees in avoidance mode.
        if not Boid.wrap_vs_avoid:
            radius += 5
        for boid in self.boids:
            bp = boid.position
            distance_from_origin = bp.length()
            if distance_from_origin > radius:
                new_position = (-bp).normalize() * radius * 0.95
                boid.ls.p = new_position
                if not Boid.wrap_vs_avoid:
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


if __name__ == "__main__":
    # TODO 20230530 runs OK (but slow) except containment sphere is still 60.
#    Flock(400, 100).run()
    Flock().run()
