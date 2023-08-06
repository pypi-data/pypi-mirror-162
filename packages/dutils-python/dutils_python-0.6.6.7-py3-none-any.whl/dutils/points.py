import open3d as o3d
import trimesh
import numpy as np


def icp_reg(pts_a, pts_b, dist=0.1, max_iter=2000):
    # returns transform pts_a -> pts_b
    pcd_a = o3d.geometry.PointCloud()
    pcd_a.points = o3d.utility.Vector3dVector(pts_a)
    pcd_b = o3d.geometry.PointCloud()
    pcd_b.points = o3d.utility.Vector3dVector(pts_b)

    reg_p2p = o3d.pipelines.registration.registration_icp(
        source=pcd_a,
        target=pcd_b,
        max_correspondence_distance=dist,
        init=np.eye(4),
        estimation_method=o3d.pipelines.registration.TransformationEstimationPointToPoint(),
        criteria=o3d.pipelines.registration.ICPConvergenceCriteria(max_iteration=max_iter),
    )
    return reg_p2p.transformation


def single_view_mesh(color_fn, depth_fn, intrinsic, dense_mask_fn=None, width=640, height=480, depth_scale=5000):
    import open3d as o3d

    volume = o3d.pipelines.integration.ScalableTSDFVolume(
        voxel_length=4.0 / 512.0, sdf_trunc=0.06, color_type=o3d.pipelines.integration.TSDFVolumeColorType.RGB8
    )

    # FLIPPING Y HERE!!!
    color = o3d.io.read_image(str(color_fn)).flip_vertical()
    depth = o3d.io.read_image(str(depth_fn)).flip_vertical()
    if dense_mask_fn is not None:
        dense_mask = o3d.io.read_image(str(dense_mask_fn)).flip_vertical()
        depth_arr = np.array(depth)
        depth_arr[np.array(dense_mask) > 0] = -1
        depth = o3d.geometry.Image(depth_arr)

    rgbd = o3d.geometry.RGBDImage.create_from_color_and_depth(
        color, depth, depth_trunc=7.0, convert_rgb_to_intensity=False, depth_scale=depth_scale
    )
    pcd_intrinsic = o3d.camera.PinholeCameraIntrinsic()
    pcd_intrinsic.set_intrinsics(width, height, intrinsic[0, 0], intrinsic[1, 1], intrinsic[0, 2], intrinsic[1, 2])
    volume.integrate(rgbd, pcd_intrinsic, np.eye(4))
    mesh = volume.extract_triangle_mesh()
    # flip
    # mesh.transform(np.diag([1,-1,1,1]))
    # mesh.compute_vertex_normals()

    return mesh


def o3d_mesh2trimesh(mesh, num_verts=None):
    if num_verts is not None:
        mesh = mesh.simplify_quadric_decimation(num_verts)
    tri_mesh = trimesh.Trimesh(vertices=np.array(mesh.vertices), faces=np.array(mesh.triangles), process=False)
    tri_mesh.visual.vertex_colors = (
        255 * np.concatenate([np.array(mesh.vertex_colors), np.ones((len(np.array(mesh.vertex_colors)), 1))], 1)
    ).astype(np.uint8)
    # tri_mesh = tri_mesh.simplify_quadratic_decimation(num_verts)
    return tri_mesh


def set_vertex_colors(mesh, colors):
    # colors in [0,1] range
    if len(colors.shape) == 2 and colors.shape[1] == 3:
        mesh.visual.vertex_colors = (255 * np.concatenate([colors, np.ones((len(colors), 1))], 1)).astype(np.uint8)
    return mesh
