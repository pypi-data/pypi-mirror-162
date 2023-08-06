# Copyright 2021 Open Logistics Foundation
#
# Licensed under the Open Logistics License 1.0.
# For details on the licensing terms, see the LICENSE file.

"""
Module that defines a wrapper class for yolox:
https://github.com/Megvii-BaseDetection/YOLOX/
"""

import argparse
import logging
import os
from typing import Any, Dict, List, Optional, Tuple, Union, cast

import numpy as np
import torch
from mlcvzoo_base.api.data.annotation_class_mapper import AnnotationClassMapper
from mlcvzoo_base.api.data.bounding_box import BoundingBox
from mlcvzoo_base.api.interfaces import NetBased, Trainable
from mlcvzoo_base.api.model import ObjectDetectionModel
from mlcvzoo_base.configuration.utils import (
    create_configuration as create_basis_configuration,
)
from yolox.data import ValTransform
from yolox.utils import fuse_model

from mlcvzoo_yolox.configuration import YOLOXConfig, YOLOXTrainArgparseConfig
from mlcvzoo_yolox.exp.custom_yolox_exp import CustomYOLOXExp
from mlcvzoo_yolox.model_utils import predict_with_model
from mlcvzoo_yolox.third_party.yolox.tools.train import main as train_yolox
from mlcvzoo_yolox.third_party.yolox.tools.trt import convert_to_tensorrt

logger = logging.getLogger(__name__)


class YOLOXModel(
    ObjectDetectionModel[YOLOXConfig, Union[str, np.ndarray, torch.Tensor]],  # type: ignore[type-arg]
    NetBased[torch.nn.Module],
    Trainable,
):
    """
    Class to wrap the implementation of yolox
    """

    def __init__(
        self,
        from_yaml: Optional[str] = None,
        configuration: Optional[YOLOXConfig] = None,
        string_replacement_map: Optional[Dict[str, str]] = None,
        init_for_inference: bool = False,
        load_tensorrt_model: bool = False,
    ) -> None:
        """
        Construct a YOLOXModel

        Args:
            from_yaml: (Optional) The yaml path where to parse the YOLOXConfig from
            configuration: (Optional) An ready to use YOLOXConfig object
            string_replacement_map: A dictionary that provides placeholders information that
                                    is needed to build a YOLOXConfig utilizing the ConfigBuilder
            init_for_inference: If the YOLOXModel should be used for inference
            load_tensorrt_model: If the YOLOXModel should use a tensorrt model instead of torch
        """

        self.yaml_config_path = from_yaml
        self.init_for_inference = init_for_inference
        self.net: Optional[torch.nn.Module] = None
        self.decode_output: bool = False
        self.preprocess: Optional[ValTransform] = None

        self.configuration: YOLOXConfig = YOLOXModel.create_configuration(
            from_yaml=from_yaml,
            configuration=configuration,
            string_replacement_map=string_replacement_map,
        )
        # We are internally calling the setter which needs the configuration to exist
        self.load_tensorrt_model = load_tensorrt_model

        mapper = AnnotationClassMapper(
            class_mapping=self.configuration.class_mapping,
            reduction_mapping=self.configuration.inference_config.reduction_class_mapping,
        )
        self.exp: CustomYOLOXExp = CustomYOLOXExp(
            configuration=self.configuration, mapper=mapper
        )
        # The ObjectDetectionModel needs the exp attribute to be initialized beforehand
        ObjectDetectionModel.__init__(
            self,
            unique_name=self.configuration.base_config.MODEL_SPECIFIER,
            configuration=self.configuration,
            init_for_inference=init_for_inference,
            mapper=mapper,
        )
        NetBased.__init__(self, net=self.net)
        Trainable.__init__(self)

    @staticmethod
    def create_configuration(
        from_yaml: Optional[str] = None,
        configuration: Optional[YOLOXConfig] = None,
        string_replacement_map: Optional[Dict[str, str]] = None,
    ) -> YOLOXConfig:
        return cast(
            YOLOXConfig,
            create_basis_configuration(
                configuration_class=YOLOXConfig,
                from_yaml=from_yaml,
                input_configuration=configuration,
                string_replacement_map=string_replacement_map,
            ),
        )

    @property
    def num_classes(self) -> int:
        return self.mapper.num_classes

    def get_classes_id_dict(self) -> Dict[int, str]:
        return self.exp.mapper.annotation_class_id_to_model_class_name_map

    def get_net(self) -> Optional[torch.nn.Module]:
        return self.net

    def store(self, checkpoint_path: str) -> None:
        # TODO: use yolox.utils.checkpoint.save_checkpoint
        pass

    def restore(self, checkpoint_path: str) -> None:
        # TODO: use yolox.utils.checkpoint.load_ckpt?
        if self.load_tensorrt_model:
            self.net = self.__load_trt_checkpoint(checkpoint_path=checkpoint_path)
        else:
            self.net = self.__load_checkpoint(checkpoint_path=checkpoint_path)

    @property
    def load_tensorrt_model(self) -> bool:
        return self._load_tensorrt_model

    @load_tensorrt_model.setter
    def load_tensorrt_model(self, load_tensorrt_model: bool) -> None:

        if load_tensorrt_model and (
            self.configuration.trt_config is None
            or self.configuration.inference_config.device != "gpu"
        ):
            raise ValueError(
                "To load a TensorRT yolox model a trt-config has to be "
                "provided and the inference_config.device has to be set to 'gpu'"
            )

        self._load_tensorrt_model = load_tensorrt_model

    def _init_inference_model(self) -> None:

        self.preprocess = ValTransform(
            legacy=self.configuration.inference_config.legacy
        )

        del self.net
        self.net = None

        if self.load_tensorrt_model:
            if self.configuration.trt_config is None or not os.path.isfile(
                self.configuration.trt_config.trt_checkpoint_path
            ):
                raise ValueError(
                    "In order to init the model with tensorrt, "
                    "a valid trt_config has to be provided"
                )
            checkpoint_path = self.configuration.trt_config.trt_checkpoint_path
        else:
            # Use the torch only yolox model

            self.net = self.exp.get_model()

            if self.configuration.inference_config.device == "gpu":
                self.net.cuda()
                if self.configuration.inference_config.gpu_fp16:
                    self.net.half()  # to FP16
            self.net.eval()

            checkpoint_path = self.configuration.inference_config.checkpoint_path

        self.restore(checkpoint_path=checkpoint_path)

    def __load_trt_checkpoint(self, checkpoint_path: str) -> torch.nn.Module:
        """
        Load the checkpoint for the model

        Returns:
            None
        """
        try:
            # TensorRT is optional, so imported here
            # pylint: disable=C0415
            from torch2trt import TRTModule
        except ImportError as importerror:
            logger.error("Torch2TRT is not installed, no model checkpoint loaded.")
            raise importerror

        logger.info("Load model (trt) checkpoint from: %s", checkpoint_path)

        tensorrt_module = TRTModule()
        state_dict = torch.load(checkpoint_path)  # type: ignore[no-untyped-call]
        tensorrt_module.load_state_dict(state_dict=state_dict)

        # When using a TRT yolox model, the net output has to be decoded in another way.
        # Details can be found in mlcvzoo_yolox.third_party.yolox.models.yolo_head.decode_outputs
        self.decode_output = True

        return cast(torch.nn.Module, tensorrt_module)

    def __load_checkpoint(self, checkpoint_path: str) -> torch.nn.Module:
        """
        Load the checkpoint for the model

        Returns:
            None
        """

        if self.net is None:
            raise ValueError(
                "The net attribute is None, the net has not been initialized for inference"
            )

        net = self.net

        if self.configuration.inference_config.fuse:
            net = fuse_model(net)

        if not os.path.isfile(checkpoint_path):
            raise ValueError(
                f"The given checkpoint path does not exist! checkpoint_path: {checkpoint_path}"
            )

        # load the model state dict
        logger.info("Load model checkpoint from: %s", checkpoint_path)
        net.load_state_dict(
            torch.load(checkpoint_path, map_location="cpu")["model"]  # type: ignore
        )

        return net

    def convert_to_tensorrt(self) -> None:
        """
        Converts the stored torch model instance to tensorrt

        Returns:
            None
        """

        if self.net is None:
            raise ValueError("The net attribute has not yet been initialized!")

        convert_to_tensorrt(
            model=self.net,
            yolox_config=self.configuration,
        )

    def predict(
        self, data_item: Union[str, np.ndarray, torch.Tensor]  # type: ignore[type-arg]
    ) -> Tuple[Union[str, np.ndarray, torch.Tensor], List[BoundingBox]]:  # type: ignore[type-arg]
        """
        Run a yolox model on a given input image and predict a list of
        mlcvzoo conform bounding boxes

        Args:
            data_item: Either the path to an image or an already created numpy image

        Returns:
            The predicted bounding boxes
        """
        if self.net is None:
            raise ValueError("The net attribute has not yet been initialized!")

        return predict_with_model(
            model=self.net,
            data_item=data_item,
            preprocess=self.preprocess,
            inference_config=self.configuration.inference_config,
            decode_output=self.decode_output,
            strides=self.exp.strides,
            mapper=self.exp.mapper,
        )

    def __get_yolox_argparse_namespace(
        self, argparse_config: YOLOXTrainArgparseConfig
    ) -> argparse.Namespace:
        """
        Load the yolox argparse arguments from the given YOLOXTrainArgparseConfig configuration
        object. The attributes of the argparse configuration reflect the argparse commandline
        parameters of yolox/tools/train.py. This makes it easier to be compatible to their API.

        Args:
            argparse_config: The YOLOXTrainArgparseConfig object that should be transformed
                             into a argparse namespace for the yolox training

        Returns:
            the created argparse Namespace
        """

        argparse_dict: Dict[str, Any] = vars(argparse_config)

        # Fill out additional argparse parameters
        argparse_dict["experiment_name"] = self.get_name()
        argparse_dict["name"] = None

        args: argparse.Namespace = argparse.Namespace(**argparse_dict)

        return args

    def train(self) -> None:

        if self.configuration.train_config is None:
            raise ValueError(
                "train_config is None! In order to be able to train a yolox model"
                "a valid train_config has to be provided!"
            )

        train_yolox(
            exp=self.exp,
            args=self.__get_yolox_argparse_namespace(
                argparse_config=self.configuration.train_config.argparse_config
            ),
        )
