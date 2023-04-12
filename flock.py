import sys
import math
import numpy as np
import open3d as o3d
from Vec3 import Vec3
from Boid import Boid
from Draw import Draw
import Utilities as util
from LocalSpace import LocalSpace

def prolog():
    # versions
    print('Python', sys.version)
    print('Open3D', o3d.__version__)
    # Unit tests.
    assert Vec3.unit_test(), "Vec3 failed unit test."
    assert Boid.unit_test(), "Boid failed unit test."
    assert util.unit_test(), "util failed unit test."
    assert LocalSpace.unit_test(), "LocalSpace failed unit test."

# TODO 20230408 prototype flock top level
def run_flock(size, initial_diameter):
#    Draw.test_callback()
#    Draw.custom_draw_geometry_with_rotation(o3d.geometry.TriangleMesh.create_octahedron())

    prolog()
    draw = Draw() ## ?? currently unused but should contain draw state
    Boid.add_boid_to_flock(size, initial_diameter)
    Boid.draw_flock()
    Draw.start_visualizer()
    while Draw.still_running():
#        if Draw.frame_duration > 0:
#            print('fps =', int(1 / Draw.frame_duration))
#        Boid.steer_flock(1 / 60) # should measure time
        Boid.steer_flock(Draw.frame_duration)
        Draw.clear_scene()
        Boid.draw_flock()
        Draw.update_scene()
        some_boid = Boid.flock[0]
#        print('boid.speed =', some_boid.speed)
        Draw.update_camera(some_boid.position().asarray())
    Draw.close_visualizer()

if __name__ == "__main__":
    run_flock(100, 10) # 100 boids in a sphere of diameter 10
