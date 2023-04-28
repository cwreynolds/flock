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


class Draw:
    """Graphics utilities based on Open3D."""

    # Initialize new instance.
    def __init__(self):
        self.temp = 0

    # Class properties to hold raw scene data for Open3D TriangleMesh.
#    mesh_vertex_count = 0
    mesh_vertices = o3d.utility.Vector3dVector()
    mesh_triangles = o3d.utility.Vector3iVector()
    mesh_vertex_colors = o3d.utility.Vector3dVector()
    
    ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ##
    # TODO 20230426 add line drawing support for annotation
#    line_vertex_count = 0
    line_points = o3d.utility.Vector3dVector()
    line_segments = o3d.utility.Vector2iVector()
    line_colors = o3d.utility.Vector3dVector()
    ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ##

    # class storage of current visualizer
    vis = None
    frame_start_time = None
    frame_duration = 0.01
    
    @staticmethod
    def add_triangle_single_color(v1, v2, v3, color):
        color = color.asarray()
        for v in [v1, v2, v3]:
            Draw.mesh_vertices.append(v.asarray())
            Draw.mesh_vertex_colors.append(color)
        t = len(Draw.mesh_triangles) * 3
        Draw.mesh_triangles.append([t, t + 1, t + 2])

    ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ##
    # TODO 20230426 add line drawing support for annotation
    @staticmethod
    def add_line_segment(v1, v2, color1=None, color2=None):
        if color1 == None:
#            color1 = Vec3(0.5, 0.5, 0.5)
            color1 = Vec3(1, 0, 0)
        if color2 == None:
            color2 = color1
        Draw.line_points.append(v1.asarray())
        Draw.line_points.append(v2.asarray())
        # TODO 20230427 may actually be just one color per line segment (see
        # http://www.open3d.org/docs/release/python_example/visualization/index.html#line-width-py )
        Draw.line_colors.append(color1.asarray())
        Draw.line_colors.append(color2.asarray())
        
#        print(Draw.line_colors.asarray())
#        print(color1,color2)
        
        i = len(Draw.line_segments) * 2
        Draw.line_segments.append([i, i + 1])
    ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ##

    @staticmethod
    def start_visualizer():
        # Create a mesh from the triangle vertices and indices
        Draw.triangle_mesh = o3d.geometry.TriangleMesh()
        Draw.triangle_mesh.vertices = Draw.mesh_vertices
        Draw.triangle_mesh.triangles = Draw.mesh_triangles
        Draw.triangle_mesh.vertex_colors = Draw.mesh_vertex_colors
        
        ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ##
        # TODO 20230426 add line drawing support for annotation
        Draw.line_set = o3d.geometry.LineSet()
        Draw.line_set.points = Draw.line_points
        Draw.line_set.lines = Draw.line_segments
        Draw.line_set.colors = Draw.line_colors
        
#            # TODO 20230427 try to use "tensor version" (o3d.t) of LineSet.
#            device = None
#    #        device = o3d.core.Device.DeviceType.CPU
#    #        device = o3d.cpu
#            dtype_f = o3d.core.float32
#            dtype_i = o3d.core.int32
#
#    #        Draw.t_line_set = o3d.t.geometry.LineSet(device)
#    #        position_tensor = o3d.core.Tensor(Draw.line_points, dtype_f, device)
#    #        Draw.t_line_set.point.positions = position_tensor
#    #        line_index_tensor = o3d.core.Tensor(Draw.line_segments, dtype_f, device)
#    #        Draw.t_line_set.line.indices = line_index_tensor
#    #        line_color_tensor = o3d.core.Tensor(Draw.line_colors, dtype_f, device)
#    #        Draw.t_line_set.line.colors = line_color_tensor
#
#            Draw.t_line_set = o3d.t.geometry.LineSet()
#            position_tensor = o3d.core.Tensor(Draw.line_points, dtype_f)
#            Draw.t_line_set.point.positions = position_tensor
#            line_index_tensor = o3d.core.Tensor(Draw.line_segments, dtype_f)
#            Draw.t_line_set.line.indices = line_index_tensor
#            line_color_tensor = o3d.core.Tensor(Draw.line_colors, dtype_f)
#            Draw.t_line_set.line.colors = line_color_tensor

        
        
#        # TODO 20230427 add "material" for line drawing
#        print(dir(Draw.line_set))
        mat = o3d.visualization.rendering.MaterialRecord()
        mat.shader = "unlitLine"
        mat.line_width = 10  # note that this is scaled with respect to pixels,
#        Draw.line_set.material = mat
        
        Draw.line_set.paint_uniform_color(Vec3(1, 0, 0).asarray())

        
        ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ##
        
        # Create Visualizer add mesh, enter draw loop.
        Draw.vis = o3d.visualization.Visualizer()
        Draw.vis.create_window()
        Draw.vis.add_geometry(Draw.triangle_mesh)
        ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ##
        # TODO 20230426 add line drawing support for annotation
        Draw.vis.add_geometry(Draw.line_set)
#        Draw.vis.add_geometry({
#                                "name": "lines",
#                                "geometry": Draw.line_set,
#                                "material": mat
#                              })
        
        # TODO 20230427 try to use "tensor version" (o3d.t) of LineSet.
#        Draw.vis.add_geometry(Draw.t_line_set)
        ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ##
        
        # TODO 23230411 temp ball for camera aim reference
        ball = o3d.geometry.TriangleMesh.create_sphere(0.1, 10)
        ball.compute_vertex_normals()
        ball.paint_uniform_color([0.8, 0.1, 0.1])
        Draw.vis.add_geometry(ball)

        Draw.frame_start_time = time.time()

        
    @staticmethod
    def close_visualizer():
        Draw.vis.destroy_window()

    @staticmethod
    def still_running():
        return Draw.vis.poll_events()

    @staticmethod
    def clear_scene():
#        Draw.mesh_vertex_count = 0
        Draw.mesh_vertices.clear()
        Draw.mesh_triangles.clear()
        Draw.mesh_vertex_colors.clear()
        
        ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ##
        # TODO 20230426 add line drawing support for annotation
        Draw.line_points.clear()
        Draw.line_segments.clear()
        Draw.line_colors.clear()
        ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ##


    @staticmethod
    def update_scene():
        Draw.triangle_mesh.vertices = Draw.mesh_vertices
        Draw.triangle_mesh.triangles = Draw.mesh_triangles
        Draw.vis.update_geometry(Draw.triangle_mesh)

        ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ##
        # TODO 20230426 add line drawing support for annotation
        Draw.line_set.points = Draw.line_points
        Draw.line_set.lines = Draw.line_segments
        Draw.line_set.colors = Draw.line_colors
        Draw.vis.update_geometry(Draw.line_set)
        ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ##

        Draw.vis.update_renderer()
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
    
    
    ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ##
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



#import open3d as o3d
#import random
#
#NUM_LINES = 10
#
#
#def random_point():
#    return [5 * random.random(), 5 * random.random(), 5 * random.random()]
#
#
#def main():
#    pts = [random_point() for _ in range(0, 2 * NUM_LINES)]
#    line_indices = [[2 * i, 2 * i + 1] for i in range(0, NUM_LINES)]
##    colors = [[0.0, 0.0, 0.0] for _ in range(0, NUM_LINES)]
#    colors = [[random.random(), random.random(), random.random()]
#              for _ in range(0, NUM_LINES)]
#
#    lines = o3d.geometry.LineSet()
#    lines.points = o3d.utility.Vector3dVector(pts)
#    lines.lines = o3d.utility.Vector2iVector(line_indices)
#    # The default color of the lines is white, which will be invisible on the
#    # default white background. So we either need to set the color of the lines
#    # or the base_color of the material.
#    lines.colors = o3d.utility.Vector3dVector(colors)
#
#    # Some platforms do not require OpenGL implementations to support wide lines,
#    # so the renderer requires a custom shader to implement this: "unlitLine".
#    # The line_width field is only used by this shader; all other shaders ignore
#    # it.
#    mat = o3d.visualization.rendering.MaterialRecord()
#    mat.shader = "unlitLine"
##    mat.line_width = 10  # note that this is scaled with respect to pixels,
#    mat.line_width = 3  # note that this is scaled with respect to pixels,
#    # so will give different results depending on the
#    # scaling values of your system
#    o3d.visualization.draw({
#        "name": "lines",
#        "geometry": lines,
#        "material": mat
#    })
#
#
#if __name__ == "__main__":
#    main()





    # Attempting to run inside modern o3d.visualization.draw()
    # while running flock simulation via callbacks.
    
    # references
    # https://github.com/isl-org/Open3D/blob/master/python/open3d/visualization/draw.py
    # https://github.com/isl-org/Open3D/blob/master/cpp/open3d/visualization/visualizer/O3DVisualizer.cpp
    # https://github.com/isl-org/Open3D/blob/88693971ae7a7c3df27546ff7c5b1d91188e39cf/cpp/open3d/visualization/visualizer/O3DVisualizer.cpp
    
    
    
    def test_callback():
        mesh = o3d.geometry.TriangleMesh.create_octahedron()
        Draw.custom_draw_geometry_with_rotation(mesh)

#        # Test animation callback.
#        def test_animation_callback():
#            mesh = o3d.geometry.TriangleMesh.create_octahedron()
#            def recolor(vis):
#                mesh.paint_uniform_color(np.random.rand(3))
#                vis.update_geometry(mesh)
#                return False
#            o3d.visualization.draw_geometries_with_animation_callback([mesh], recolor)
#    #        o3d.visualization.draw([mesh], on_animation_frame=recolor)
#    #        o3d.visualization.draw([mesh], on_animation_tick=recolor)

    # Test animation callback.
    def test_animation_callback():
#        mesh = o3d.geometry.TriangleMesh.create_octahedron()
        mesh = o3d.t.geometry.TriangleMesh.create_octahedron()
        
        
#            def cb_test(vis):
#                print('in cb_test')
#    #            return False
#    #            return True

        def cb_test(vis, value):
            
#            print(mesh.vertex.colors)
#
#            mesh.paint_uniform_color(np.random.rand(3))
            
            mesh.translate(np.random.rand(3))
            
            
#            vis.update_geometry(mesh)
            vis.update_geometry('wot', mesh, int(value))

            print('in cb_test, value =', value)

#        o3d.visualization.draw_geometries_with_animation_callback([mesh], cb_test)
#        o3d.visualization.draw([mesh], on_animation_frame=cb_test)
#        o3d.visualization.draw([mesh], on_animation_tick=cb_test)


        # TODO Really would be nice to have “always animating” mode. No need to
        # specify fictitious animation_time_step and animation_duration. No need
        # to open UI and click run.

        o3d.visualization.draw([mesh],
                               on_animation_frame=cb_test,
#                               animation_time_step=1.0,
                               animation_time_step = 1 / 20,
                               animation_duration=1000000000,
                               show_ui=True,
                               )




    ##
    ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ##
