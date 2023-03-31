import open3d as o3d
import numpy as np
import math

mesh_vertices = o3d.utility.Vector3dVector()
mesh_triangles = o3d.utility.Vector3iVector()
mesh_vertex_count = 0

mesh_vertex_colors = o3d.utility.Vector3dVector()


def frandom01():
    return np.random.uniform(0, 1)


def add_random_triangle():
#    pos_scale = 10
    pos_scale = 50
    add_triangle([pos_scale * frandom01(), pos_scale * frandom01(), 0],
                  0)

def add_triangle(position, orientation):
    xyz = np.array([position[0], position[1], position[2]])
    
    v = np.array([1, 0, 0])
    a = frandom01() * math.pi * 2
    color = [frandom01(), frandom01(), frandom01()]
    
#    print()
#    print(xyz)
    
    for i in range(3):
        a += math.pi * 2 / 3
        v = np.array(rotate_xy_about_z(v, a))
#        print('v = ', v)
        rp = xyz + np.array(v)
#        print('rp = ', rp)
        mesh_vertices.append(rp)
        
        mesh_vertex_colors.append(color)
    
    global mesh_vertex_count
    mesh_triangles.append([mesh_vertex_count,
                           mesh_vertex_count + 1,
                           mesh_vertex_count + 2])
    mesh_vertex_count += 3

def rotate_xy_about_z(vec3, angle):
    s = math.sin(angle)
    c = math.cos(angle)
    x = vec3[0]
    y = vec3[1]
    z = vec3[2]
    return [(x * c + y * s), y * c - x * s, z]

def test():

#    for i in range(50):
    for i in range(200):
        add_random_triangle()

    # Create a mesh from the triangle vertices and indices
    triangle_mesh = o3d.geometry.TriangleMesh()
    triangle_mesh.vertices = mesh_vertices
    triangle_mesh.triangles = mesh_triangles
    
#    mesh_np.vertex_colors = o3d.utility.Vector3dVector(
#        np.random.uniform(0, 1, size=(N, 3)))

    triangle_mesh.vertex_colors = mesh_vertex_colors

#    print('len(mesh_vertices) =', len(mesh_vertices))
#    print('len(mesh_triangles) =', len(mesh_triangles))
#    print('Vertices:')
#    print(np.asarray(triangle_mesh.vertices))
#    print('Triangles:')
#    print(np.asarray(triangle_mesh.triangles))


    # mesh.triangle["colors"] = o3d.core.Tensor(...)
#    print('triangle_mesh.triangles["colors"].asarray() =', triangle_mesh.triangles["colors"].asarray() )


    vis = o3d.visualization.Visualizer()
    vis.create_window()
    vis.add_geometry(triangle_mesh)
    
    rot_z_angle = 0

    for i in range(400):
        triangle_mesh.vertices = mesh_vertices
        triangle_mesh.triangles = mesh_triangles

        rot_z_angle += 0.008
    
        rot = triangle_mesh.get_rotation_matrix_from_xyz((0, 0, rot_z_angle))
        triangle_mesh.rotate(rot, center=(0, 0, 0))
        
        triangle_mesh.compute_vertex_normals()
        
        vis.update_geometry(triangle_mesh)
        vis.poll_events()
        vis.update_renderer()
    vis.destroy_window()

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

if __name__ == "__main__":
#    for i in range(50):
#        print(frandom01())

#    print('[1, 2, 3] + [10, 20, 30]', [1, 2, 3] + [10, 20, 30])
    
#        rp = xyz + np.array([frandom01(), frandom01(), 0])

#    print('np.array([1, 2, 3]) + np.array([10, 20, 30])',
#          np.array([1, 2, 3]) + np.array([10, 20, 30]))
    
    test()
