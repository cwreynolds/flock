import math
import numpy as np
#import open3d as o3d
from Vec3 import Vec3
from Boid import Boid
from Draw import Draw
from LocalSpace import LocalSpace
import Utilities as util

#
#    mesh_vertices = o3d.utility.Vector3dVector()
#    mesh_triangles = o3d.utility.Vector3iVector()
#    mesh_vertex_count = 0
#
#    mesh_vertex_colors = o3d.utility.Vector3dVector()
#
#    #def interpolate(alpha, p, q):
#    #    return (p * (1 - alpha)) + (q * alpha)
#    #
#    #    def frandom01():
#    #        return np.random.uniform(0, 1)
#    #
#    #    def frandom2(a, b):
#    #        return interpolate(frandom01(), a, b)
#
#    def add_random_triangle():
#        pos_scale = 50
#        add_triangle([pos_scale * util.frandom01(),
#                      pos_scale * util.frandom01(),
#                      0], None)
#
#    def add_triangle(position, orientation):
#        xyz = np.array([position[0], position[1], position[2]])
#        
#        v = np.array([1, 0, 0])
#        a = util.frandom01() * math.pi * 2
#        color = [util.frandom2(0.4, 0.6),
#                 util.frandom2(0.4, 0.6),
#                 util.frandom2(0.4, 0.6)]
#        
#        for i in range(3):
#            a += math.pi * 2 / 3
#            v = np.array(rotate_xy_about_z(v, a))
#            rp = xyz + np.array(v)
#            mesh_vertices.append(rp)
#            mesh_vertex_colors.append(color)
#
#        t = len(mesh_triangles) * 3
#        mesh_triangles.append([t, t + 1, t + 2])
#
#    def rotate_xy_about_z(vec3, angle):
#        s = math.sin(angle)
#        c = math.cos(angle)
#        x = vec3[0]
#        y = vec3[1]
#        z = vec3[2]
#        return [(x * c + y * s), y * c - x * s, z]
#
#    def test():
#        for i in range(200):
#            add_random_triangle()
#
#        # Create a mesh from the triangle vertices and indices
#        triangle_mesh = o3d.geometry.TriangleMesh()
#        triangle_mesh.vertices = mesh_vertices
#        triangle_mesh.triangles = mesh_triangles
#        triangle_mesh.vertex_colors = mesh_vertex_colors
#
#        vis = o3d.visualization.Visualizer()
#        vis.create_window()
#        vis.add_geometry(triangle_mesh)
#        
#        rot_z_angle = 0
#        for i in range(400):
#            triangle_mesh.vertices = mesh_vertices
#            triangle_mesh.triangles = mesh_triangles
#            rot_z_angle += 0.008
#            rot = triangle_mesh.get_rotation_matrix_from_xyz((0, 0, rot_z_angle))
#            triangle_mesh.rotate(rot, center=(0, 0, 0))
#            triangle_mesh.compute_vertex_normals() ## ???
#            vis.update_geometry(triangle_mesh)
#            vis.poll_events()
#            vis.update_renderer()
#        vis.destroy_window()
#
#    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#
#    # Trying to test per-triangle colors as claimed to exist on:
#    # https://github.com/isl-org/Open3D/issues/1087#issuecomment-1222782733
#
#    def face_color_test():
#        mesh = o3d.geometry.TriangleMesh.create_octahedron()
#        rgb = [[0,0,0],[0,0,1],[0,1,0],[0,1,1],[1,0,0],[1,0,1],[1,1,0],[1,1,1]]
#        # face_colors = o3d.utility.Vector3dVector(np.array(rgb, np.float32))
#        face_colors = o3d.utility.Vector3iVector(np.array(rgb, np.int32))
#        mesh.triangles["colors"] = face_colors
#        vis = o3d.visualization.Visualizer()
#        vis.create_window()
#        vis.add_geometry(mesh)
#        vis.run()
#        vis.destroy_window()
#
#    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# TODO 20230408 prototype flock top level

#    def run_flock(size, initial_diameter):
#
#        flock = []
#        r = initial_diameter / 2  # radius of random position spread
#        for i in range(size):
#            boid = Boid()
#    #        boid.ls.p = Vec3(spread * frandom01(), 0, spread * frandom01())
#            boid.ls.p = Vec3(util.frandom2(-r, r), 0, util.frandom2(-r, r))
#
#            boid.wander_steer(None)
#
#            flock.append(boid)
#
#    #    draw = Draw()


def run_flock(size, initial_diameter):
    draw = Draw()
    Boid.add_boid_to_flock(size, initial_diameter)
#    Draw.test()
#    Draw.face_color_test()
    Draw.test()


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

import sys

if __name__ == "__main__":
#    print('Python version =', sys.version)
#    print('o3d.__version__ =', o3d.__version__)

#    for i in range(50):
#        print(frandom01())

#    print('[1, 2, 3] + [10, 20, 30]', [1, 2, 3] + [10, 20, 30])
    
#        rp = xyz + np.array([frandom01(), frandom01(), 0])

#    print('np.array([1, 2, 3]) + np.array([10, 20, 30])',
#          np.array([1, 2, 3]) + np.array([10, 20, 30]))
    
#    test()

#    face_color_test()

    print('Vec3.unit_test() =', Vec3.unit_test())
    
#    print('LocalSpace() =', LocalSpace())
    print('LocalSpace.unit_test() =', LocalSpace.unit_test())

#    print('Agent.unit_test() =', Agent.unit_test())
    print('Boid.unit_test() =', Boid.unit_test())

    print('util.unit_test() =', util.unit_test())

#    run_flock(10, 10) # 10 boids in a 10x10 area
    
#    seed = 0
#    for i in range(50):
#        print('util.rehash32bits(seed)', seed := util.rehash32bits(seed))

#    Draw.add_triangle_single_color(Vec3(1, 0, 0),
#                                   Vec3(0, 1, 0),
#                                   Vec3(0, 0, 1),
#                                   Vec3(1, 1, 1))
#
#    Boid.draw_test()

    run_flock(100, 10) # 10 boids in a 10x10 area

    
    
