# suggested by ChatGPT:


import open3d as o3d
import numpy as np

# Create a triangle with vertices at (0, 0, 0), (1, 0, 0), and (0, 1, 0)
triangle_vertices = np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0]])
triangle_indices = np.array([[0, 1, 2]])

# Create a mesh from the triangle vertices and indices
triangle_mesh = o3d.geometry.TriangleMesh()
triangle_mesh.vertices = o3d.utility.Vector3dVector(triangle_vertices)
triangle_mesh.triangles = o3d.utility.Vector3iVector(triangle_indices)

# Create a visualization window and add the triangle mesh to it
vis = o3d.visualization.Visualizer()
vis.create_window()
vis.add_geometry(triangle_mesh)

# Render the visualization
vis.run()
vis.destroy_window()
