#-------------------------------------------------------------------------------
#
# Draw.py -- new flock experiments
#
# Graphics utilities based on Open3D
#
# MIT License -- Copyright © 2023 Craig Reynolds
#
#-------------------------------------------------------------------------------

import open3d as o3d
import numpy as np # temp?
import time
import math
import Utilities as util  # temp?
from Vec3 import Vec3     # temp?
import random             # temp?
from LocalSpace import LocalSpace


class Draw:
    """Graphics utilities based on Open3D."""

    # Initialize new instance.
    def __init__(self):
        self.temp = 0

    # Class properties to hold raw scene data for Open3D TriangleMesh.
    mesh_vertices = o3d.utility.Vector3dVector()
    mesh_triangles = o3d.utility.Vector3iVector()
    mesh_vertex_colors = o3d.utility.Vector3dVector()
    
    # class storage of current visualizer
    vis = None
    frame_start_time = None
    frame_duration = 0.01
    
    @staticmethod
    def add_triangle_single_color(v1, v2, v3, color):
        for v in [v1, v2, v3]:
            Draw.mesh_vertices.append(v.asarray())
            Draw.mesh_vertex_colors.append(color.asarray())
        t = len(Draw.mesh_triangles) * 3
        Draw.mesh_triangles.append([t, t + 1, t + 2])

    # TODO 20230430 line drawing support for annotation
    # given all the problems getting LineSets to draw in bright unshaded colors,
    # trying this approach drawing lines as several triangles.
    # TODO 20230426 add line drawing support for annotation
    @staticmethod
    def add_line_segment(v1, v2, color=Vec3(), radius = 0.01, sides = 3):
        # Vector along the segment, from v1 to v2
        offset = v2 - v1
        distance = offset.length()
        if distance > 0:
            tangent = offset / distance
            basis1 = tangent.find_perpendicular()
            basis2 = tangent.cross(basis1)
            # Make transform from "line segment space" to global space.
            ls = LocalSpace(basis1, basis2, tangent, v1)
            for i in range(sides):
                angle_step = math.pi * 2 / sides
                radial = Vec3(radius, 0, 0)
                a = ls.globalize(radial.rotate_xy_about_z(angle_step * i))
                b = ls.globalize(radial.rotate_xy_about_z(angle_step * (i+1)))
                c = b + offset
                d = a + offset
                Draw.draw_quadrilateral(d, c, b, a, color)

    # Draw quadrilateral as 2 tris. Assumes planar and convex but does not care.
    @staticmethod
    def draw_quadrilateral(v1, v2, v3, v4, color=Vec3()):
        Draw.add_triangle_single_color(v1, v2, v3, color)
        Draw.add_triangle_single_color(v1, v3, v4, color)

    @staticmethod
    def start_visualizer():
        # Create a mesh from the triangle vertices and indices
        Draw.triangle_mesh = o3d.geometry.TriangleMesh()
        Draw.triangle_mesh.vertices = Draw.mesh_vertices
        Draw.triangle_mesh.triangles = Draw.mesh_triangles
        Draw.triangle_mesh.vertex_colors = Draw.mesh_vertex_colors
                
        # Create Visualizer add mesh, enter draw loop.
        Draw.vis = o3d.visualization.Visualizer()
        Draw.vis.create_window()
        
        # Add (then remove) sphere to init view. aim_radius controls distance.
        aim_radius = 20
        aim_ball = o3d.geometry.TriangleMesh.create_sphere(aim_radius, 10)
        Draw.vis.add_geometry(aim_ball)
        Draw.vis.remove_geometry(aim_ball, False)

        # Add the flock's TriangleMesh to the scene.
        Draw.vis.add_geometry(Draw.triangle_mesh, False)
        
        # TODO 23230411 temp ball for camera aim reference
        ball = o3d.geometry.TriangleMesh.create_sphere(0.1, 10)
        ball.compute_vertex_normals()
        ball.paint_uniform_color([0.1, 0.1, 0.1])
        Draw.vis.add_geometry(ball, False)

        Draw.frame_start_time = time.time()

    @staticmethod
    def close_visualizer():
        Draw.vis.destroy_window()

    @staticmethod
    def still_running():
        return Draw.vis.poll_events()

    @staticmethod
    def clear_scene():
        Draw.mesh_vertices.clear()
        Draw.mesh_triangles.clear()
        Draw.mesh_vertex_colors.clear()

    # Update scene geometry.
    # In this application, all geometry is regenerated anew every frame.
    @staticmethod
    def update_scene():
        # Copy new simulation data into TriangleMesh object.
        Draw.triangle_mesh.vertices = Draw.mesh_vertices
        Draw.triangle_mesh.triangles = Draw.mesh_triangles
        Draw.triangle_mesh.vertex_colors = Draw.mesh_vertex_colors
        Draw.vis.update_geometry(Draw.triangle_mesh)
        
        # I'm not sure why this is unneeded. Maybe new geometry implies it?
        # Draw.vis.update_renderer()
        
        # Measure frame duration:
        frame_end_time = time.time()
        Draw.frame_duration = frame_end_time - Draw.frame_start_time
        Draw.frame_start_time = frame_end_time
        Draw.frame_counter += 1

    # TODO 20230419 but does not work because "Visualizer.get_view_control()
    #               gives a copy." https://github.com/isl-org/Open3D/issues/6009
    @staticmethod
    def update_camera(lookat):
        camera = Draw.vis.get_view_control()
        camera.set_lookat(lookat)

    # Frame counter
    frame_counter = 0
    
################################################################################
##
## TODO 20230419 random test code, to be removed eventually.

    # TODO 20230401
    # Trying to test per-triangle colors as claimed to exist on:
    # https://github.com/isl-org/Open3D/issues/1087#issuecomment-1222782733
    # See my questions on:
    # https://stackoverflow.com/questions/75907926/open3d-color-per-triangle
    # https://github.com/isl-org/Open3D/issues/6060
    def face_color_test():
        mesh = o3d.geometry.TriangleMesh.create_octahedron()
        rgb = [[0,0,0],[0,0,1],[0,1,0],[0,1,1],[1,0,0],[1,0,1],[1,1,0],[1,1,1]]
        # face_colors = o3d.utility.Vector3dVector(np.array(rgb, np.float32))
        face_colors = o3d.utility.Vector3iVector(np.array(rgb, np.int32))
        # mesh.triangles["colors"] = face_colors
        vis = o3d.visualization.Visualizer()
        vis.create_window()
        vis.add_geometry(mesh)
        vis.run()
        vis.destroy_window()

    # TODO 20230412, cannot set any view parameters because “get_view_control()
    # gives a copy” (https://github.com/isl-org/Open3D/issues/6009). So this
    # example (from https://github.com/isl-org/Open3D/blob/master/examples/python/visualization/customized_visualization.py#L39):
    def custom_draw_geometry_with_rotation(pcd):
        def rotate_view(vis):
            ctr = vis.get_view_control()
            ctr.rotate(10.0, 0.0)
            return False
        o3d.visualization.draw_geometries_with_animation_callback([pcd],
                                                                  rotate_view)

    # Attempting to run inside modern o3d.visualization.draw()
    # while running flock simulation via callbacks.
    
    # references
    # https://github.com/isl-org/Open3D/blob/master/python/open3d/visualization/draw.py
    # https://github.com/isl-org/Open3D/blob/master/cpp/open3d/visualization/visualizer/O3DVisualizer.cpp
    
    def test_callback():
        mesh = o3d.geometry.TriangleMesh.create_octahedron()
        Draw.custom_draw_geometry_with_rotation(mesh)


    # Test animation callback.
    # Used as sample code for https://github.com/isl-org/Open3D/issues/6094
    def test_animation_callback():
        oct = o3d.geometry.TriangleMesh.create_octahedron()
        def cb_test(vis, time):
            print('in cb_test, time =', time)
            oct.paint_uniform_color(np.random.rand(3))
            vis.remove_geometry('oct')
            vis.add_geometry('oct', oct)
        o3d.visualization.draw({'name': 'oct', 'geometry': oct},
                               on_animation_frame = cb_test,
                               animation_time_step = 1 / 60,
                               animation_duration = 1000000,
                               show_ui=True)



    # expand line_width.py sample code: http://www.open3d.org/docs/release/python_example/visualization/index.html#line-width-py
    def expand_line_width_sample():
        NUM_LINES = 10
        def random_point():
            return [5 * random.random(), 5 * random.random(), 5 * random.random()]
        pts = [random_point() for _ in range(0, 2 * NUM_LINES)]
        line_indices = [[2 * i, 2 * i + 1] for i in range(0, NUM_LINES)]
    #    colors = [[0.0, 0.0, 0.0] for _ in range(0, NUM_LINES)]
        colors = [[random.random(), random.random(), random.random()]
                  for _ in range(0, NUM_LINES)]

        lines = o3d.geometry.LineSet()
        lines.points = o3d.utility.Vector3dVector(pts)
        lines.lines = o3d.utility.Vector2iVector(line_indices)
        # The default color of the lines is white, which will be invisible on the
        # default white background. So we either need to set the color of the lines
        # or the base_color of the material.
        lines.colors = o3d.utility.Vector3dVector(colors)

        # Some platforms do not require OpenGL implementations to support wide lines,
        # so the renderer requires a custom shader to implement this: "unlitLine".
        # The line_width field is only used by this shader; all other shaders ignore
        # it.
        mat = o3d.visualization.rendering.MaterialRecord()
        mat.shader = "unlitLine"
    #    mat.line_width = 10  # note that this is scaled with respect to pixels,
        mat.line_width = 3  # note that this is scaled with respect to pixels,
        # so will give different results depending on the
        # scaling values of your system
        
        def cb_test(vis, value):
            print('in cb_test, value =', value)
            # vis.update_geometry(lines)
            # vis.clear_geometries()
            # vis.add_geometry(lines)
            vis.add_geometry(lines)
            return True

        o3d.visualization.draw({"name": "lines",
                                "geometry": lines,
                                "material": mat},
                               on_animation_frame=cb_test,
                               animation_time_step = 1 / 30,
                               animation_duration=1000000000,
                               show_ui=True,
                              )

##
## TODO 20230419 random test code, to be removed eventually.
################################################################################
