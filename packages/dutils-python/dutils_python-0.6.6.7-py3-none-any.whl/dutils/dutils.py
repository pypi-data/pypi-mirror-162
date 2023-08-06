import torch
import numpy as np


def type_convert(*args, to_torch=True, to_cuda=True):
    converted_args = []
    if to_torch:
        if any([isinstance(x, torch.Tensor) for x in args]):
            devices = set([x.device for x in args if isinstance(x, torch.Tensor)])
            if torch.device("cpu") in devices:
                devices.remove(torch.device("cpu"))
            if len(devices) > 1:
                raise IOError("Cannot convert: Several GPU devices found")
            if len(devices) == 0:
                gpu_device = torch.device("cuda")
            else:
                gpu_device = devices.pop()
            for x in args:
                if isinstance(x, np.ndarray):
                    x = torch.from_numpy(x)
                    if x.dtype == torch.double:
                        x = x.float()
                if to_cuda and (x.device != gpu_device):
                    x = x.to(gpu_device)
                converted_args.append(x)
        # quick solution
        if any([x.dtype.is_floating_point for x in converted_args]):
            for i in range(len(converted_args)):
                converted_args[i] = converted_args[i].float()

    else:
        # all as numpy arrays
        for x in args:
            if isinstance(x, torch.Tensor):
                x = x.cpu().numpy()
            converted_args.append(x)
        common_type = np.find_common_type([x.dtype for x in converted_args], [])
        for i in range(len(converted_args)):
            converted_args[i] = converted_args[i].astype(common_type)
    return converted_args


def has_torch(*args):
    return any([isinstance(x, torch.Tensor) for x in args])


def torch_isin(a, b):
    b = b.squeeze()
    return (a[..., None] == b).any(-1)


def filter_with_map(a, mask, out_map=True, in_map=True):
    # out_map: filt2org: return the in_indices corresponding to a[mask] (injective)
    # in_map: org2filt: return the out_indices corresponding to a (-1 for invalid)
    if has_torch(a):
        filt2org = mask.nonzero().squeeze(0)
    else:
        filt2org = np.argwhere(mask)

    if not in_map:  # only mapping a[mask] -> a
        if out_map:
            return a[mask], filt2org
        return a[mask]
    # compute mapping a -> a[mask]
    if has_torch(a):
        org2filt = torch.cumsum(mask, 0) - 1
    else:
        org2filt = np.cumsum(mask, 0) - 1

    org2filt[~mask] = -1
    if out_map:
        return a[mask], filt2org, org2filt
    return a[mask], org2filt


def dims(elements):
    dim_list = []
    for elem in elements:
        if has_torch(elem):
            dim_list.append(elem.dim())
        else:
            dim_list.append(len(elem.shape))
    return dim_list


def get_dim(elem):
    if has_torch(elem):
        return elem.dim()
    return len(elem.shape)


def cat(elements, *args, **kwargs):
    ignore_none = kwargs.get("ignore_none", False)
    if len(elements) == 0:
        return torch.empty(0)
    dim_list = dims(elements)
    dim = kwargs.get("dim", kwargs.get("axis", args[0] if len(args) > 0 else 0))

    max_dim = max(max(dim_list), dim + 1)
    reshaped_elements = []
    for elem in elements:
        if elem is None:
            if ignore_none:
                continue
            else:
                raise IOError("None in input list encountered: maybe set ignore_none=True")

        if get_dim(elem) == max_dim - 1:
            if has_torch(elem):
                reshaped_elements.append(elem.unsqueeze(dim))
            else:
                reshaped_elements.append(np.expand_dims(elem, dim))
        else:
            reshaped_elements.append(elem)
    if has_torch(*elements):
        return torch.cat(type_convert(*reshaped_elements), dim=dim)
    return np.concatenate(reshaped_elements, axis=dim)


def unique_agg(coords, feats, agg="mean"):
    unique_coords, all2unique, unique_counts = torch.unique(coords, dim=0, return_inverse=True, return_counts=True)
    temp_sparse = torch.sparse.FloatTensor(torch.stack([all2unique, torch.arange(len(all2unique)).to(all2unique)], 0), feats)
    if agg == "sum":
        agg_feats = torch.sparse.sum(temp_sparse, 1).values()
    elif agg == "mean":
        agg_feats = torch.sparse.sum(temp_sparse, 1).values() / unique_counts.unsqueeze(1)
    else:
        raise NotImplementedError
    return unique_coords, agg_feats


def majority_agg(coords, labels):
    unique_coords, all2unique, unique_counts = torch.unique(coords, dim=0, return_inverse=True, return_counts=True)
    unique_labels, all2unique_labels = torch.unique(labels, return_inverse=True)
    continuous_labels = torch.arange(len(unique_labels)).to(unique_labels)

    temp_sparse = torch.sparse.FloatTensor(
        torch.stack([all2unique, torch.arange(len(all2unique)).to(all2unique), all2unique_labels], 0),
        torch.ones(len(all2unique_labels)).to(labels),
    )
    continuous_maj = torch.sparse.sum(temp_sparse, 1).to_dense().argmax(1)
    return (unique_coords, unique_labels[continuous_maj])

def tensor_mem(tensor, grad_sep=False):
    grad_mem = 0
    if tensor.grad is not None:
        grad_mem = tensor_mem(tensor.grad)
    numel = tensor.storage().size()
    element_size = tensor.storage().element_size()
    mem = numel * element_size / 1024 / 1024  # 32bit=4Byte, MByte
    if grad_sep:
        return np.array([mem, grad_mem], dtype=np.float64)
    return mem + grad_mem


def mem_report(container, grad_sep=False):
    if grad_sep:
        total_mem = np.array([0, 0], dtype=np.float64)
    else:
        total_mem = 0
    if isinstance(container, (list, tuple)):
        for elem in container:
            total_mem += mem_report(elem, grad_sep)
    elif isinstance(container, dict):
        for elem_name, elem in container.items():
            total_mem += mem_report(elem, grad_sep)
    elif isinstance(container, torch.Tensor):
        total_mem += tensor_mem(container, grad_sep)
    elif isinstance(container, torch.nn.Module):
        for name, param in container.named_parameters():
            total_mem += mem_report(param, grad_sep)
    else:
        pass

    return total_mem
