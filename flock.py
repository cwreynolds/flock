import open3d as o3d
import numpy as np
import math


#    # Create a triangle with vertices at (0, 0, 0), (1, 0, 0), and (0, 1, 0)
#    triangle_vertices = np.array([])
#    triangle_indices = np.array([])


mesh_vertices = o3d.utility.Vector3dVector()
mesh_triangles = o3d.utility.Vector3iVector()
mesh_vertex_count = 0

def frandom01():
    return np.random.uniform(0, 1)


def add_random_triangle():
#    pos_scale = 10
    pos_scale = 50
    add_triangle([pos_scale * frandom01(), pos_scale * frandom01(), 0],
                  0)


#def add_triangle(position, orientation):
##    xyz = np.array([0, 0, 0])
#    xyz = np.array([position[0], position[1], position[2]])
#    mesh_vertices.append(xyz)
#
#    global mesh_vertex_count
#    mesh_triangles.append([mesh_vertex_count,
#                           mesh_vertex_count + 1,
#                           mesh_vertex_count + 3])
#    mesh_vertex_count += 3

#    def add_triangle(position, orientation):
#    #    xyz = np.array([0, 0, 0])
#        xyz = np.array([position[0], position[1], position[2]])
#
#        rp = xyz + [frandom01(), frandom01(), 0]
#        mesh_vertices.append(rp)
#        rp = xyz + [frandom01(), frandom01(), 0]
#        mesh_vertices.append(rp)
#        rp = xyz + [frandom01(), frandom01(), 0]
#        mesh_vertices.append(rp)
#
#        global mesh_vertex_count
#        mesh_triangles.append([mesh_vertex_count,
#                               mesh_vertex_count + 1,
#                               mesh_vertex_count + 3])
#        mesh_vertex_count += 3

#    def add_triangle(position, orientation):
#        xyz = np.array([position[0], position[1], position[2]])
#
#        print()
#        print('xyz =', xyz)
#
#        for i in range(3):
#            ro = np.array([frandom01(), frandom01(), 0])
#            print('ro = ', ro)
#            rp = xyz + np.array([frandom01(), frandom01(), 0])
#            print('rp = ', rp)
#            mesh_vertices.append(rp)
#
#        global mesh_vertex_count
#        mesh_triangles.append([mesh_vertex_count,
#                               mesh_vertex_count + 1,
#                               mesh_vertex_count + 3])
#        mesh_vertex_count += 3

def add_triangle(position, orientation):
    xyz = np.array([position[0], position[1], position[2]])
    
    v = np.array([1, 0, 0])
    a = frandom01() * math.pi * 2
    
    print()
    print(xyz)
    
    for i in range(3):
#        ro = np.array([frandom01(), frandom01(), 0])
        a += math.pi * 2 / 3
        v = np.array(rotate_xy_about_z(v, a))
        print('v = ', v)
        rp = xyz + np.array(v)
        print('rp = ', rp)
        mesh_vertices.append(rp)
    
    global mesh_vertex_count
    mesh_triangles.append([mesh_vertex_count,
                           mesh_vertex_count + 1,
                           mesh_vertex_count + 2])
    mesh_vertex_count += 3

#    // TODO 20230221 reconsider name, etc.
#    Vec3 rotateXyAboutZ(float angle) const
#    {
#        float s = std::sin(angle);
#        float c = std::cos(angle);
#        return Vec3(x() * c + y() * s, y() * c - x() * s, z());
#    }

def rotate_xy_about_z(vec3, angle):
    s = math.sin(angle)
    c = math.cos(angle)
    x = vec3[0]
    y = vec3[1]
    z = vec3[2]
    return [(x * c + y * s), y * c - x * s, z]

def test():

    for i in range(50):
        add_random_triangle()


#    # Create a triangle with vertices at (0, 0, 0), (1, 0, 0), and (0, 1, 0)
#    triangle_vertices = np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0]])
#    triangle_indices = np.array([[0, 1, 2]])

    # Create a mesh from the triangle vertices and indices
    triangle_mesh = o3d.geometry.TriangleMesh()
#    triangle_mesh.vertices = o3d.utility.Vector3dVector(triangle_vertices)
#    triangle_mesh.triangles = o3d.utility.Vector3iVector(triangle_indices)
    triangle_mesh.vertices = mesh_vertices
    triangle_mesh.triangles = mesh_triangles
    
    print('len(mesh_vertices) =', len(mesh_vertices))
    print('len(mesh_triangles) =', len(mesh_triangles))

#    print('mesh_vertices.asarray() =', mesh_vertices.asarray())
#    print('mesh_triangles.asarray() =', mesh_triangles.asarray())

    print('Vertices:')
    print(np.asarray(triangle_mesh.vertices))
    print('Triangles:')
    print(np.asarray(triangle_mesh.triangles))


    vis = o3d.visualization.Visualizer()
    vis.create_window()
    vis.add_geometry(triangle_mesh)
    
    rot_z_angle = 0

#    for i in range(200):
    for i in range(400):
#        triangle_mesh.vertices = o3d.utility.Vector3dVector(triangle_vertices)
#        triangle_mesh.triangles = o3d.utility.Vector3iVector(triangle_indices)
        triangle_mesh.vertices = mesh_vertices
        triangle_mesh.triangles = mesh_triangles

#        rot_z_angle += 0.01
        rot_z_angle += 0.008
    
#        R = triangle_mesh.get_rotation_matrix_from_xyz((0,0,0.01))
        rot = triangle_mesh.get_rotation_matrix_from_xyz((0, 0, rot_z_angle))
        triangle_mesh.rotate(rot, center=(0, 0, 0))
        vis.update_geometry(triangle_mesh)
        vis.poll_events()
        vis.update_renderer()
    vis.destroy_window()

if __name__ == "__main__":
#    for i in range(50):
#        print(frandom01())

#    print('[1, 2, 3] + [10, 20, 30]', [1, 2, 3] + [10, 20, 30])
    
#        rp = xyz + np.array([frandom01(), frandom01(), 0])

#    print('np.array([1, 2, 3]) + np.array([10, 20, 30])',
#          np.array([1, 2, 3]) + np.array([10, 20, 30]))
    
    test()
