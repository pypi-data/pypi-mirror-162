# Copyright 2021 Open Logistics Foundation
#
# Licensed under the Open Logistics License 1.0.
# For details on the licensing terms, see the LICENSE file.

"""
Module for defining a yolox conform Evaluation class, which calculates
the metrics based on the functionality of the MLCVZoo
"""

import logging
from typing import Any, Dict, List, Optional, Tuple, cast

import torch
from mlcvzoo_base.api.data.annotation import BaseAnnotation
from mlcvzoo_base.api.data.bounding_box import BoundingBox
from mlcvzoo_base.data_preparation.annotation_handler import AnnotationClassMapper
from mlcvzoo_base.evaluation.object_detection.data_classes import (
    ODModelEvaluationMetrics,
)
from mlcvzoo_base.evaluation.object_detection.metrics_computation import (
    MetricsComputation,
)
from mlcvzoo_base.evaluation.object_detection.metrics_logging import (
    log_od_metrics_to_mlflow,
)
from mlcvzoo_base.evaluation.object_detection.model_evaluation import (
    evaluate_with_precomputed_data,
)
from torch import Tensor
from torch.cuda import synchronize
from tqdm import tqdm
from yolox.data import DataLoader
from yolox.utils import get_local_rank, is_main_process

from mlcvzoo_yolox.configuration import YOLOXConfig
from mlcvzoo_yolox.data.datasets.dataset import MLCVZooDataset
from mlcvzoo_yolox.model_utils import predict_with_model

logger = logging.getLogger(__name__)


class MLCVZooEvaluator:
    """
    Class for handling the evaluation of an yolox model. It utilizes modules from
    mlcvzoo_base.evaluation.object_detection to produce object detection metrics. The yolox
    Trainer class will instantiate an MLCVZooEvaluator during the training of an yolox
    model. For evaluations after the training TODO
    mlcvzoo_base.evaluation.object_detection.object_detection_evaluator package directly.

    The MLCVZooEvaluator is implemented in the same manner as the COCOEvaluator class of the
    yolox.evaluators.coco_evaluator package. Meaning, the main functions that are called
    from other of modules of the yolox package, follow the same interface.

    NOTE: Since the MLCVZooEvaluator doesn't share any other features of the COCOEvaluator,
          than the evaluate method, an inheritance is not applied. We leave it open to
          define an overall super class in yolox that is defining an overall structure of an
          evaluator.
    """

    def __init__(
        self,
        dataloader: DataLoader,
        configuration: YOLOXConfig,
        mapper: AnnotationClassMapper,
    ) -> None:
        self.dataloader: DataLoader = dataloader
        self.configuration: YOLOXConfig = configuration
        self.mapper: AnnotationClassMapper = mapper

    def __predict_on_dataloader(
        self,
        model: torch.nn.Module,
        half: bool = False,
    ) -> Dict[str, List[BoundingBox]]:

        predict_annotation_dict: Dict[str, List[BoundingBox]] = {}

        tensor_type: Tensor
        if half:
            tensor_type = torch.cuda.HalfTensor  # type: ignore
        else:
            tensor_type = torch.cuda.FloatTensor  # type: ignore

        model = model.eval()
        if half:
            model = model.half()

        progress_bar = tqdm if is_main_process() else iter

        for cur_iter, (imgs, _, info_imgs, ids) in enumerate(
            progress_bar(self.dataloader)
        ):
            with torch.no_grad():  # type: ignore
                imgs = imgs.type(tensor_type)

                _, bounding_boxes = predict_with_model(
                    model=model,
                    data_item=imgs,
                    preprocess=None,
                    inference_config=self.configuration.inference_config,
                    mapper=self.mapper,
                    image_shape=(int(info_imgs[0]), int(info_imgs[1])),
                )

            predict_annotation_dict[info_imgs[2][0]] = bounding_boxes

        return predict_annotation_dict

    def log_metrics(self, model_metrics: ODModelEvaluationMetrics) -> None:

        log_od_metrics_to_mlflow(
            model_specifier="",
            metrics_dict=model_metrics.metrics_dict,
            iou_threshold=0.5,
        )

    def evaluate(
        self,
        model: torch.nn.Module,
        distributed: bool = False,
        half: bool = False,
        trt_file: Optional[str] = None,
        decoder: Optional[Any] = None,
        test_size: Optional[Tuple[int, int]] = None,
    ) -> Tuple[float, float, str]:
        """
        Run the evaluation of the given yolox model. The method structure is conform to the
        COCOEvaluator class of the yolox.evaluators.coco_evaluator package. This is needed so
        that this method can be used by a Trainer instance of the yolox package correctly.

        Args:
            model: The model that should be evaluated
            distributed: Whether the function is executed in a distributed context
            half: Whether the model should be used with half precision
            trt_file: NOT USED FOR NOW, definition is only needed to be compatible to the yolox
                      interface
            decoder: NOT USED FOR NOW, definition is only needed to be compatible to the yolox
                     interface
            test_size: NOT USED FOR NOW, definition is only needed to be compatible to the yolox
                       interface

        Returns:
            1x3 Tuple containing COCO AP of IoU=50-95, COCO AP of IoU=50 and a short summary info of the evaluation
        """

        if not is_main_process():
            logger.debug(
                "process rank='%s'. Not the main process, return default evaluation result"
                % get_local_rank()
            )
            return 0.0, 0.0, ""

        logger.info(
            "Execute yolox evaluation on model: %s"
            % self.configuration.base_config.MODEL_SPECIFIER
        )

        gt_annotation_dict: Dict[str, BaseAnnotation] = cast(
            MLCVZooDataset, self.dataloader.dataset
        ).gt_annotation_dict

        predict_annotation_dict: Dict[
            str, List[BoundingBox]
        ] = self.__predict_on_dataloader(model=model, half=half)

        assert len(gt_annotation_dict) == len(predict_annotation_dict)

        # Compute metrics with iou-thresholds that are needed to determine the COCO mAP
        model_metrics = evaluate_with_precomputed_data(
            model_specifier=self.configuration.base_config.MODEL_SPECIFIER,
            classes_id_dict=self.mapper.annotation_class_id_to_model_class_name_map,
            gt_annotations=list(gt_annotation_dict.values()),
            iou_thresholds=MetricsComputation.iou_thresholds_ap_50_95,
            predicted_bounding_boxes_list=list(predict_annotation_dict.values()),
        )

        self.log_metrics(model_metrics=model_metrics)

        ap50 = MetricsComputation.get_ap_50(model_metrics=model_metrics)
        ap50_95 = MetricsComputation.get_ap_50_95(model_metrics=model_metrics)

        summary = f"COCO mAP={ap50_95}, AP0.5={ap50}"

        if distributed:
            # TODO: check if an extra handling for distributed training is needed
            pass

        logger.debug(
            "process rank='%s'. Waiting synchronisation after evaluation"
            % get_local_rank()
        )
        synchronize()

        return ap50_95, ap50, summary
