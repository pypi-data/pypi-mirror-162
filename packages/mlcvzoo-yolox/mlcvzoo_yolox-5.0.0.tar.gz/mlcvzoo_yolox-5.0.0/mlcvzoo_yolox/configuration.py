# Copyright 2021 Open Logistics Foundation
#
# Licensed under the Open Logistics License 1.0.
# For details on the licensing terms, see the LICENSE file.

"""
Module for defining configuration classes that define the behavior of a yolox model
"""

from typing import Any, Dict, List, Optional

import related
from config_builder.BaseConfigClass import BaseConfigClass
from loguru import logger
from mlcvzoo_base.api.configuration import Configuration
from mlcvzoo_base.configuration.annotation_handler_config import AnnotationHandlerConfig
from mlcvzoo_base.configuration.class_mapping_config import ClassMappingConfig
from mlcvzoo_base.configuration.detector_configs import DetectorConfig
from mlcvzoo_base.configuration.reduction_mapping_config import ReductionMappingConfig

from mlcvzoo_yolox.exp.default import YOLOXExperiments


@related.mutable(strict=True)
class YOLOXExperimentConfig(BaseConfigClass):
    # Type of the yolox experiments that should be used as base experiment
    exp_type: str = related.StringField()
    # name of your experiment
    exp_name: Optional[str] = related.StringField(required=False, default=None)

    # Dictionary for overwriting attributes of the loaded
    # base experiment
    attribute_overwrite: Dict[str, Any] = related.ChildField(
        cls=dict, default={}, required=False
    )

    def check_values(self) -> bool:

        if self.exp_type not in [str(d.upper()) for d in YOLOXExperiments]:  # type: ignore
            raise ValueError(
                f"Exp-type='{self.exp_type}' not valid. Please provide one of "  # type: ignore
                f"{[str(d.upper()) for d in YOLOXExperiments]}"
            )

        if self.exp_name is None:
            logger.warning(
                "DEPRECATED: The exp_name attribute is deprecated "
                "and will be removed in future versions "
            )

        return True


@related.mutable(strict=True)
class YOLOXInferenceConfig(BaseConfigClass):
    input_dim: List[int] = related.SequenceField(cls=int)

    checkpoint_path: str = related.StringField()

    score_threshold: float = related.FloatField()
    nms_threshold: float = related.FloatField()

    device: str = related.StringField()
    gpu_fp16: bool = related.BooleanField()
    fuse: bool = related.BooleanField()
    legacy: bool = related.BooleanField(default=False)

    reduction_class_mapping: Optional[ReductionMappingConfig] = related.ChildField(
        cls=ReductionMappingConfig, required=False, default=None
    )

    def check_values(self) -> bool:
        return self.device in ["gpu", "cpu"] and len(self.input_dim) == 2


@related.mutable(strict=True)
class YOLOXTRTConfig(BaseConfigClass):
    trt_checkpoint_path: str = related.StringField()
    trt_engine_path: str = related.StringField()

    # Size of workspace
    workspace: int = related.IntegerField(default=32)
    # Size of batch
    batch: int = related.IntegerField(default=1)
    # Convert to int 8?
    int8: bool = related.BooleanField(default=False)
    # Convert to float 16?
    fp16: bool = related.BooleanField(default=True)


@related.mutable(strict=True)
class YOLOXTrainArgparseConfig(BaseConfigClass, Configuration):
    """
    argparse parameter as stated in yolox/tools/train.py

    """

    # NOTE: This is here to indicate that we did not forget the "exp_file" and "experiment_name"
    #       argparse parameter. Since we are using the YOLOXExperimentConfig to define one
    #       experiment config for inference as well as fore training, we are creating a
    #       correct argparse dictionary at runtime, using the information from the given
    #       YOLOXExperimentConfig.
    # exp_file: str = related.StringField()
    # experiment_name: str = related.StringField()

    # NOTE: This is here to indicate that we did not forget the "name" argparse parameter.
    #       It is used in yolox for parsing a config with the given name. Since we will not
    #       make use of this feature, we don't have to specify it here
    # name: Optional[str] = related.StringField(default=None, required=False)

    # batch-size to train on
    batch_size: int = related.IntegerField()
    # distributed backend
    dist_backend: str = related.StringField(default="nccl")
    # url used to set up distributed training
    dist_url: Optional[str] = related.StringField(default=None, required=False)
    # (number of) devices for training
    devices: Optional[int] = related.IntegerField(default=None, required=False)
    # resume training
    resume: bool = related.BooleanField(default=False)
    # checkpoint file to load
    ckpt: Optional[str] = related.StringField(default=None, required=False)
    # resume training start epoch
    start_epoch: Optional[int] = related.IntegerField(default=None, required=False)
    # num of node for training
    num_machines: int = related.IntegerField(default=1)
    # node rank for multi-node training
    machine_rank: int = related.IntegerField(default=0)
    # Adopting mix precision training
    fp16: bool = related.BooleanField(default=False)
    # Caching imgs to RAM for fast training
    cache: bool = related.BooleanField(default=False)
    # occupy GPU memory first for training
    occupy: bool = related.BooleanField(default=False)
    # Logger to be used for metrics
    logger: str = related.StringField(default="tensorboard")


@related.mutable(strict=True)
class YOLOXTrainConfig(BaseConfigClass, Configuration):

    argparse_config: YOLOXTrainArgparseConfig = related.ChildField(
        cls=YOLOXTrainArgparseConfig
    )

    train_annotation_handler_config: AnnotationHandlerConfig = related.ChildField(
        cls=AnnotationHandlerConfig
    )

    test_annotation_handler_config: AnnotationHandlerConfig = related.ChildField(
        cls=AnnotationHandlerConfig
    )

    output_dir: Optional[str] = related.StringField(required=False, default=None)

    def check_values(self) -> bool:

        if self.output_dir is None:
            logger.debug(
                "The YOLOXTrainConfig.output_dir is set to None. "
                "Therefore the yolox trainer will use the output_dir"
                "which is specified in the configuration attribute"
                " YOLOXTrainConfig.argparse_config.exp_file"
            )

        return True


@related.mutable(strict=True)
class YOLOXConfig(BaseConfigClass, Configuration):
    class_mapping: ClassMappingConfig = related.ChildField(cls=ClassMappingConfig)

    experiment_config: YOLOXExperimentConfig = related.ChildField(
        cls=YOLOXExperimentConfig
    )

    inference_config: YOLOXInferenceConfig = related.ChildField(
        cls=YOLOXInferenceConfig
    )

    trt_config: Optional[YOLOXTRTConfig] = related.ChildField(
        cls=YOLOXTRTConfig, required=False, default=None
    )

    train_config: Optional[YOLOXTrainConfig] = related.ChildField(
        cls=YOLOXTrainConfig, required=False, default=None
    )

    base_config: DetectorConfig = related.ChildField(
        cls=DetectorConfig, default=DetectorConfig()
    )
