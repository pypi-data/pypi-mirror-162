from dutils.bbox import shape_AABB
import torch
import numpy as np

import trimesh

from .transforms import dot
from .dutils import type_convert, has_torch, unique_agg
from dutils.points import set_vertex_colors

# new
def occ2mesh(occ_arr, smooth=False):
    import marching_cubes as mcubes

    min_val = np.zeros(3)
    color_grid = None
    if len(occ_arr.shape) == 2 and occ_arr.shape[1] == 3:
        occ_grid, min_val = indices2grid(occ_arr)
    elif len(occ_arr.shape) == 2 and occ_arr.shape[1] == 6:
        occ_grid, min_val = indices2grid(occ_arr[:, :3])
        color_grid = np.zeros((*occ_grid.shape, 3))
        color_grid = map_points_into_grid(color_grid, (occ_arr[:, :3] - min_val).astype(int), occ_arr[:, 3:6])
    elif len(occ_arr.shape) == 4:
        occ_grid = occ_arr[..., 0]
        color_grid = occ_arr[..., 1:4]
        if occ_arr.max() <= 1:
            color_grid = (color_grid * 255).astype(int)

    elif len(occ_arr.shape) == 3:
        occ_grid = occ_arr
    else:
        raise IOError

    if smooth:
        occ_grid = mcubes.smooth(occ_grid)

    if color_grid is not None:
        occ_grid = np.pad(occ_grid, pad_width=1)
        color_grid = np.pad(color_grid, pad_width=((1, 1), (1, 1), (1, 1), (0, 0))).astype(int)
        vertices, triangles = mcubes.marching_cubes_color(occ_grid, color_grid, 0.5)
        vertices -= 1
        tm = trimesh.Trimesh(vertices=vertices[:, :3] + min_val, faces=triangles, process=False)
        tm = set_vertex_colors(tm, vertices[:, 3:6])
    else:
        occ_grid = np.pad(occ_grid, pad_width=1)

        vertices, triangles = mcubes.marching_cubes(occ_grid, 0.5)
        vertices -= 1
        tm = trimesh.Trimesh(vertices=vertices + min_val, faces=triangles, process=False)
    return tm


def indices2grid(indices, fill=0):
    if has_torch(indices):
        return indices2grid_torch(indices, fill)
    min_val, max_val = np.min(indices, 0), np.max(indices, 0)
    grid = fill * np.ones((max_val - min_val).astype(np.int) + 1)
    grid[tuple((indices - min_val).astype(np.int).T)] = 1
    return grid, min_val


def indices2grid_torch(indices, fill=0):
    min_val, max_val = torch.min(indices, 0).values, torch.max(indices, 0).values
    grid = fill * torch.ones(tuple((max_val - min_val).int() + 1)).to(indices)
    grid[tuple((indices - min_val).long().T)] = 1
    return grid, min_val


def dense_crop(vg, local_aabb, padded=False, pad_value=0):
    f = -1
    if len(vg.shape) > 3:
        f = vg.shape[0]
    if padded:
        if f > 0:
            grid_shape = [f, *shape_AABB(local_aabb)]
        else:
            grid_shape = shape_AABB(local_aabb)
        if has_torch(vg):
            vg_pad = pad_value * torch.ones(grid_shape).to(vg)
        else:
            vg_pad = pad_value * np.ones(grid_shape)
        vg_shape = vg.shape[-3:]
        delta_min = np.max(np.stack([(-local_aabb[:3]), np.zeros(3)], 0), 0).astype(int)
        delta_max = np.min(np.stack([vg_shape - local_aabb[:3], local_aabb[3:6] - local_aabb[:3]], 0), 0).astype(int)
        vg_pad[..., delta_min[0] : delta_max[0], delta_min[1] : delta_max[1], delta_min[2] : delta_max[2]] = vg[
            ...,
            (local_aabb[0] + delta_min[0]) : (local_aabb[0] + delta_max[0]),
            (local_aabb[1] + delta_min[1]) : (local_aabb[1] + delta_max[1]),
            (local_aabb[2] + delta_min[2]) : (local_aabb[2] + delta_max[2]),
        ]
        return vg_pad

    return vg[
        ...,
        int(local_aabb[0]) : int(local_aabb[3]),
        int(local_aabb[1]) : int(local_aabb[4]),
        int(local_aabb[2]) : int(local_aabb[5]),
    ]


def dense_crop_mask(vg, local_aabb):
    if isinstance(vg, torch.Tensor):
        crop_mask = torch.BoolTensor(vg.shape[-3:]).fill_(False)
    else:
        crop_mask = np.zeros(vg.shape[-3:], dtype=bool)
    crop_mask[
        ...,
        int(local_aabb[0]) : int(local_aabb[3]),
        int(local_aabb[1]) : int(local_aabb[4]),
        int(local_aabb[2]) : int(local_aabb[5]),
    ] = True
    return crop_mask


def valid_grid_coords(grid, coords):
    if has_torch(grid):
        grid_shape = torch.Tensor(tuple(grid.shape[:3])).int().to(grid)
        return torch.all(coords >= 0, 1) & torch.all(coords < grid_shape, 1)

    grid_shape = grid.shape[:3]
    return np.all(coords >= 0, 1) & np.all(coords < grid_shape, 1)


def grid_coords(shape, as_torch=True):
    if as_torch:
        return torch.stack(torch.meshgrid(*[torch.arange(dim) for dim in shape]), -1)
    return np.stack(np.meshgrid(*[np.arange(dim) for dim in shape], indexing="ij"), -1)


def map_points_into_grid(grid, mapped_points, mapped_feats, agg_fct=None):
    # grid WHLxC
    if len(mapped_points) > 0:
        if not isinstance(mapped_feats, (int, float)):
            assert len(mapped_points) == len(mapped_feats)
        if has_torch(mapped_points):
            mapped_coords = mapped_points.long()
            grid_filter_mask = (
                torch.all(mapped_coords >= 0, 1)
                & (mapped_coords[:, 0] < grid.shape[0])
                & (mapped_coords[:, 1] < grid.shape[1])
                & (mapped_coords[:, 2] < grid.shape[2])
            )
        else:
            mapped_coords = mapped_points.astype(np.int)
            grid_filter_mask = (
                np.all(mapped_coords >= 0, 1)
                & (mapped_coords[:, 0] < grid.shape[0])
                & (mapped_coords[:, 1] < grid.shape[1])
                & (mapped_coords[:, 2] < grid.shape[2])
            )
        if agg_fct is None:  # just take any value
            if isinstance(mapped_feats, (int, float)):
                grid[tuple(mapped_coords[grid_filter_mask].T)] = mapped_feats
            else:
                grid[tuple(mapped_coords[grid_filter_mask].T)] = mapped_feats[grid_filter_mask]
        else:
            unique_coords, agg_feats = unique_agg(mapped_coords, mapped_feats, "mean")
            grid[tuple(unique_coords.T)] = agg_feats

    return grid


def lookup_grid_in_grid(grid_from, grid_to, from2to):
    # from low res to high res lookup
    # grid_from: WHLxC  grid_to: WHLxC
    grid_from_coords = grid_coords(grid_from.shape[:3], has_torch(grid_from)).reshape(-1, 3)
    if has_torch(grid_from_coords):
        grid_from_coords = grid_from_coords.to(grid_from.device)
        grid_from_coords_in_to = dot(from2to, grid_from_coords.float()).long()
    else:
        grid_from_coords_in_to = dot(from2to, grid_from_coords).astype(int)

    valid_from_in_to_coords = valid_grid_coords(grid_to, grid_from_coords_in_to)

    grid_from[tuple(grid_from_coords[valid_from_in_to_coords].T)] = grid_to[
        tuple(grid_from_coords_in_to[valid_from_in_to_coords].T)
    ]
    return grid_from


# old ===>


def decode_color(rgb_vals):
    colors_b = np.floor(rgb_vals / (256 * 256))
    colors_g = np.floor((rgb_vals - colors_b * 256 * 256) / 256)
    colors_r = rgb_vals - colors_b * 256 * 256 - colors_g * 256
    if len(rgb_vals.shape) == 2:
        colors = np.floor(np.asarray([colors_r, colors_g, colors_b])).T
    else:  # assume grid shape
        colors = np.floor(np.asarray([colors_r, colors_g, colors_b])).transpose(1, 2, 3, 0)
    return colors.astype(np.uint8)


def vg_crop(vg, bboxes, spatial_end=True, crop_box=False):
    # vg: ... X W X L X H
    # bboxes: N x (min, max,...) or (min,max,...)
    if len(bboxes.shape) == 1:
        if spatial_end:
            if not crop_box:
                assert np.all(bboxes[:3] >= 0) and np.all(bboxes[3:6] < vg.shape[-3:])
                return vg[..., int(bboxes[0]) : int(bboxes[3]), int(bboxes[1]) : int(bboxes[4]), int(bboxes[2]) : int(bboxes[5])]
            else:
                bbox_cropped = np.concatenate([np.max([bboxes[:3], np.zeros(3)], 0), np.min([bboxes[3:], vg.shape[-3:]], 0)], 0)
                return vg[
                    ...,
                    int(bbox_cropped[0]) : int(bbox_cropped[3]),
                    int(bbox_cropped[1]) : int(bbox_cropped[4]),
                    int(bbox_cropped[2]) : int(bbox_cropped[5]),
                ]
        else:
            if not crop_box:
                assert np.all(bboxes[:3] >= 0) and np.all(bboxes[3:6] < vg.shape[:3])
                return vg[int(bboxes[0]) : int(bboxes[3]), int(bboxes[1]) : int(bboxes[4]), int(bboxes[2]) : int(bboxes[5])]
            else:
                bbox_cropped = np.concatenate([np.max([bboxes[:3], np.zeros(3)], 0), np.min([bboxes[3:], vg.shape[:3]], 0)], 0)
                return vg[
                    int(bbox_cropped[0]) : int(bbox_cropped[3]),
                    int(bbox_cropped[1]) : int(bbox_cropped[4]),
                    int(bbox_cropped[2]) : int(bbox_cropped[5]),
                ]
    if len(bboxes.shape) == 2:
        return [vg_crop(vg, bbox, spatial_end, crop_box) for bbox in bboxes]


def shape2indices(shape):
    return np.stack(np.meshgrid(*[np.arange(dim) for dim in shape], indexing="ij"), -1)


def points_to_indices(points, vg_transform):
    points_in_vg = (np.linalg.inv(vg_transform[:3, :3]) @ (points - vg_transform[:3, 3]).T).T
    return np.round(points_in_vg).astype(int)


def integrate_grid_shift(gridA, gridB, shift=np.zeros(3), spatial_end=False, crop=False):
    # integrade B into A by shifting gridB
    gridA_shape = gridA.shape[:3] if not spatial_end else gridA.shape[-3:]
    gridB_shape = gridB.shape[:3] if not spatial_end else gridB.shape[-3:]
    if crop:
        gridA_shift_min = np.max([shift, np.zeros(3)], 0)
        gridA_shift_max = np.min([shift + gridB_shape, gridA_shape], 0)
        gridB_shift_min = -np.min([shift, np.zeros(3)], 0)
        gridB_shift_max = gridB_shape - np.max([shift, np.zeros(3)], 0)
    else:
        if not spatial_end:
            assert np.all(gridB_shape[-3:] + shift <= gridA_shape[-3:], 0)
        else:
            assert np.all(gridB_shape[:3] + shift <= gridA_shape[:3], 0)
        gridA_shift_min = shift
        gridA_shift_max = shift + gridB_shape
        gridB_shift_min = np.zeros(3)
        gridB_shift_max = gridB_shape

    if not spatial_end:
        gridA[
            int(gridA_shift_min[0]) : int(gridA_shift_max[0]),
            int(gridA_shift_min[1]) : int(gridA_shift_max[1]),
            int(gridA_shift_min[2]) : int(gridA_shift_max[2]),
        ] = gridB[
            int(gridB_shift_min[0]) : int(gridB_shift_max[0]),
            int(gridB_shift_min[1]) : int(gridB_shift_max[1]),
            int(gridB_shift_min[2]) : int(gridB_shift_max[2]),
        ]
        # gridA[int(shift[0]):int(shift[0] + gridB.shape[0]), int(shift[1]):int(shift[1] + gridB.shape[1]), int(shift[2]):int(shift[2] + gridB.shape[2])] = gridB
    else:
        gridA[
            ...,
            int(gridA_shift_min[0]) : int(gridA_shift_max[0]),
            int(gridA_shift_min[1]) : int(gridA_shift_max[1]),
            int(gridA_shift_min[2]) : int(gridA_shift_max[2]),
        ] = gridB[
            ...,
            int(gridB_shift_min[0]) : int(gridB_shift_max[0]),
            int(gridB_shift_min[1]) : int(gridB_shift_max[1]),
            int(gridB_shift_min[2]) : int(gridB_shift_max[2]),
        ]
        # gridA[..., int(shift[0]):int(shift[0] + gridB.shape[0]), int(shift[1]):int(shift[1] + gridB.shape[1]), int(shift[2]):int(shift[2] + gridB.shape[2])] = gridB


def integrate_grid(gridA, a2w, gridB, b2w, update_fct=None):
    # integrate grid B in to A by checking mapping from A to B
    a_coords = dot(a2w, shape2indices(gridA.shape).reshape(-1, 3))
    a_coords_in_b = points_to_indices(a_coords, b2w)
    valid_mask = np.all(a_coords_in_b >= 0, 1) & np.all(a_coords_in_b < gridB.shape, 1)
    if update_fct == "min":
        gridA[valid_mask.reshape(gridA.shape)] = np.min(
            [gridA[valid_mask.reshape(gridA.shape)], gridB[tuple(a_coords_in_b[valid_mask].T)]], 0
        )
    elif update_fct == "max":
        gridA[valid_mask.reshape(gridA.shape)] = np.max(
            [gridA[valid_mask.reshape(gridA.shape)], gridB[tuple(a_coords_in_b[valid_mask].T)]], 0
        )
    elif update_fct is None:
        gridA[valid_mask.reshape(gridA.shape)] = gridB[tuple(a_coords_in_b[valid_mask].T)]


def downsample_with_invalid(grid, scale_factor, invalid_val=-1):
    valid_inds = np.argwhere(grid != invalid_val)
    grid_valid = grid[grid != invalid_val].reshape(-1)
    interpolated_inds = (scale_factor * valid_inds).astype(np.int)
    down_sampled_grid = invalid_val * np.ones(np.ceil(np.array(grid.shape) * scale_factor).astype(int), dtype=float)

    unique_interp_inds, org2unique_idx = np.unique(interpolated_inds, return_inverse=True, axis=0)
    for i in range(len(unique_interp_inds)):
        down_sampled_grid[tuple(unique_interp_inds[i])] = np.mean(grid_valid[org2unique_idx == i])

    return down_sampled_grid
