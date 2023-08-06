# Copyright 2021 Open Logistics Foundation
#
# Licensed under the Open Logistics License 1.0.
# For details on the licensing terms, see the LICENSE file.

from typing import Any, Dict, List, Optional, Tuple

import cv2
import numpy as np
from mlcvzoo_base.api.data.annotation import BaseAnnotation
from mlcvzoo_base.configuration.annotation_handler_config import AnnotationHandlerConfig
from mlcvzoo_base.data_preparation.annotation_handler import AnnotationHandler
from yolox.data.datasets import VOCDetection
from yolox.data.datasets.datasets_wrapper import Dataset


class MLCVZooDataset(VOCDetection):

    """
    Provide dataset that can be used to train a yolox model based on the
    data structure of the MLCVZoo
    """

    def __init__(
        self,
        annotation_handler: AnnotationHandler,
        img_size: Tuple[int, int] = (416, 416),
        preproc: Optional[Any] = None,
        cache: bool = False,
    ) -> None:
        Dataset.__init__(self, img_size)

        self.img_size = img_size
        self.preproc = preproc

        self.annotation_handler = annotation_handler

        self.base_annotations: List[
            BaseAnnotation
        ] = self.annotation_handler.parse_training_annotations()

        self.annotations = self._load_coco_annotations()

        self.gt_annotation_dict: Dict[str, BaseAnnotation] = {}
        for gt_annotation in self.base_annotations:
            self.gt_annotation_dict[gt_annotation.image_path] = gt_annotation

        self.imgs = None
        if cache:
            self._cache_images()

    def __len__(self) -> int:
        return len(self.base_annotations)

    def _load_coco_annotations(
        self,
    ) -> List[Tuple[np.ndarray, Tuple[int, int, str], Tuple[int, int]]]:  # type: ignore[type-arg]
        """
        Overwrite the _load_coco_annotations method to be conform to the
        datastructures of the MLCVZooDataset

        Returns:
            the List of annotations needed to train a yolox model
        """

        return [
            self.load_anno_from_ids(_ids) for _ids in range(len(self.base_annotations))
        ]

    def load_anno_from_ids(
        self, index: int
    ) -> Tuple[np.ndarray, Tuple[int, int, str], Tuple[int, int]]:  # type: ignore[type-arg]
        """
        Overwrite the load_anno_from_ids method to be conform to the
        datastructures of the MLCVZooDataset.

        It will transform a single annotation the is identified by the given index.

        Args:
            index: The index to address the annotation from the global list of annotations

        Returns:
            the annotation that is needed to train a yolox model
        """

        annotation = self.base_annotations[index]

        # Transform image required for yolox, see
        # yolox/data/datasets/voc.py
        yolox_data_array, image_info = MLCVZooDataset.__annotation_to_yolox_tuple(
            annotation=annotation
        )
        height, width, _ = image_info

        # Extract information that is needed to apply bounding-box scaling later on
        ratio = min(self.img_size[0] / height, self.img_size[1] / width)
        resized_info = (int(height * ratio), int(width * ratio))

        # Apply the scaling to the bounding-boxes in yolox format
        yolox_data_array[:, :4] *= ratio

        return yolox_data_array, image_info, resized_info

    def load_image(self, index: int) -> np.ndarray:  # type: ignore[type-arg]
        """
        Overwrite load_image method.

        Args:
            index: The index to address the annotation from the global list of annotations

        Returns:

        """

        image_path = self.base_annotations[index].image_path

        img: np.ndarray = cv2.imread(image_path, cv2.IMREAD_COLOR)  # type: ignore[type-arg]
        assert img is not None

        return img

    @staticmethod
    def __annotation_to_yolox_tuple(
        annotation: BaseAnnotation,
    ) -> Tuple[np.ndarray, Tuple[int, int, str]]:  # type: ignore[type-arg]
        """
        Arguments:
            annotation: the target annotation to be made usable for yolox
                will be an BaseAnnotation
        Returns:
            a list containing lists of bounding boxes  [bbox coords, class name]
        """

        yolox_data_array = np.empty((0, 5))

        for bounding_box in annotation.get_bounding_boxes(include_segmentations=True):

            bndbox = [
                bounding_box.box.xmin,
                bounding_box.box.ymin,
                bounding_box.box.xmax,
                bounding_box.box.ymax,
                bounding_box.class_id,
            ]

            yolox_data_array = np.vstack((yolox_data_array, bndbox))

        width = int(annotation.get_width())
        height = int(annotation.get_height())
        image_info = (height, width, annotation.image_path)

        return yolox_data_array, image_info
