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

# Flock top level.
def run_flock(size, diameter):
    radius = diameter / 2
    setup()
    draw = Draw() ## ?? currently unused but should contain draw state
    Draw.start_visualizer()
    Boid.add_boid_to_flock(size, radius)
    Boid.draw_flock()
    while Draw.still_running():
        if Draw.run_simulation_this_frame():
            Draw.clear_scene()
            Boid.steer_flock(Draw.frame_duration)
            Boid.sphere_wrap_around_flock(radius)
            Boid.draw_flock()
            Draw.update_scene()
            Boid.log_stats_for_flock()
    Draw.close_visualizer()

if __name__ == "__main__":
#    Draw.test_animation_callback()
#    Draw.expand_line_width_sample()

#    run_flock(50, sphere_diameter)
#    run_flock(100, sphere_diameter)
    run_flock(200, sphere_diameter)
#    run_flock(500, sphere_diameter)
