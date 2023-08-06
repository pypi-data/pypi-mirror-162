# Copyright 2021 Open Logistics Foundation
#
# Licensed under the Open Logistics License 1.0.
# For details on the licensing terms, see the LICENSE file.

"""
Module for defining a experiment/configuration class to handle the settings
of the yolox package and the mlcvzoo_base It will handle the settings that are
defined for the yolox experiment class "yolox.exp.Exp" and the mlcvzoo
configuration class "mlcvzoo_yolox.configuration.YOLOXConfig".
"""
import argparse
from typing import Any, List, Type

from mlcvzoo_base.api.data.annotation_class_mapper import AnnotationClassMapper
from mlcvzoo_base.data_preparation.annotation_handler import AnnotationHandler
from yolox.data import DataLoader, TrainTransform
from yolox.exp import Exp as YOLOXExp
from yolox.utils import get_local_rank, wait_for_the_master

from mlcvzoo_yolox.configuration import YOLOXConfig
from mlcvzoo_yolox.data.datasets.dataset import MLCVZooDataset
from mlcvzoo_yolox.evaluators.evaluator import MLCVZooEvaluator
from mlcvzoo_yolox.exp.default import yolox_experiment_settings
from mlcvzoo_yolox.third_party.yolox.exps.yolox_base import (
    get_data_loader as get_yolox_data_loader,
)
from mlcvzoo_yolox.third_party.yolox.exps.yolox_base import (
    get_eval_loader as get_yolox_eval_loader,
)


class CustomYOLOXExp(YOLOXExp):
    """
    Define a configuration/experiment base class for yolox experiments in the mlcvzoo.
    """

    def __init__(
        self,
        configuration: YOLOXConfig,
        mapper: AnnotationClassMapper,
        evaluator_type: Type[MLCVZooEvaluator] = MLCVZooEvaluator,
    ) -> None:
        YOLOXExp.__init__(self)
        # ========================================================
        # Custom MLCVZoo yolox attributes
        self.configuration: YOLOXConfig = configuration
        self.mapper = mapper

        # Interval for logging yolox checkpoints
        self.checkpoint_interval = 2
        # strides used to convert a yolox model to a TensorRT model
        self.strides: List[int] = [8, 16, 32]

        # ========================================================
        # Initialization of yolox experiment parameters
        self.__sub_experiment = yolox_experiment_settings[
            self.configuration.experiment_config.exp_type
        ].constructor()

        # overwrite experiment defaults
        for key, value in yolox_experiment_settings[
            self.configuration.experiment_config.exp_type
        ].attribute_dict.items():
            self.__sub_experiment.__dict__[key] = value

        for key, value in self.__sub_experiment.__dict__.items():
            self.__dict__[key] = value

        for (
            key,
            value,
        ) in self.configuration.experiment_config.attribute_overwrite.items():
            if key not in self.__dict__:
                raise ValueError(
                    "Can not overwrite attribute '%s' since is it not defined for "
                    "the experiment! Pleas remove it from the configuration "
                    "dictionary configuration.experiment_config.attribute_overwrite"
                    % key
                )
            self.__dict__[key] = value

        # ========================================================
        # Adaptation / overwrite of yolox attributes

        # NOTE: In the "yolox.exp.Exp" class the dataset attribute is
        #       defined without a type hint, therefore state the type here
        self.dataset: MLCVZooDataset

        # Overwrite the num_classes attribute of the yolox Exp class
        self.num_classes = self.mapper.num_classes
        self.__sub_experiment.num_classes = self.mapper.num_classes

        self.exp_name = self.configuration.base_config.MODEL_SPECIFIER

        if (
            self.configuration.train_config is not None
            and self.configuration.train_config.output_dir is not None
        ):
            self.output_dir = self.configuration.train_config.output_dir

        self.model = self.__sub_experiment.get_model()

        self.evaluator_type: Type[MLCVZooEvaluator] = evaluator_type

    def get_trainer(self, args: argparse.Namespace) -> Any:
        from mlcvzoo_yolox.core.trainer import YoloxTrainer

        return YoloxTrainer(exp=self, args=args)

    def get_data_loader(
        self,
        batch_size: int,
        is_distributed: bool,
        no_aug: bool = False,
        cache_img: bool = False,
    ) -> DataLoader:
        """
        Produce a yolox conform dataloader based on the datastructures of the mlcvzoo.
        This dataloader is intended to be used for a training of a yolox model. It is
        mainly defined by the data that is configured in the configuration attribute
        "configuration.train_config.train_annotation_handler_config" of the yolox configuration.

        Args:
            batch_size: The batch size that should be used during training
            is_distributed: Whether to the training will be fulfilled in a distributed manner
            no_aug: Whether to augmentation steps should be used
            cache_img: Whether to the yolox caching mechanism for images should be used

        Returns:
            The produced dataloader instance
        """

        local_rank = get_local_rank()

        if self.configuration.train_config is None:
            raise ValueError(
                "train_config is None! In order to be able to train a yolox model"
                "a valid train_config has to be provided!"
            )

        with wait_for_the_master(local_rank):

            dataset = MLCVZooDataset(
                annotation_handler=AnnotationHandler(
                    mapper=self.mapper,
                    configuration=self.configuration.train_config.train_annotation_handler_config,
                ),
                img_size=self.input_size,
                preproc=TrainTransform(
                    max_labels=50, flip_prob=self.flip_prob, hsv_prob=self.hsv_prob
                ),
                cache=cache_img,
            )

        return get_yolox_data_loader(
            exp=self,
            dataset=dataset,
            batch_size=batch_size,
            is_distributed=is_distributed,
            no_aug=no_aug,
        )

    def get_eval_loader(
        self,
        batch_size: int,
        is_distributed: bool,
        testdev: bool = False,
        legacy: bool = False,
    ) -> DataLoader:
        """
        Produce a yolox conform dataloader based on the datastructures of the mlcvzoo.
        This dataloader is intended to be used for an evaluation during the training of a yolox
        model. It is mainly defined by the data that is configured in the configuration attribute
        "configuration.train_config.test_annotation_handler_config" of the yolox configuration.

        Args:
            batch_size: The batch size that should be used during training
            is_distributed: Whether to the training will be fulfilled in a distributed manner
            testdev: NOT USED HERE. This is only needed to be conform to the super class method
            legacy: Whether to the ValTransform should be used in legacy mode or not

        Returns:
            The produced dataloader instance
        """

        from yolox.data import ValTransform

        if self.configuration.train_config is None:
            raise ValueError(
                "train_config is None! In order to be able to train a yolox model"
                "a valid train_config has to be provided!"
            )

        return get_yolox_eval_loader(
            data_num_workers=self.data_num_workers,
            valdataset=MLCVZooDataset(
                annotation_handler=AnnotationHandler(
                    mapper=self.mapper,
                    configuration=self.configuration.train_config.test_annotation_handler_config,
                ),
                img_size=self.input_size,
                preproc=ValTransform(legacy=legacy),
                cache=False,
            ),
            batch_size=1,  # NOTE: Batch inference is not implemented for now!
            is_distributed=is_distributed,
            testdev=testdev,
            legacy=legacy,
        )

    def get_evaluator(
        self,
        batch_size: int,
        is_distributed: bool,
        testdev: bool = False,
        legacy: bool = False,
    ) -> MLCVZooEvaluator:
        """
        Produce a yolox conform evaluator that is conform with the structures of the mlcvzoo.

        Args:
            batch_size: The batch size that should be used during training
            is_distributed: Whether to the training will be fulfilled in a distributed manner
            testdev: NOT USED HERE. This is only needed to be conform to the super class method
            legacy: Whether to the ValTransform should be used in legacy mode or not

        Returns:
            The produced evaluator instance
        """

        evaluator = self.evaluator_type(
            dataloader=self.get_eval_loader(
                batch_size=batch_size,
                is_distributed=is_distributed,
                testdev=testdev,
                legacy=legacy,
            ),
            configuration=self.configuration,
            mapper=self.mapper,
        )

        return evaluator
