# Copyright (c) Megvii, Inc. and its affiliates.

import argparse
import logging
import random
import warnings

import torch
import torch.backends.cudnn as cudnn
from loguru import logger
from yolox.utils import configure_nccl, configure_omp

from mlcvzoo_yolox.exp.custom_yolox_exp import CustomYOLOXExp

python_logger = logging.getLogger(__name__)


@logger.catch
def main(exp: CustomYOLOXExp, args: argparse.Namespace) -> None:
    """
    Functionality mainly from:
    https://github.com/Megvii-BaseDetection/YOLOX/blob/dd5700c24693e1852b55ce0cb170342c19943d8b/
    tools/train.py#L92-L110

    Main difference to the original: instantiate our own trainer instance
    TODO: Create pull request @ https://github.com/Megvii-BaseDetection/YOLOX

    Args:
        exp:
        args:

    Returns:

    """

    if exp.seed is not None:
        random.seed(exp.seed)
        torch.manual_seed(exp.seed)
        cudnn.deterministic = True
        warnings.warn(
            "You have chosen to seed training. This will turn on the CUDNN deterministic setting, "
            "which can slow down your training considerably! You may see unexpected behavior "
            "when restarting from checkpoints."
        )

    # set environment variables for distributed training
    configure_nccl()
    configure_omp()
    cudnn.benchmark = True

    try:
        trainer = exp.get_trainer(args)
        trainer.train()
    except Exception as e:
        # TODO: add return value?
        python_logger.exception(e)
        raise e
