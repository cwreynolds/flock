import sys
import open3d as o3d
from Vec3 import Vec3
from Boid import Boid
from Draw import Draw
from Agent import Agent
import Utilities as util
from LocalSpace import LocalSpace

# For initial placememnt and wrap-around.
sphere_diameter = 60

def setup():
    # Log versions.
    print('Python', sys.version)
    print('Open3D', o3d.__version__)
    # Run unit tests.
    Vec3.unit_test()
    LocalSpace.unit_test()
    Agent.unit_test()
    util.unit_test()
    print('All unit tests OK.')

def draw_global_axes():
    size = 10
    sides = 8
    radius = 0.05
    black = Vec3()
    x = Vec3(size, 0, 0)
    y = Vec3(0, size, 0)
    z = Vec3(0, 0, size)
    move = Boid.camera_aim_boid_draw_offset_qqq()
    Draw.add_line_segment(-x - move, x - move, black, radius, sides)
    Draw.add_line_segment(-y - move, y - move, black, radius, sides)
    Draw.add_line_segment(-z - move, z - move, black, radius, sides)

# TODO 20230408 prototype flock top level
def run_flock(size, initial_diameter):
    setup()
    draw = Draw() ## ?? currently unused but should contain draw state
    Boid.add_boid_to_flock(size, initial_diameter)
    Boid.draw_flock()
    draw_global_axes()
    Draw.start_visualizer()
    while Draw.still_running():
        if Draw.run_simulation_this_frame():
            Boid.steer_flock(Draw.frame_duration)
            Boid.sphere_wrap_around_flock(sphere_diameter / 2) # takes radius
        Draw.clear_scene()
        Boid.draw_flock()
        draw_global_axes()
        Draw.update_scene()
        some_boid = Boid.flock[0]
        Draw.update_camera(some_boid.position.asarray())
        Boid.log_stats_for_flock()
    Draw.close_visualizer()

if __name__ == "__main__":
#    Draw.test_animation_callback()
#    Draw.expand_line_width_sample()

    run_flock(100, sphere_diameter)
#    run_flock(500, sphere_diameter)
#    run_flock(200, sphere_diameter)
#    run_flock(50, sphere_diameter)
