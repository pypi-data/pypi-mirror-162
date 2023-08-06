# Copyright 2022 Open Logistics Foundation
#
# Licensed under the Open Logistics License 1.0.
# For details on the licensing terms, see the LICENSE file.

"""
Model that wraps all objection detection models of mmdetection
"""

import logging
import typing
from typing import Dict, List, Optional, Tuple, Union

import numpy as np
import torch.nn
from mlcvzoo_base.api.data.annotation_class_mapper import AnnotationClassMapper
from mlcvzoo_base.api.data.bounding_box import BoundingBox
from mlcvzoo_base.api.data.class_identifier import ClassIdentifier
from mlcvzoo_base.api.interfaces import NetBased, Trainable
from mlcvzoo_base.api.model import ObjectDetectionModel
from mlcvzoo_base.configuration.structs import ObjectDetectionBBoxFormats
from mlcvzoo_base.configuration.utils import (
    create_configuration as create_basis_configuration,
)
from mmdet.apis import inference_detector

from mlcvzoo_mmdetection.configuration import MMDetectionConfig
from mlcvzoo_mmdetection.model import MMDetectionModel

logger = logging.getLogger(__name__)


class MMObjectDetectionModel(
    MMDetectionModel,
    ObjectDetectionModel[MMDetectionConfig, Union[str, np.ndarray]],  # type: ignore[type-arg]
    NetBased[torch.nn.Module],
    Trainable,
):
    """
    Class for wrapping mmdetection models
    """

    def __init__(
        self,
        from_yaml: Optional[str] = None,
        configuration: Optional[MMDetectionConfig] = None,
        string_replacement_map: Optional[Dict[str, str]] = None,
        init_for_inference: bool = False,
        is_multi_gpu_instance: bool = False,
    ) -> None:

        MMDetectionModel.__init__(
            self,
            from_yaml=from_yaml,
            configuration=configuration,
            string_replacement_map=string_replacement_map,
            init_for_inference=init_for_inference,
            is_multi_gpu_instance=is_multi_gpu_instance,
        )
        ObjectDetectionModel.__init__(
            self,
            unique_name=self.configuration.base_config.MODEL_SPECIFIER,
            configuration=self.configuration,
            mapper=AnnotationClassMapper(
                class_mapping=self.configuration.class_mapping,
                reduction_mapping=self.configuration.inference_config.reduction_class_mapping,
            ),
            init_for_inference=init_for_inference,
        )
        NetBased.__init__(self, net=self.net)
        Trainable.__init__(self)

    @staticmethod
    def create_configuration(
        from_yaml: Optional[str] = None,
        configuration: Optional[MMDetectionConfig] = None,
        string_replacement_map: Optional[Dict[str, str]] = None,
    ) -> MMDetectionConfig:
        return typing.cast(
            MMDetectionConfig,
            create_basis_configuration(
                configuration_class=MMDetectionConfig,
                from_yaml=from_yaml,
                input_configuration=configuration,
                string_replacement_map=string_replacement_map,
            ),
        )

    @property
    def num_classes(self) -> int:
        return self.mapper.num_classes

    def get_classes_id_dict(self) -> Dict[int, str]:
        return self.mapper.annotation_class_id_to_model_class_name_map

    def __decode_mmdet_result(
        self, model_result: List[np.ndarray]  # type: ignore[type-arg]
    ) -> List[BoundingBox]:
        """
        Decode output of an object detection model from mmdetection

        Args:
            model_result: The result that the model has predicted

        Returns:
            The model_result as list of bounding boxes in MLCVZoo format
        """

        bounding_boxes: List[BoundingBox] = list()

        np_bounding_boxes = np.vstack(model_result)
        assert np_bounding_boxes.shape[1] == 5

        # Create numpy array containing all class ids
        class_id_list = []
        for index, box in enumerate(model_result):
            class_id_list.append(np.full(box.shape[0], index, dtype=np.int32))
        np_class_id_array = np.concatenate(class_id_list)

        # Get relevant indices that do match a given threshold
        np_scores = np_bounding_boxes[:, -1]
        valid_indices = np_scores > self.configuration.inference_config.score_threshold

        # Filter results according to the determined valid indices
        np_bounding_boxes = np_bounding_boxes[valid_indices, :]
        np_class_id_array = np_class_id_array[valid_indices]
        np_scores = np_scores[valid_indices]

        for bbox, class_id, score in zip(
            np_bounding_boxes, np_class_id_array, np_scores
        ):
            bbox_int = bbox.astype(np.int32)

            bounding_boxes.extend(
                self.build_bounding_boxes(
                    box_format=ObjectDetectionBBoxFormats.XYXY,
                    box_list=(bbox_int[0:4]),
                    class_identifiers=self.mapper.map_model_class_id_to_output_class_identifier(
                        class_id=class_id
                    ),
                    model_class_identifier=ClassIdentifier(
                        class_id=class_id,
                        class_name=self.mapper.map_annotation_class_id_to_model_class_name(
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

    def predict(
        self, data_item: Union[str, np.ndarray]  # type: ignore[type-arg]
    ) -> Tuple[Union[str, np.ndarray], List[BoundingBox]]:  # type: ignore[type-arg]
        """
        Predicts objects for given data_item

        Args:
            data_item: Object on which a prediction is to be executed

        Returns:
            Data_item which served as input
            List of BoundingBox objects containing bounding box information for every prediction
            made by the model. Only contains bounding boxes which are above the score threshold
            specified in configuration file.
        """

        if self.net is None:
            raise ValueError(
                "MMDetectionModel is not initialized for inference! "
                "Please set the parameter 'init_for_inference=True'"
            )

        result = inference_detector(model=self.net, imgs=data_item)

        # Check if model output is only bbox head, or if the model has other heads:
        # tuple => bbox-head + mask-head
        if isinstance(result, tuple):
            model_result = result[0]

        # type is list => bbox-head only
        else:
            model_result = result

        bounding_boxes = self.__decode_mmdet_result(model_result=model_result)

        return data_item, bounding_boxes
