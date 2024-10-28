# Sandbox for python version of look_at work around, see:
#
#     How do I set the 3D coordinates of the virtual camera...
#     https://github.com/isl-org/Open3D/discussions/7031
#
#     “look at” add-on to legacy Visualizer/ViewControl
#     https://github.com/isl-org/Open3D/discussions/7023

# ------------------------------------------------------------------------------
#
# Looks like this is a dead end, but I will keep it here for now. Issue #7031
# ends with:

# cwreynolds:
# Maybe the answer is no. I tried to translate my code to Python. That required
# making a new environment for Open3D 0.18.0 since the last time I used Open3D
# from Python the current release was 0.17.0, which had a bug preventing
#  modification of ViewControl.
#
# But as near as I can tell, there is no direct Python analog to the c++
# function open3d::visualization::gl_util::LookAt() which my code is based on.
# The symbol “gl_util” does not appear in the Open3D Python doc at all. It would
# be possible to write such a function, but I think that is probably going too
# far in the wrong direction.
#
# You might be better off to look into the newer O3DVisualizer class which has a
# function providing look-at-up functionality: setup_camera()
#
# Zhouwudexiazhou:
# I have tested O3DVisualizer class in python. It work!!! Thank you bro, Thank
# you!!!
#
# ------------------------------------------------------------------------------

import open3d as o3d

#    void setOpen3DVisualizerViewByFromAt(open3d::visualization::Visualizer& vis,
#                                         const Eigen::Vector3d& look_from,
#                                         const Eigen::Vector3d& look_at,
#                                         const Eigen::Vector3d& up = {0, 1, 0})
#    {
#        // Compute 4x4 from/at matrix.
#        using namespace open3d::visualization::gl_util;
#        Eigen::Matrix4d la_matrix = LookAt(look_from, look_at, up).cast<double>();
#
#        // Get current PinholeCameraParameters.
#        open3d::camera::PinholeCameraParameters pcp;
#        vis.GetViewControl().ConvertToPinholeCameraParameters(pcp);
#
#        // Overwrite the pcp's previous view matrix with the new look_at matrix.
#        // (I am deeply puzzled by the need for that negation, but here we are.)
#        pcp.extrinsic_ = -la_matrix;
#        pcp.extrinsic_(3, 3) = 1;
#
#        // Write back PinholeCameraParameters with new from/at view matrix.
#        vis.GetViewControl().ConvertFromPinholeCameraParameters(pcp);
#    }


def setOpen3DVisualizerViewByFromAt(vis, look_from, look_at, up = [0, 1, 0]):


#    open3d::visualization::gl_util::LookAt()

    o3d.visualization.gl_util.look_at(look_from, look_at, up)

#    cam = o3d.visualization.rendering.Camera()
#    cam = o3d.camera.PinholeCameraParameters()
#    cam = o3d.visualization.rendering.FilamentCamera()
#    cam = o3d.visualization.rendering.Camera()
    
#    // Compute 4x4 from/at matrix.
#    using namespace open3d::visualization::gl_util;
#    Eigen::Matrix4d la_matrix = LookAt(look_from, look_at, up).cast<double>();



#    // Get current PinholeCameraParameters.
#    open3d::camera::PinholeCameraParameters pcp;
#    vis.GetViewControl().ConvertToPinholeCameraParameters(pcp);

    vc = vis.get_view_control()

    # Get current PinholeCameraParameters.
    pcp = vc.convert_to_pinhole_camera_parameters()
    
    print(vis.get_view_control().convert_to_pinhole_camera_parameters().intrinsic.width)
    print(vis.get_view_control().convert_to_pinhole_camera_parameters().intrinsic.height)
    
    print(pcp.intrinsic.width, pcp.intrinsic.height)
    

#    vc.convert_from_pinhole_camera_parameters(pcp)
    vc.convert_from_pinhole_camera_parameters(pcp, True)


#
#    // Overwrite the pcp's previous view matrix with the new look_at matrix.
#    // (I am deeply puzzled by the need for that negation, but here we are.)
#    pcp.extrinsic_ = -la_matrix;
#    pcp.extrinsic_(3, 3) = 1;
#    
#    // Write back PinholeCameraParameters with new from/at view matrix.
#    vis.GetViewControl().ConvertFromPinholeCameraParameters(pcp);



def test_look_at():

    # Create Visualizer and a window for it.
    vis = o3d.visualization.VisualizerWithKeyCallback()
    vis.create_window()

    # Add green octohedron.
    oct = o3d.geometry.TriangleMesh.create_octahedron(radius=0.5)
    oct.compute_vertex_normals()
    oct.paint_uniform_color([0, 0.5, 0])
    vis.add_geometry(oct)

#    vis.run()

    while (vis.poll_events()):
        setOpen3DVisualizerViewByFromAt(vis, [2, 2, 2], [0, 0.5, 0])
        vis.update_geometry(oct)


if __name__ == "__main__":
    test_look_at()
