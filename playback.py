#-------------------------------------------------------------------------------
#
# playback.py -- new flock experiments
#
# VERY WIP PROTOTYPE
# Utility for visualizing flock simulation computed on c++ side.
#
# Reads a .py file containing the results of a flock simulation in c++.
#
# MIT License -- Copyright © 2024 Craig Reynolds
#
#-------------------------------------------------------------------------------

from boid_centers import boid_centers

from Vec3 import Vec3
from Draw import Draw
from flock import Flock
import Utilities as util
import open3d as o3d
import time

#print(boid_centers)

#    counter = 0
#    for step in boid_centers:
#        print()
#        print(counter)
#        counter += 1
#        for center in step:
#            print(center)

# For ideas about how to do this, perhaps with more flexibility see:
#
# How to call a script from another script?
# https://stackoverflow.com/q/1186789/1991373
#
# Also "Read .py file variables in another python file using the filepath"
# https://stackoverflow.com/q/66849437/1991373
#
# "How can I import a module dynamically given the full path?"
# https://stackoverflow.com/q/67631/1991373
# esp the first answer: https://stackoverflow.com/a/67692/1991373


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



# Simple animated version:

def draw(boid_centers):
    time_step = 1/ 30  # This should be in the flock data file.
    flock = Flock()
    draw = Draw() ## ?? currently unused but should contain draw state
    Draw.start_visualizer(50, Vec3())
    flock.register_single_key_commands() # For Open3D visualizer GUI.
    Draw.clear_scene()
    boid_meshes = add_boids_to_scene(boid_centers[0])
    Draw.update_scene()
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
        mesh = Draw.add_ball(0.5, center, color, shaded=False)
        boid_meshes.append(mesh)
    return boid_meshes

def update_boids_in_scene(boid_centers_this_step, boid_meshes):
    assert len(boid_centers_this_step) == len(boid_meshes)
    for i in range(len(boid_meshes)):
        boid_meshes[i].translate(boid_centers_this_step[i], relative=False)
        Draw.vis.update_geometry(boid_meshes[i])


if __name__ == "__main__":
    draw(boid_centers)
