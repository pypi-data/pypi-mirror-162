#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# Copyright (c) 2014-2021 Megvii Inc. All rights reserved.

from typing import Any, List

import torch


def decode_outputs(
    output_dim: List[List[int]], strides_list: List[int], outputs: Any, dtype: Any
) -> Any:
    """
    Copy code from yolox/models/yolo_head.YOLOXHead in order to use be able to decode
    the output for yolox models that have been converted with TensorRT.

    Args:
        output_dim:
        strides_list:
        outputs:
        dtype:

    Returns:
        The decoded outputs
    """

    grids = []
    strides = []

    for (hsize, wsize), stride in zip(output_dim, strides_list):
        yv, xv = torch.meshgrid([torch.arange(hsize), torch.arange(wsize)])
        grid = torch.stack((xv, yv), 2).view(1, -1, 2)
        grids.append(grid)
        shape = grid.shape[:2]
        strides.append(torch.full((*shape, 1), stride))

    grids = torch.cat(grids, dim=1).type(dtype)
    strides = torch.cat(strides, dim=1).type(dtype)

    outputs[..., :2] = (outputs[..., :2] + grids) * strides
    outputs[..., 2:4] = torch.exp(outputs[..., 2:4]) * strides

    return outputs
