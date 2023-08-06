#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# Copyright (c) 2014-2021 Megvii Inc. All rights reserved.


"""
This module is used to source out the conversion of yolox models to TensorRT and is derived from

https://github.com/Megvii-BaseDetection/YOLOX/blob/c4298f800d99ddc930267d8503d49b4dc06cff48/tools/trt.py
"""

import torch
from loguru import logger

from mlcvzoo_yolox.configuration import YOLOXConfig


def convert_to_tensorrt(model: torch.nn.Module, yolox_config: YOLOXConfig) -> None:
    """
    Take a yolox torch model and convert it to a TensorRT model. Save the relevant
    files according to the given YOLOXConfig.

    Mainly copied from tools/trt.py

    Args:
        model: The torch model to convert
        yolox_config: The YOLOXConfig storing the relevant parameter information for the
                      conversion

    Returns:
        None
    """
    try:
        # TensorRT is optional, so imported here
        # pylint: disable=C0415
        from torch2trt import torch2trt
    except ImportError as importerror:
        logger.error("Torch2TRT is not installed, model not converted.")
        raise importerror

    # TensorRT including conversion only runs on NVIDIA GPU
    if not torch.cuda.is_available():
        raise ValueError(
            "In order to be able to convert the yolox model to tensorrt, "
            "CUDA must be available."
        )

    if yolox_config.trt_config is None:
        raise ValueError(
            "In order to be able to convert the yolox model to tensorrt, "
            "the trt_config attribute has to be specified."
        )

    logger.debug("Start torch2trt conversion")

    model.eval()
    model.cuda()

    # NOTE: This attribute is set by the yolox package
    model.head.decode_in_inference = False  # type: ignore[union-attr]

    x = torch.ones(
        (
            1,
            3,
            yolox_config.inference_config.input_dim[0],
            yolox_config.inference_config.input_dim[1],
        )
    ).cuda()

    model_trt = torch2trt(
        model,
        [x],
        fp16_mode=yolox_config.trt_config.fp16,
        int8_mode=yolox_config.trt_config.int8,
        max_workspace_size=(1 << yolox_config.trt_config.workspace),
        max_batch_size=yolox_config.trt_config.batch,
    )

    logger.info(
        "Save (torch) TensorRT model to: '%s'"
        % yolox_config.trt_config.trt_checkpoint_path
    )
    torch.save(model_trt.state_dict(), yolox_config.trt_config.trt_checkpoint_path)
    with open(yolox_config.trt_config.trt_engine_path, "wb") as f:
        f.write(model_trt.engine.serialize())

    logger.info(
        "Save TensorRT engine file to: '%s'." % yolox_config.trt_config.trt_engine_path
    )

    del model
