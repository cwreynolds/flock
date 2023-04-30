import sys
import math
import numpy as np
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

# TODO 20230408 prototype flock top level
def run_flock(size, initial_diameter):
    setup()
    draw = Draw() ## ?? currently unused but should contain draw state
    Boid.add_boid_to_flock(size, initial_diameter)
    Boid.draw_flock()
    Draw.start_visualizer()
    while Draw.still_running():
        Boid.steer_flock(Draw.frame_duration)
        Boid.sphere_wrap_around_flock(sphere_diameter / 2) # this takes a radius
#        Boid.sphere_wrap_around_flock(sphere_diameter * 2) # this takes a radius
        Draw.clear_scene()
        Boid.draw_flock()
        Draw.update_scene()
        some_boid = Boid.flock[0]
        Draw.update_camera(some_boid.position.asarray())
        Boid.log_stats_for_flock()
    Draw.close_visualizer()

if __name__ == "__main__":
    Draw.test_animation_callback()
    
#     print([util.frandom2(0.6, 0.8) for i in range(3)])
#    run_flock(100, sphere_diameter)
#    run_flock(500, sphere_diameter)
#    run_flock(200, sphere_diameter)

#    Draw.expand_line_width_sample()
