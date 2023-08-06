import numpy as np
import torch
from dutils import type_convert, has_torch


def get_iou_box(boxA, boxB):
    """ Compute IoU of two bounding boxes.
    """
    # determine the (x, y, z)-coordinates of the intersection rectangle
    minx_overlap = max(boxA[0], boxB[0])
    miny_overlap = max(boxA[1], boxB[1])
    minz_overlap = max(boxA[2], boxB[2])

    maxx_overlap = min(boxA[3], boxB[3])
    maxy_overlap = min(boxA[4], boxB[4])
    maxz_overlap = min(boxA[5], boxB[5])

    # compute the area of intersection rectangle
    interArea = max(0, maxx_overlap - minx_overlap) * max(0, maxy_overlap - miny_overlap) * max(0, maxz_overlap - minz_overlap)

    # compute the area of both the prediction and ground-truth
    # rectangles
    boxAArea = (boxA[3] - boxA[0]) * (boxA[4] - boxA[1]) * (boxA[5] - boxA[2])
    boxBArea = (boxB[3] - boxB[0]) * (boxB[4] - boxB[1]) * (boxB[5] - boxB[2])

    # compute the intersection over union by taking the intersection
    # area and dividing it by the sum of prediction + ground-truth
    # areas - the interesection area
    iou = interArea / float(boxAArea + boxBArea - interArea)

    # return the intersection over union value
    return iou


def iou3d(boxes, query_boxes):
    box_ares = (boxes[:, 3] - boxes[:, 0]) * (boxes[:, 4] - boxes[:, 1]) * (boxes[:, 5] - boxes[:, 2])
    query_ares = (
        (query_boxes[:, 3] - query_boxes[:, 0])
        * (query_boxes[:, 4] - query_boxes[:, 1])
        * (query_boxes[:, 5] - query_boxes[:, 2])
    )

    if type(boxes) == torch.Tensor:
        iw = (torch.min(boxes[:, 3], query_boxes[:, 3]) - torch.max(boxes[:, 0], query_boxes[:, 0])).clamp(min=0)
        ih = (torch.min(boxes[:, 4], query_boxes[:, 4]) - torch.max(boxes[:, 1], query_boxes[:, 1])).clamp(min=0)
        il = (torch.min(boxes[:, 5], query_boxes[:, 5]) - torch.max(boxes[:, 2], query_boxes[:, 2])).clamp(min=0)
        ua = (box_ares + query_ares - iw * ih * il).float()

    else:
        iw = (np.min([boxes[:, 3], query_boxes[:, 3]], axis=0) - np.max([boxes[:, 0], query_boxes[:, 0]], axis=0)).clip(min=0)
        ih = (np.min([boxes[:, 4], query_boxes[:, 4]], axis=0) - np.max([boxes[:, 1], query_boxes[:, 1]], axis=0)).clip(min=0)
        il = (np.min([boxes[:, 5], query_boxes[:, 5]], axis=0) - np.max([boxes[:, 2], query_boxes[:, 2]], axis=0)).clip(min=0)
        ua = (box_ares + query_ares - iw * ih * il).astype(np.float)
    overlaps = iw * ih * il / ua
    return overlaps


def vols_AABB(boxes):
    return (boxes[:, 3] - boxes[:, 0]) * (boxes[:, 4] - boxes[:, 1]) * (boxes[:, 5] - boxes[:, 2])


def ious_AABB(boxesA, boxesB):
    if len(boxesA) == 0 or len(boxesB) == 0:
        return None
    if isinstance(boxesA, list):
        if has_torch(*boxesA):
            boxesA = torch.stack(boxesA, 0)
        else:
            boxesA = np.stack(boxesA, 0)
    if isinstance(boxesB, list):
        if has_torch(*boxesB):
            boxesB = torch.stack(boxesB, 0)
        else:
            boxesB = np.stack(boxesB, 0)

    volA = vols_AABB(boxesA)
    volB = vols_AABB(boxesB)

    if has_torch(boxesA):
        lt = torch.max(boxesA[:, None, :3], boxesB[:, :3])
        rb = torch.min(boxesA[:, None, 3:6], boxesB[:, 3:6])
        wh = (rb - lt).clamp(min=0)
    else:
        lt = np.stack([np.tile(boxesA[:, None, :3], (1, len(boxesB), 1)), np.repeat(boxesB[None, :, :3], len(boxesA), 0)], 0).max(
            0
        )
        rb = np.stack(
            [np.tile(boxesA[:, None, 3:6], (1, len(boxesB), 1)), np.repeat(boxesB[None, :, 3:6], len(boxesA), 0)], 0
        ).min(0)
        wh = (rb - lt).clip(min=0)
    inter = wh[:, :, 0] * wh[:, :, 1] * wh[:, :, 2]
    if has_torch(inter):
        iou = inter.float() / (volA[:, None] + volB - inter).float()
    else:
        iou = inter.astype(float) / (volA[:, None] + volB - inter).astype(float)
    return iou


if __name__ == "__main__":
    print(
        ious_AABB(
            torch.Tensor([[1, 2, 3, 10, 50, 60], [0, 0, 0, 10, 20, 20]]),
            torch.Tensor([[0, 0, 0, 10, 50, 60], [3, 3, 3, 10, 20, 30], [0, 0, 0, 10, 20, 20], [0, 0, 0, 10, 20, 20]]),
        )
    )

    print(
        ious_AABB(
            np.array([[1, 2, 3, 10, 50, 60], [0, 0, 0, 10, 20, 20]]),
            np.array([[0, 0, 0, 10, 50, 60], [3, 3, 3, 10, 20, 30], [0, 0, 0, 10, 20, 20], [0, 0, 0, 10, 20, 20]]),
        )
    )

    print(
        ious_AABB(
            [torch.Tensor([1, 2, 3, 10, 50, 60]), torch.Tensor([0, 0, 0, 10, 20, 20])],
            torch.Tensor([[0, 0, 0, 10, 50, 60], [3, 3, 3, 10, 20, 30], [0, 0, 0, 10, 20, 20], [0, 0, 0, 10, 20, 20]]),
        )
    )
