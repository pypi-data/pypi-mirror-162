# Copyright 2021 Open Logistics Foundation
#
# Licensed under the Open Logistics License 1.0.
# For details on the licensing terms, see the LICENSE file.

"""
Module for defining utility methods that are needed to process
the input and output of a yolox model.
"""

import logging
import os
from typing import Any, Dict, List, Optional, Tuple, Union

import cv2
import numpy as np
import torch
from mlcvzoo_base.api.data.annotation_class_mapper import AnnotationClassMapper
from mlcvzoo_base.api.data.bounding_box import BoundingBox
from mlcvzoo_base.api.data.box import Box
from mlcvzoo_base.api.data.class_identifier import ClassIdentifier
from mlcvzoo_base.api.model import ObjectDetectionModel
from yolox.utils import postprocess

from mlcvzoo_yolox.configuration import YOLOXInferenceConfig
from mlcvzoo_yolox.third_party.yolox.models.yolo_head import decode_outputs

logger = logging.getLogger(__name__)


def transform_np_to_torch_image(
    np_image: np.ndarray, inference_config: YOLOXInferenceConfig  # type: ignore[type-arg]
) -> torch.Tensor:
    """
    Transforms a given image as numpy array into a yolox conform torch Tensor.

    Args:
        np_image: The image that should be transformed
        inference_config: An YOLOXInferenceConfig object stating how the transformation
                          has to be performed

    Returns:
        The transformed image as torch Tensor
    """

    image_tensor = torch.from_numpy(np_image).unsqueeze(0)
    image_tensor = image_tensor.float()

    # move the image tensor to the correct hardware location
    if inference_config.device == "gpu":
        image_tensor = image_tensor.cuda()
        if inference_config.gpu_fp16:
            image_tensor = image_tensor.half()  # to FP16

    return image_tensor


def decode_yolox_output(
    yolox_model_output: torch.Tensor,
    ratio: float,
    score_threshold: float,
    mapper: AnnotationClassMapper,
) -> List[BoundingBox]:
    """
    Decode the output tensor that has been predicted by a yolox model and
    create a list of mlcvzoo compatible bounding boxes.

    Args:
        yolox_model_output: the output tensor
        ratio: the ratio between the input image and input dimension of the model, used
               for scaling the output
        score_threshold: Skip any predicted bounding box that has a score value beneath the
                         score_threshold.
        mapper: TODO

    Returns:
        The decoded list of bounding-boxes
    """

    bounding_boxes: List[BoundingBox] = []

    yolox_model_output = yolox_model_output.cpu()

    # NOTE: It is possible that the output of a yolox model has only one dimension.
    #       If this is the case the tensor has to be 'unsqueezed' to get a two-dimensional tensor,
    #       so that the indices below work.
    if len(yolox_model_output.shape) == 1:
        yolox_model_output = torch.unsqueeze(yolox_model_output, dim=0)

    bboxes = yolox_model_output[:, 0:4] / ratio

    class_ids = yolox_model_output[:, 6]
    bbox_scores = yolox_model_output[:, 4] * yolox_model_output[:, 5]

    for i in range(len(bboxes)):
        box = bboxes[i]

        score = bbox_scores[i]
        if score < score_threshold:
            continue

        class_id = int(class_ids[i])

        bounding_boxes.extend(
            ObjectDetectionModel.build_bounding_boxes(
                box_list=(
                    int(box[0]),
                    int(box[1]),
                    int(box[2]),
                    int(box[3]),
                ),
                class_identifiers=mapper.map_model_class_id_to_output_class_identifier(
                    class_id=class_id
                ),
                model_class_identifier=ClassIdentifier(
                    class_id=class_id,
                    class_name=mapper.map_annotation_class_id_to_model_class_name(
                        class_id=class_id
                    ),
                ),
                score=float(score),
                difficult=False,
                occluded=False,
                content="",
            )
        )

    return bounding_boxes


def predict_with_model(
    model: torch.nn.Module,
    data_item: Union[str, np.ndarray, torch.Tensor],  # type: ignore[type-arg]
    preprocess: Optional[Any],
    inference_config: YOLOXInferenceConfig,
    mapper: AnnotationClassMapper,
    decode_output: bool = False,
    strides: Optional[List[int]] = None,
    image_shape: Optional[Tuple[int, int]] = None,  # height, width
) -> Tuple[Union[str, np.ndarray, torch.Tensor], List[BoundingBox]]:  # type: ignore[type-arg]
    """
    Run a yolox model on a given input image and predict a list of mlcvzoo conform bounding boxes.
    The image can be provided in a couple of formats. When using a torch.Tensor as input data, the
    'image_shape' parameter has to be provided in order to be able to determine a scaling ratio
    for the predicted bounding boxes.

    Args:
        model: The yolox model that should be used for prediction
        data_item: Either the path to an image or a already created numpy image
        preprocess: Preprocessing method for the given image
        inference_config: An YOLOXInferenceConfig object stating relevant prediction settings
        mapper: TODO
        decode_output: If a dedicated decode method should be used. This is needed for tensorrt
                       models, since they don't have a yolox head anymore.
        strides: (Optional) List defining the strides used to build the YOLOXHead. Only needed if
                 the decode_output is True
        image_shape: (Optional) Needed when the input data is a torch Tensor. Shape of the original
                      input image. It will be used to determine a scaling ratio for the predicted
                      bounding boxes, so that they fit to the shape of the original input image.

    Returns:
        The predicted bounding boxes
    """
    image_tensor: torch.Tensor

    # TODO: ensure tensor is 4D
    if isinstance(data_item, torch.Tensor):
        image_tensor = data_item

        if image_shape is not None:
            ratio = min(
                inference_config.input_dim[0] / image_shape[0],
                inference_config.input_dim[1] / image_shape[1],
            )
        else:
            raise ValueError(
                "When using a torch.Tensor as input data for 'predict_with_model',"
                "'image_shape' parameter has to be provided!"
            )
    else:
        if isinstance(data_item, str):
            if os.path.isfile(data_item):
                image = cv2.imread(data_item)
                if image is None:
                    raise ValueError("Could not read image from '%s'" % data_item)
            else:
                raise ValueError(f"File {data_item} does not exist!")
        else:
            image = data_item

        ratio = min(
            inference_config.input_dim[0] / image.shape[0],
            inference_config.input_dim[1] / image.shape[1],
        )

        # preprocess the image as needed for yolox
        if preprocess is None:
            raise ValueError(
                "No preprocess method available for the yolox model! "
                "Maybe you have initialized it as a training model?"
                "Normally this is set to be an instance of "
                "yolox.data.data_augment.ValTransform"
            )

        preprocessed_np_image, _ = preprocess(image, None, inference_config.input_dim)

        image_tensor = transform_np_to_torch_image(
            np_image=preprocessed_np_image, inference_config=inference_config
        )

    # run prediction and postprocess the output
    # NOTE: mypy error 'Call to untyped function "close" in typed context'
    #       can be ignored
    with torch.no_grad():  # type: ignore
        yolox_model_outputs = model(image_tensor)

        if decode_output:

            if strides is None:
                raise ValueError(
                    "In order to be able to decode the output, the "
                    "'strides' parameters has to be provided!"
                )

            output_dim = []
            for index, stride in enumerate(strides):
                output_dim.append(
                    [
                        int(inference_config.input_dim[0] / stride),
                        int(inference_config.input_dim[0] / stride),
                    ]
                )

            decode_outputs(
                output_dim=output_dim,
                strides_list=strides,
                outputs=yolox_model_outputs,
                dtype=yolox_model_outputs.type(),
            )

        yolox_model_outputs = postprocess(
            prediction=yolox_model_outputs,
            num_classes=mapper.num_classes,
            conf_thre=inference_config.score_threshold,
            nms_thre=inference_config.nms_threshold,
            class_agnostic=True,
        )

    # decode the final result
    if yolox_model_outputs[0] is not None:
        bounding_boxes: List[BoundingBox] = decode_yolox_output(
            yolox_model_output=yolox_model_outputs[0],
            ratio=ratio,
            score_threshold=inference_config.score_threshold,
            mapper=mapper,
        )
    else:
        bounding_boxes = []

    return data_item, bounding_boxes
