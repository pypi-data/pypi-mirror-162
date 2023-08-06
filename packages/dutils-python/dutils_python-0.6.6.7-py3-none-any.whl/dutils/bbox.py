import torch
import numpy as np
from .transforms import dot
from .dutils import type_convert, has_torch, cat


def bbox2bbox_corners(bbox, discrete=False):
    #      3-------7
    #     /|      /|
    #    / |     / |
    #   2--|----6  |
    #   |  1----|--5
    #   | /     | /
    #   |/      |/
    #   0-------4
    bbox_corners = []
    for x in [0, 3]:
        for y in [1, 4]:
            for z in [2, 5]:
                bbox_corners.append([bbox[x], bbox[y], bbox[z]])

    bbox_corners = np.array(bbox_corners)
    if discrete:
        return bbox_corners.astype(int)
    return bbox_corners


def bbox_corners2bbox(bbox_corners, discrete=False):
    bbox_min = np.min(bbox_corners, 0)
    bbox_max = np.max(bbox_corners, 0)
    if discrete:
        return np.concatenate([bbox_min.astype(int), np.ceil(bbox_max).astype(int)])
    return np.concatenate([bbox_min, bbox_max])


def bbox_corners2transform(bbox_corners):
    z = bbox_corners[1] - bbox_corners[0]
    y = bbox_corners[2] - bbox_corners[0]
    x = bbox_corners[4] - bbox_corners[0]
    trs = np.eye(4)
    trs[:3, :3] = np.stack([x, y, z]).T
    trs[:3, 3] = bbox_corners[0]
    return trs


def compute_AABB(points):
    return np.concatenate([np.min(points, 0), np.max(points, 0)])


def shape_AABB(aabb):
    return aabb[3:6] - aabb[:3]


def vol_AABB(aabb):
    if has_torch(aabb):
        return torch.prod(shape_AABB(aabb))
    return np.prod(shape_AABB(aabb))


def compute_FBB(points):
    cov_points = np.cov(points, y=None, rowvar=0, bias=1)
    v, vect = np.linalg.eig(cov_points)
    tvect = np.transpose(vect)
    points_rotated = np.dot(points, np.linalg.inv(tvect))
    mina = np.min(points_rotated, axis=0)
    maxa = np.max(points_rotated, axis=0)
    bbox_corners = dot(tvect.T, bbox2bbox_corners(np.concatenate([mina, maxa])))
    return bbox_corners


def compute_OBB(points):
    cov_points = np.cov(points[:, [0, 2]], y=None, rowvar=0, bias=1)
    v, vect = np.linalg.eig(cov_points)
    tvect = np.transpose(vect)
    points_rotated = np.dot(points[:, [0, 2]], np.linalg.inv(tvect))
    mina = np.min(points_rotated, axis=0)
    maxa = np.max(points_rotated, axis=0)
    t_g = np.eye(3)
    t_g[0, 0] = tvect[0, 0]
    t_g[0, 2] = tvect[0, 1]
    t_g[2, 0] = tvect[1, 0]
    t_g[2, 2] = tvect[1, 1]
    mina = np.array([mina[0], np.min(points[:, 1]), mina[1]])
    maxa = np.array([maxa[0], np.max(points[:, 1]), maxa[1]])
    bbox_corners = dot(t_g.T, bbox2bbox_corners(np.concatenate([mina, maxa])))
    return bbox_corners


def intersect_AABB(*aabbs):
    if has_torch(*aabbs):
        return intersect_AABB_torch(type_convert(*aabbs))

    joint_aabbs = np.stack(aabbs, 0)
    intersect_aabb = np.concatenate([np.max(joint_aabbs[:, :3], 0), np.min(joint_aabbs[:, 3:6], 0)])

    return intersect_aabb


def intersect_AABB_torch(*aabbs):

    joint_aabbs = torch.stack(*aabbs, 0)
    intersect_aabb = torch.cat([torch.max(joint_aabbs[:, :3], 0).values, torch.min(joint_aabbs[:, 3:6], 0).values])
    return intersect_aabb


def union_AABB(*aabbs):
    if has_torch(*aabbs):
        return union_AABB_torch(type_convert(*aabbs))

    joint_aabbs = np.stack(aabbs, 0)
    intersect_aabb = np.concatenate([np.min(joint_aabbs[:, :3], 0), np.max(joint_aabbs[:, 3:6], 0)])
    return intersect_aabb


def union_AABB_torch(*aabbs):
    joint_aabbs = torch.stack(*aabbs, 0)
    union_aabb = torch.cat([torch.min(joint_aabbs[:, :3], 0).values, torch.max(joint_aabbs[:, 3:6], 0).values])
    return union_aabb


def shift_AABB(aabb, translation):
    # translation: xyz
    if isinstance(translation, torch.Tensor):
        shift_vector = torch.cat([translation, translation]).to(aabb.device)
    else:
        shift_vector = np.concatenate([translation, translation])
    return aabb + shift_vector


def inside_AABB(points, aabb):
    if has_torch(points):
        if not has_torch(aabb):
            aabb = torch.from_numpy(aabb).to(points)
        return torch.all(points >= aabb[:3], 1) & torch.all(points <= aabb[3:6], 1)
    else:
        if has_torch(aabb):
            aabb = aabb.cpu().numpy()
        return np.all(points >= aabb[:3], 1) & np.all(points <= aabb[3:6], 1)

