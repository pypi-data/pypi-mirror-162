# Copyright (c) Megvii, Inc. and its affiliates.

import torch
import torch.distributed as dist
from yolox.data import (
    DataLoader,
    InfiniteSampler,
    MosaicDetection,
    TrainTransform,
    VOCDetection,
    YoloBatchSampler,
    worker_init_reset_seed,
)
from yolox.exp import Exp as MyExp


def get_data_loader(
    exp: MyExp,
    dataset: VOCDetection,
    batch_size: int,
    is_distributed: bool,
    no_aug: bool = False,
) -> DataLoader:
    """
    Functionality taken from:

    https://github.com/Megvii-BaseDetection/YOLOX/blob/dd5700c24693e1852b55ce0cb170342c19943d8b/
    yolox/exp/yolox_base.py#L122-L163

    The data loading has to be compatible to the original implementation to achieve the
    same training results.

    Args:
        exp:
        dataset:
        batch_size:
        is_distributed:
        no_aug:

    Returns:

    """

    dataset = MosaicDetection(
        dataset,
        mosaic=not no_aug,
        img_size=exp.input_size,
        preproc=TrainTransform(
            max_labels=120, flip_prob=exp.flip_prob, hsv_prob=exp.hsv_prob
        ),
        degrees=exp.degrees,
        translate=exp.translate,
        mosaic_scale=exp.mosaic_scale,
        mixup_scale=exp.mixup_scale,
        shear=exp.shear,
        enable_mixup=exp.enable_mixup,
        mosaic_prob=exp.mosaic_prob,
        mixup_prob=exp.mixup_prob,
    )

    exp.dataset = dataset

    if is_distributed:
        batch_size = batch_size // dist.get_world_size()  # type: ignore

    sampler = InfiniteSampler(len(exp.dataset), seed=exp.seed if exp.seed else 0)

    batch_sampler = YoloBatchSampler(
        sampler=sampler,
        batch_size=batch_size,
        drop_last=False,
        mosaic=not no_aug,
    )

    dataloader_kwargs = {"num_workers": exp.data_num_workers, "pin_memory": True}
    dataloader_kwargs["batch_sampler"] = batch_sampler

    # Make sure each process has different random seed, especially for 'fork' method
    dataloader_kwargs["worker_init_fn"] = worker_init_reset_seed

    train_loader = DataLoader(exp.dataset, **dataloader_kwargs)

    return train_loader


def get_eval_loader(
    valdataset: VOCDetection,
    data_num_workers: int,
    batch_size: int,
    is_distributed: bool,
    testdev: bool = False,
    legacy: bool = False,
) -> DataLoader:
    """
    Functionality taken from:

    https://github.com/Megvii-BaseDetection/YOLOX/blob/dd5700c24693e1852b55ce0cb170342c19943d8b/
    yolox/exp/yolox_base.py#L251-L267

    The data loading has to be compatible to the original implementation to achieve the
    same training results.

    Args:
        valdataset:
        batch_size:
        is_distributed:
        testdev:
        legacy:

    Returns:

    """

    if is_distributed:
        batch_size = batch_size // dist.get_world_size()  # type: ignore
        sampler = torch.utils.data.distributed.DistributedSampler(  # type: ignore
            valdataset, shuffle=False
        )
    else:
        sampler = torch.utils.data.SequentialSampler(valdataset)  # type: ignore

    dataloader_kwargs = {
        "num_workers": data_num_workers,
        "pin_memory": True,
        "sampler": sampler,
        "batch_size": batch_size,
    }
    val_loader = torch.utils.data.DataLoader(valdataset, **dataloader_kwargs)  # type: ignore

    return val_loader
