import numpy as np
import torch
from .dutils import has_torch
from transforms3d.euler import euler2mat
from transforms3d.axangles import axangle2mat
from transforms3d.quaternions import quat2mat


def dot(transform, points, coords=False):
    if isinstance(points, torch.Tensor):
        return dot_torch(transform, points, coords)
    else:
        if isinstance(transform, torch.Tensor):  # points dominate
            transform = transform.cpu().numpy()
    if type(points) == list:
        points = np.array(points)

    if len(points.shape) == 1:
        # single point
        if transform.shape == (3, 3):
            return transform @ points[:3]
        else:
            return (transform @ np.array([*points[:3], 1]))[:3]
    if points.shape[1] == 3 or (coords and points.shape[1] > 3):
        # nx[xyz,...]
        if transform.shape == (4, 4):
            pts = (transform[:3, :3] @ points[:, :3].T).T + transform[:3, 3]
        elif transform.shape == (3, 3):
            pts = (transform[:3, :3] @ points[:, :3].T).T
        else:
            raise RuntimeError("Format of transform not understood")
        return np.concatenate([pts, points[:, 3:]], 1)
    else:
        raise RuntimeError(f"Format of points {points.shape} not understood")

    """
    elif len(points.shape) == 2:
        if points.shape[0] not in [3, 4] and points.shape[1] in [3, 4]:
            # needs to be transposed for dot product
            points = points.T
    else:
        raise RuntimeError("Format of points not understood")
    # points in format [3/4,n]
    if transform.shape == (4, 4):
        return (transform[:3, :3] @ points[:3]).T + transform[:3, 3]
    elif transform.shape == (3, 3):
        return (transform[:3, :3] @ points[:3]).T
    else:
        raise RuntimeError("Format of transform not understood")
    """


def dot_torch(transform, points, coords=False):
    if not isinstance(transform, torch.Tensor):
        transform = torch.from_numpy(transform).float()

    transform = transform.to(points.device).float()
    if type(points) == list:
        points = torch.Tensor(points)
    if len(points.shape) == 1:
        # single point
        if transform.shape == (3, 3):
            return transform @ points[:3]
        else:
            return (transform @ torch.Tensor([*points[:3], 1]))[:3]
    if points.shape[1] == 3 or (coords and points.shape[1] > 3):
        # nx[xyz,...]
        if transform.shape == (4, 4):
            pts = (transform[:3, :3] @ points[:, :3].T).T + transform[:3, 3]
        elif transform.shape == (3, 3):
            pts = (transform[:3, :3] @ points[:, :3].T).T
        else:
            raise RuntimeError("Format of transform not understood")
        return torch.cat([pts, points[:, 3:]], 1)
    else:
        raise RuntimeError(f"Format of points {points.shape} not understood")
    """
    elif len(points.shape) == 2:
        if points.shape[0] not in [3, 4] and points.shape[1] in [3, 4]:
            # needs to be transposed for dot product
            points = points.T
    else:
        raise RuntimeError("Format of points not understood")
    # points in format [3/4,n]
    if transform.shape == (4, 4):
        return (transform[:3, :3] @ points[:3]).T + transform[:3, 3]
    elif transform.shape == (3, 3):
        return (transform[:3, :3] @ points[:3]).T
    else:
        raise RuntimeError("Format of transform not understood")
    """


def dot2d(transform, points):
    if type(points) == list:
        points = np.array(points)

    if len(points.shape) == 1:
        # single point
        if transform.shape == (2, 2):
            return transform @ points[:2]
        else:
            return (transform @ np.array([*points[:2], 1]))[:2]
    elif len(points.shape) == 2:
        if points.shape[1] in [2, 3]:
            # needs to be transposed for dot product
            points = points.T
    else:
        raise RuntimeError("Format of points not understood")
    # points in format [2/3,n]
    if transform.shape == (3, 3):
        return (transform[:2, :2] @ points[:2]).T + transform[:2, 2]
    elif transform.shape == (2, 2):
        return (transform[:2, :2] @ points[:2]).T
    else:
        raise RuntimeError("Format of transform not understood")


def backproject(depth, intrinsics, cam2world=np.eye(4), color=None):
    # in height x width (xrgb)
    h, w = depth.shape
    valid_px = depth > 0
    yv, xv = np.meshgrid(range(h), range(w), indexing="ij")
    img_coords = np.stack([yv, xv], -1)
    img_coords = img_coords[valid_px]
    z_coords = depth[valid_px]
    pts = uvd_backproject(img_coords, z_coords, intrinsics, cam2world, color[valid_px] if color is not None else None)

    return pts


def uvd_backproject(uv, d, intrinsics, cam2world=np.eye(4), color=None):
    fx, fy, cx, cy = intrinsics[0, 0], intrinsics[1, 1], intrinsics[0, 2], intrinsics[1, 2]
    py = (uv[:, 0] - cy) * d / fy
    px = (uv[:, 1] - cx) * d / fx
    pts = np.stack([px, py, d])

    pts = cam2world[:3, :3] @ pts + np.tile(cam2world[:3, 3], (pts.shape[1], 1)).T
    pts = pts.T
    if color is not None:
        pts = np.concatenate([pts, color], 1)

    return pts


def trs_decomp(A):
    if has_torch(A):
        s_vec = torch.norm(A[:3, :3], dim=0)
    else:
        s_vec = np.linalg.norm(A[:3, :3], axis=0)
    R = A[:3, :3] / s_vec
    t = A[:3, 3]
    return t, R, s_vec


def scale_mat(s, as_torch=True):
    if isinstance(s, np.ndarray):
        s_mat = np.eye(4)
        s_mat[:3, :3] *= s
    elif has_torch(s):
        s_mat = torch.eye(4).to(s.device)
        s_mat[:3, :3] *= s
        s_mat
    else:
        s_mat = torch.eye(4) if as_torch else np.eye(4)
        s_mat[:3, :3] *= s
    return s_mat


def trans_mat(t):
    if has_torch(t):
        t_mat = torch.eye(4).to(t.device).float()
        t_mat[:3, 3] = t
    else:
        t_mat = np.eye(4, dtype=np.float32)
        t_mat[:3, 3] = t
    return t_mat


def rot_mat(axangle=None, euler=None, quat=None, as_torch=True):
    R = np.eye(3)
    if axangle is not None:
        if euler is None:
            axis, angle = axangle[0], axangle[1]
        else:
            axis, angle = axangle, euler
        R = axangle2mat(axis, angle)
    elif euler is not None:
        R = euler2mat(*euler)
    elif quat is not None:
        R = quat2mat(quat)
    if as_torch:
        R = torch.Tensor(R)
    return R


def hmg(M):
    if len(M.shape) == 2:
        if M.shape[0] == 3 and M.shape[1] == 3:
            if has_torch(M):
                hmg_M = torch.eye(4, dtype=M.dtype).to(M.device)
            else:
                hmg_M = np.eye(4, dtype=M.dtype)
            hmg_M[:3, :3] = M
        elif M.shape[1] == 2:
            # uv coordinates
            if has_torch(M):
                hmg_M = torch.cat([M, torch.ones(len(M), 1).to(M)], -1)
            else:
                hmg_M = np.concatenate([M, np.ones((len(M), 1))], -1)
        else:
            hmg_M = M
        
    else:
        return M
    return hmg_M


def trs_comp(t, R, s_vec):
    return trans_mat(t) @ hmg(R) @ scale_mat(s_vec)

def unproject_2d_3d(cam2world, K, d, uv=None, th=None, extra_img=None):
    if extra_img is not None:
        extra_img = extra_img.reshape(-1,3)
    if uv is None and len(d.shape) >= 2:
        # create mesh grid according to d
        uv = np.stack(np.meshgrid(np.arange(d.shape[1]), np.arange(d.shape[0])), -1)
        uv = uv.reshape(-1, 2)
        d = d.reshape(-1)
        if not isinstance(d, np.ndarray):
            uv = torch.from_numpy(uv).to(d)
        if th is not None:
            depth_mask = d > th
            uv = uv[depth_mask]
            d = d[depth_mask]
        if extra_img is not None and depth_mask is not None:
            extra_img = extra_img[depth_mask]
    if isinstance(uv, np.ndarray):
        uvh = np.concatenate([uv, np.ones((len(uv), 1))], -1)
        cam_point = dot(np.linalg.inv(K), uvh) * d[:, None]
    else:
        uvh = torch.cat([uv, torch.ones(len(uv), 1).to(uv)], -1)
        cam_point = dot(torch.inverse(K), uvh) * d[:, None]

    world_point = dot(cam2world, cam_point)
    if extra_img is not None:
        if isinstance(world_point, np.ndarray):
            return np.concatenate([world_point,extra_img],1)
        else:
            return torch.cat([world_point,extra_img],1)
    return world_point

def project_3d_2d(cam2world, K, world_point, with_z=False, discrete=True,round=True):
    if isinstance(world_point, np.ndarray):
        cam_point = dot(np.linalg.inv(cam2world), world_point)
        img_point = dot(K, cam_point)
        uv_point = img_point[:, :2] / img_point[:, 2][:, None]
        if discrete:
            if round:
                uv_point = np.round(uv_point)
            uv_point = uv_point.astype(np.int)
        if with_z:
            return uv_point, img_point[:, 2]
        return uv_point

    else:
        cam_point = dot(torch.inverse(cam2world), world_point)
        img_point = dot(K, cam_point)
        uv_point = img_point[:, :2] / img_point[:, 2][:, None]
        if discrete:
            if round:
                uv_point = torch.round(uv_point)
                uv_point = uv_point.int()
        if with_z:
            return uv_point, img_point[:, 2]

        return uv_point
