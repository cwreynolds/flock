#-------------------------------------------------------------------------------
#
# Draw.py -- new flock experiments
#
# Graphics utilities based on Open3D
#
# MIT License -- Copyright © 2023 Craig Reynolds
#
#-------------------------------------------------------------------------------

import numpy as np # temp?

import open3d as o3d

class Draw:
    """Graphics utilities based on Open3D."""

    # Initialize new instance.
    def __init__(self):
        self.temp = 0

    # Class properties to hold raw scene data for Open3D TriangleMesh.
    mesh_vertex_count = 0
    mesh_vertices = o3d.utility.Vector3dVector()
    mesh_triangles = o3d.utility.Vector3iVector()
    mesh_vertex_colors = o3d.utility.Vector3dVector()
    
#    #    def add_triangle(position, orientation):
#        def add_triangle_single_color(v1, v2, v3, color):
#    #        xyz = np.array([position[0], position[1], position[2]])
#    #
#    #        v = np.array([1, 0, 0])
#    #        a = util.frandom01() * math.pi * 2
#    #        color = [util.frandom2(0.4, 0.6),
#    #                 util.frandom2(0.4, 0.6),
#    #                 util.frandom2(0.4, 0.6)]
#
#    #        for i in range(3):
#    #            a += math.pi * 2 / 3
#    #            v = np.array(rotate_xy_about_z(v, a))
#    #            rp = xyz + np.array(v)
#    #            mesh_vertices.append(rp)
#    #            mesh_vertex_colors.append(color)
#
#            for v in [v1, v2, v3]:
#                mesh_vertices.append(v)
#                mesh_vertex_colors.append(color)
#
#            t = len(mesh_triangles) * 3
#            mesh_triangles.append([t, t + 1, t + 2])

    @staticmethod
    def add_triangle_single_color(v1, v2, v3, color):
        color = color.asarray()
        for v in [v1, v2, v3]:
            Draw.mesh_vertices.append(v.asarray())
            Draw.mesh_vertex_colors.append(color)
        t = len(Draw.mesh_triangles) * 3
        Draw.mesh_triangles.append([t, t + 1, t + 2])

    @staticmethod
    def test():
#        for i in range(200):
#            add_random_triangle()


        # Create a mesh from the triangle vertices and indices
        Draw.triangle_mesh = o3d.geometry.TriangleMesh()
        Draw.triangle_mesh.vertices = Draw.mesh_vertices
        Draw.triangle_mesh.triangles = Draw.mesh_triangles
        Draw.triangle_mesh.vertex_colors = Draw.mesh_vertex_colors

#        print('len(Draw.mesh_vertices) =', len(Draw.mesh_vertices))
#        print('len(Draw.mesh_triangles) =', len(Draw.mesh_triangles))
#        print('len(Draw.mesh_vertex_colors) =', len(Draw.mesh_vertex_colors))
#        print('len(Draw.triangle_mesh.vertices) =', len(Draw.triangle_mesh.vertices))
#        print('len(Draw.triangle_mesh.triangles) =', len(Draw.triangle_mesh.triangles))
#        print('len(Draw.triangle_mesh.vertex_colors) =', len(Draw.triangle_mesh.vertex_colors))
#        print(np.asarray(Draw.mesh_vertices))
#        print(np.asarray(Draw.mesh_triangles))
#        print(np.asarray(Draw.mesh_vertex_colors))


        # TODO 20230410 temp mesh for debugging
#        temp_mesh = o3d.geometry.TriangleMesh.create_octahedron()

        vis = o3d.visualization.Visualizer()
        vis.create_window()

        # TODO 20230410 temp mesh for debugging
        vis.add_geometry(Draw.triangle_mesh)
#        vis.add_geometry(temp_mesh)
        
#        rot_z_angle = 0
#        for i in range(400):
        while True:
            Draw.triangle_mesh.vertices = Draw.mesh_vertices
            Draw.triangle_mesh.triangles = Draw.mesh_triangles
#            rot_z_angle += 0.008
#            rot = triangle_mesh.get_rotation_matrix_from_xyz((0, 0, rot_z_angle))
#            triangle_mesh.rotate(rot, center=(0, 0, 0))
#            triangle_mesh.compute_vertex_normals() ## ???
#            Draw.triangle_mesh.compute_vertex_normals() ## ???


            # TODO 20230410 temp mesh for debugging
            vis.update_geometry(Draw.triangle_mesh)
            vis.poll_events()
            vis.update_renderer()
        vis.destroy_window()


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# Trying to test per-triangle colors as claimed to exist on:
# https://github.com/isl-org/Open3D/issues/1087#issuecomment-1222782733

    def face_color_test():
        mesh = o3d.geometry.TriangleMesh.create_octahedron()
        rgb = [[0,0,0],[0,0,1],[0,1,0],[0,1,1],[1,0,0],[1,0,1],[1,1,0],[1,1,1]]
        # face_colors = o3d.utility.Vector3dVector(np.array(rgb, np.float32))
        face_colors = o3d.utility.Vector3iVector(np.array(rgb, np.int32))
#        mesh.triangles["colors"] = face_colors
        vis = o3d.visualization.Visualizer()
        vis.create_window()
        vis.add_geometry(mesh)
        vis.run()
        vis.destroy_window()

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

#    mesh_vertices = o3d.utility.Vector3dVector()
#    mesh_triangles = o3d.utility.Vector3iVector()
#    mesh_vertex_count = 0
#
#    mesh_vertex_colors = o3d.utility.Vector3dVector()
#
#    def add_random_triangle():
#        pos_scale = 50
#        add_triangle([pos_scale * util.frandom01(),
#                      pos_scale * util.frandom01(),
#                      0], None)

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

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
