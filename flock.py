import open3d as o3d
import numpy as np

# from http://www.open3d.org/docs/release/tutorial/visualization/non_blocking_visualization.html


# Create a triangle with vertices at (0, 0, 0), (1, 0, 0), and (0, 1, 0)
triangle_vertices = np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0]])
triangle_indices = np.array([[0, 1, 2]])

# Create a mesh from the triangle vertices and indices
triangle_mesh = o3d.geometry.TriangleMesh()
triangle_mesh.vertices = o3d.utility.Vector3dVector(triangle_vertices)
triangle_mesh.triangles = o3d.utility.Vector3iVector(triangle_indices)

vis = o3d.visualization.Visualizer()
vis.create_window()
#    vis.add_geometry(source)
#    vis.add_geometry(target)
vis.add_geometry(triangle_mesh)

#    threshold = 0.05
#    icp_iteration = 100
#    save_image = False

#for i in range(icp_iteration):
#        reg_p2l = o3d.pipelines.registration.registration_icp(
#            source, target, threshold, np.identity(4),
#            o3d.pipelines.registration.TransformationEstimationPointToPlane(),
#            o3d.pipelines.registration.ICPConvergenceCriteria(max_iteration=1))
#        source.transform(reg_p2l.transformation)
for i in range(200):

#    triangle_mesh.rotate(1,2,3)

#    R = mesh.get_rotation_matrix_from_xyz((np.pi / 2, 0, np.pi / 4))
#    mesh_r.rotate(R, center=(0, 0, 0))
#    R = triangle_mesh.get_rotation_matrix_from_xyz((1,2,3))
    R = triangle_mesh.get_rotation_matrix_from_xyz((0,0,0.01))
    triangle_mesh.rotate(R, center=(0, 0, 0))



#    vis.update_geometry(source)
    vis.update_geometry(triangle_mesh)
    vis.poll_events()
    vis.update_renderer()
#        if save_image:
#            vis.capture_screen_image("temp_%04d.jpg" % i)
vis.destroy_window()



#    # suggested by ChatGPT:
#
#    import open3d as o3d
#    import numpy as np
#
#    # Create a triangle with vertices at (0, 0, 0), (1, 0, 0), and (0, 1, 0)
#    triangle_vertices = np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0]])
#    triangle_indices = np.array([[0, 1, 2]])
#
#    # Create a mesh from the triangle vertices and indices
#    triangle_mesh = o3d.geometry.TriangleMesh()
#    triangle_mesh.vertices = o3d.utility.Vector3dVector(triangle_vertices)
#    triangle_mesh.triangles = o3d.utility.Vector3iVector(triangle_indices)
#
#    # Create a visualization window and add the triangle mesh to it
#    vis = o3d.visualization.Visualizer()
#    vis.create_window()
#    #vis.add_geometry(triangle_mesh)
#
#    # Create a view control to rotate the camera
#    view_control = vis.get_view_control()
#    view_control.rotate(10.0, 0.0)
#
#    # Keep rotating the camera until the window is closed
#    i = 0
#    while True:
#    #    view_control.rotate(10.0, 0.0)
#        view_control.rotate(1, 2, 3)
#    #    vis.update_geometry()
#        vis.update_geometry(triangle_mesh)
#        vis.poll_events()
#        vis.update_renderer()
#        print(i)
#        i += 1

vis.destroy_window()


#    import open3d as o3d
#    import numpy as np
#
#    # Create a triangle with vertices at (0, 0, 0), (1, 0, 0), and (0, 1, 0)
#    triangle_vertices = np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0]])
#    triangle_indices = np.array([[0, 1, 2]])
#
#    # Create a mesh from the triangle vertices and indices
#    triangle_mesh = o3d.geometry.TriangleMesh()
#    triangle_mesh.vertices = o3d.utility.Vector3dVector(triangle_vertices)
#    triangle_mesh.triangles = o3d.utility.Vector3iVector(triangle_indices)
#
#    # Create a visualization window and add the triangle mesh to it
#    vis = o3d.visualization.Visualizer()
#    vis.create_window()
#    vis.add_geometry(triangle_mesh)
#
#    #    # Create a view control to rotate the camera
#    #    view_control = vis.get_view_control()
#    #    view_control.rotate(10.0, 0.0)
#
#
#    # Keep rotating the camera until the window is closed
#    #while not vis.poll_events():
#    #while True:
#    while vis.poll_events():
#    #    view_control.rotate(10.0, 0.0)
#        triangle_mesh.rotate(10, 0)
#        vis.update_renderer()
#
#    vis.destroy_window()


#    import open3d as o3d
#    import numpy as np
#
#    # Create a triangle with vertices at (0, 0, 0), (1, 0, 0), and (0, 1, 0)
#    triangle_vertices = np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0]])
#    triangle_indices = np.array([[0, 1, 2]])
#
#    # Create a mesh from the triangle vertices and indices
#    triangle_mesh = o3d.geometry.TriangleMesh()
#    triangle_mesh.vertices = o3d.utility.Vector3dVector(triangle_vertices)
#    triangle_mesh.triangles = o3d.utility.Vector3iVector(triangle_indices)
#
#    # Create a visualization window and add the triangle mesh to it
#    vis = o3d.visualization.Visualizer()
#    vis.create_window()
#    vis.add_geometry(triangle_mesh)
#
#    # Render the visualization
#    vis.run()
#    vis.destroy_window()
