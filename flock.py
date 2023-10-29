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

class Flock:

    def __init__(self,
                 boid_count = 200,
                 sphere_diameter = 60,
                 sphere_center = Vec3(),
                 max_simulation_steps = math.inf,
                 fixed_time_step = False,
                 fixed_fps = 60,
                 seed = 1234567890):
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
        # give Flock a default list of obstacles
        self.obstacles = [EvertedSphereObstacle(self.sphere_radius,
                                                self.sphere_center)]
        # If there is ever a need to have multiple Flock instances at the same
        # time, these steps should be reconsidered:
        Draw.set_random_seeds(seed)
        self.setup()

    # Run boids simulation. (Currently runs until stopped by user.)
    def run(self):
        draw = Draw() ## ?? currently unused but should contain draw state
        Draw.start_visualizer(self.sphere_radius, self.sphere_center)
        Flock.vis_pairs.add_pair(Draw.vis, self)  # Pairing for key handlers.
        self.register_single_key_commands() # For Open3D visualizer GUI.
        self.make_boids(self.boid_count, self.sphere_radius, self.sphere_center)
        self.draw()
        while self.still_running():
            if self.run_simulation_this_frame():
                Draw.clear_scene()
                self.fly_flock(1 / self.fixed_fps if self.fixed_time_step
                               else Draw.frame_duration)
                self.sphere_wrap_around()
                self.draw()
                Draw.update_scene()
                self.log_stats()
                self.update_fps()
        Draw.close_visualizer()
        print('Exit at step:', Draw.frame_counter)

    # Populate this flock by creating "count" boids with uniformly distributed
    # random positions inside a sphere with the given "radius" and "center".
    # Each boid has a uniformly distributed random orientation.
    def make_boids(self, count, radius, center):
        for i in range(count):
            boid = Boid(self)
            boid.sphere_radius = radius
            boid.sphere_center = center
            boid.ls.randomize_orientation()
            boid.ls.p = (center + (radius * 0.5 *
                                   Vec3.random_point_in_unit_radius_sphere()))
            self.boids.append(boid)
        # Initialize per-Boid cached_nearest_neighbors. Randomize time stamp.
        for b in self.boids:
            b.recompute_nearest_neighbors()
            t = util.frandom01() * b.neighbor_refresh_rate
            b.time_since_last_neighbor_refresh = t

    # Draw each boid in flock.
    def draw(self):
        Draw.update_camera(self.selected_boid().position if
                           self.tracking_camera else Vec3())
        for boid in self.boids:
            color = None
            if self.enable_annotation and self.tracking_camera and \
                    boid in self.selected_boid().cached_nearest_neighbors:
                color = Vec3(0.0, 1.0, 0.0)
            boid.draw(color=color)

    # Fly each boid in flock for one simulation step. Consists of two sequential
    # steps to avoid artifacts from order of boids. First a "sense/plan" phase
    # which computes the desired steering based on current state. Then an "act"
    # phase which actually moves the boids.
    def fly_flock(self, time_step):
        for boid in self.boids:
            boid.plan_next_steer(time_step)
        for boid in self.boids:
            boid.apply_next_steer(time_step)

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
                for b in self.boids:
                    n = b.cached_nearest_neighbors[0]
                    dist = (b.position - n.position).length()
                    if max_nn_dist < dist:
                        max_nn_dist = dist
                print(str(Draw.frame_counter) +
                      ' fps=' + str(round(self.fps.value)) +
                      ', ave_speed=' + str(average_speed)[0:5] +
                      ', min_sep=' + str(min_sep)[0:5] +
                      ', ave_sep=' + str(ave_sep)[0:5] +
                      ', max_nn_dist=' + str(max_nn_dist)[0:5] +
                      ', cumulative_sep_fail/boid=' +
                          (str(self.cumulative_sep_fail / len(self.boids)) +
                          '00')[0:5] +
                      ', avoid_fail=' + str(self.total_avoid_fail))

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
        Draw.vis.register_key_callback(ord(' '), Flock.toggle_paused_mode)
        Draw.vis.register_key_callback(ord('1'), Flock.set_single_step_mode)
        Draw.vis.register_key_callback(ord('S'), Flock.select_next_boid)
        Draw.vis.register_key_callback(ord('A'), Flock.toggle_annotation)
        Draw.vis.register_key_callback(ord('C'), Flock.toggle_tracking_camera)
        Draw.vis.register_key_callback(ord('W'), Flock.toggle_wrap_vs_avoid)
        Draw.vis.register_key_callback(ord('E'), Flock.toggle_dynamic_erase)
        Draw.vis.register_key_callback(ord('F'), Flock.toggle_fixed_time_step)
        Draw.vis.register_key_callback(ord('B'), Flock.toggle_avoid_blend_mode)
        Draw.vis.register_key_callback(ord('H'), Flock.print_help)

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
        return (Draw.vis.poll_events() and
                Draw.frame_counter < self.max_simulation_steps)

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
#    Flock(400).run()                       # OK
#    Flock(400, 100).run()                  # OK
#    Flock(400, 100, Vec3(100, 0, 0)).run() # containment sphere still at origin
#
#    Flock(200, 60, Vec3(), 200).run()      # Test max_simulation_steps
#    Flock(max_simulation_steps=200, fixed_time_step=True, fixed_fps=30).run()
#    Flock(max_simulation_steps=200, fixed_time_step=True, seed=438538457).run()

    Flock().run()
#    Flock(2).run()
