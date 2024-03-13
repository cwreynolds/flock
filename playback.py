#-------------------------------------------------------------------------------
#
# playback.py -- new flock experiments
#
# Utility for visualizing flock simulation computed on c++ side.
# Reads a .py file containing the results of a flock simulation in c++.
#
# Usage:
#     python playback.py ~/Desktop/boid_centers.py
#
# MIT License -- Copyright © 2024 Craig Reynolds
#
#-------------------------------------------------------------------------------

from Vec3 import Vec3
from Draw import Draw
from flock import Flock
from obstacle import EvertedSphereObstacle
from obstacle import CylinderObstacle
import Utilities as util
import open3d as o3d
import time


# Simple animated version:

def draw(boid_centers):
    time_step = 1/ 30  # This should be in the flock data file.
    flock = Flock()
    draw = Draw() ## ?? currently unused but should contain draw state
    Draw.start_visualizer(50, Vec3())
    flock.register_single_key_commands() # For Open3D visualizer GUI.
    Draw.clear_scene()
    add_obstacles_to_scene()
    boid_meshes = add_boids_to_scene(boid_centers[0])
    Draw.update_scene()
    while flock.still_running():
        print('Begin playback')
        step_index = 0
        while flock.still_running() and (step_index < len(boid_centers)):
            update_boids_in_scene(boid_centers[step_index], boid_meshes)
            step_index += 1
            time.sleep(time_step)
    Draw.close_visualizer()

def add_boids_to_scene(boid_centers_this_step):
    boid_meshes = []
    for xyz in boid_centers_this_step:
        center = Vec3.from_array(xyz)
        color = Vec3.from_array([util.frandom2(0.4, 0.6) for i in range(3)])
        mesh = Draw.add_ball(0.5, center, color, shaded=False, reset_bounding_box=False)
        boid_meshes.append(mesh)
    return boid_meshes

def update_boids_in_scene(boid_centers_this_step, boid_meshes):
    assert len(boid_centers_this_step) == len(boid_meshes)
    for i in range(len(boid_meshes)):
        boid_meshes[i].translate(boid_centers_this_step[i], relative=False)
        Draw.vis.update_geometry(boid_meshes[i])

def add_obstacles_to_scene():
    # For now: draw the default "evoflock" obstacles.
    r = 50      # sphere_radius
    c = Vec3()  # sphere center
    sphere = EvertedSphereObstacle(r, c)
    sphere.draw()
    Draw.vis.add_geometry(sphere.tri_mesh, False)
    cylinder = CylinderObstacle(r * 0.2,
                                c + Vec3(r * 0.6, r, 0),
                                c + Vec3(r * 0.6, -r, 0))
    cylinder.draw()
    Draw.vis.add_geometry(cylinder.tri_mesh, False)

################################################################################
#
# Spacetime worm version:
#
#    def draw():
#        flock = Flock()
#        draw = Draw() ## ?? currently unused but should contain draw state
#        Draw.start_visualizer(50, Vec3())
#        flock.register_single_key_commands() # For Open3D visualizer GUI.
#        Draw.clear_scene()
#        draw_all_boids_for_all_steps(boid_centers)
#        Draw.update_scene()
#        while flock.still_running():
#            time.sleep(0.01)
#        Draw.close_visualizer()
#
#    saturated_colors = [Vec3(1.0, 0.0, 0.0),
#                        Vec3(1.0, 1.0, 0.0),
#                        Vec3(0.0, 1.0, 0.0),
#                        Vec3(0.0, 1.0, 1.0),
#                        Vec3(0.0, 0.0, 1.0),
#                        Vec3(1.0, 0.0, 1.0)]
#
#    def draw_all_boids_for_all_steps(boid_centers_per_step):
#        ball_count = 0 #############################################################
#        counter = 0
#        step_count = len(boid_centers_per_step)
#        gray = Vec3(1, 1, 1)
#        for step in boid_centers_per_step:
#            counter += 1
#            relative_time = counter / step_count
#            if (counter % 5) == 0:
#                color_index = 0
#                for xyz in step:
#                    center = Vec3.from_array(xyz)
#                    sci = color_index % len(saturated_colors)
#                    color = util.interpolate(relative_time, gray, saturated_colors[sci])
#                    color_index += 1
#                    Draw.add_ball(0.5, center, color, shaded=False)
#                    ball_count += 1    #############################################
#                    print(ball_count)  #############################################
################################################################################


if __name__ == "__main__":
    import argparse
    import importlib.util
    import sys

    # Get pathname for flock data file from command line.
    path = ''
    parser = argparse.ArgumentParser(description='Playback flock data file.')
    parser.add_argument('path', type=str, default=path, const=path, nargs='?',
                        help='pathname of flock data file.')
    args = parser.parse_args()
    path = args.path
    
    if path == '':
        print('    Expecting a pathname on the command line.')
    else:
        # Load data file from given pathname.
        # (Use method described at: https://stackoverflow.com/a/67692/1991373)
        spec = importlib.util.spec_from_file_location("boid_centers", path)
        boid_centers = importlib.util.module_from_spec(spec)
        sys.modules["module.name"] = boid_centers
        spec.loader.exec_module(boid_centers)

        # Run playback.
        draw(boid_centers.boid_centers)
