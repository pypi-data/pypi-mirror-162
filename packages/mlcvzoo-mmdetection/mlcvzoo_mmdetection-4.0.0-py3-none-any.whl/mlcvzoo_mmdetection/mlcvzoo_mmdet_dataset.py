# Copyright 2022 Open Logistics Foundation
#
# Licensed under the Open Logistics License 1.0.
# For details on the licensing terms, see the LICENSE file.

"""
Module for providing the possibility to train a mmocr
model on data that is provided by the annotation handler
of the MLCVZoo. This is realized by extending the 'DATASETS'
registry of mmocr (mmdetection).
"""

import logging
from typing import Any, Dict, List, Optional

import numpy as np
from mlcvzoo_base.api.data.annotation import BaseAnnotation
from mlcvzoo_base.configuration.annotation_handler_config import AnnotationHandlerConfig
from mlcvzoo_base.data_preparation.annotation_handler import AnnotationHandler
from mlcvzoo_base.evaluation.object_detection.utils import generate_img_id_map
from mmdet.datasets.builder import DATASETS
from mmdet.datasets.custom import CustomDataset
from related import to_model

logger = logging.getLogger(__name__)


@DATASETS.register_module()
class MLCVZooMMDetDataset(CustomDataset):
    """
    Implementation of a custom dataset. It follows the instructions given by:
    https://mmdetection.readthedocs.io/en/latest/tutorials/customize_dataset.html

    We followed an example and created our own dataset class
    which has to be compatible to the class "CustomDataset"
    of the mmdetection framework

    Custom dataset for segmentations.

    Annotation format required from mmdet.datasets.custom.CustomDataset:
    [
        {
            'filename': 'a.jpg',
            'width': 1280,
            'height': 720,
            'ann': {
                'bboxes': <np.ndarray> (n, 4),
                'labels': <np.ndarray> (n, ),
                'bboxes_ignore': <np.ndarray> (k, 4), (optional field) => NOTE: not yet implemented
                'labels_ignore': <np.ndarray> (k, 4) (optional field)  => NOTE: not yet implemented
            }
        },
        ...
    ]

    The `ann` field is optional for testing.
    """

    def __init__(  # pylint: disable=R0913, disable=R0914
        self,  # pylint: disable=W0613
        ann_file: Optional[
            str
        ],  # => ensure compatibility to superclass 'CustomDataset'
        pipeline: Optional[Any],
        classes: Optional[
            Any
        ] = None,  # => ensure compatibility to superclass 'CustomDataset'
        data_root: Optional[
            Any
        ] = None,  # => ensure compatibility to superclass 'CustomDataset'
        img_prefix: Optional[
            str
        ] = "",  # => ensure compatibility to superclass 'CustomDataset'
        seg_prefix: Optional[
            Any
        ] = None,  # => ensure compatibility to superclass 'CustomDataset'
        proposal_file: Optional[
            Any
        ] = None,  # => ensure compatibility to superclass 'CustomDataset'
        test_mode: bool = False,  # => ensure compatibility to superclass 'CustomDataset'
        filter_empty_gt: bool = True,  # => ensure compatibility to superclass 'CustomDataset'
        annotation_handler_config_path: str = "",  # Not consumed by the dataset
        annotation_handler_config_dict: Optional[Dict[Any, Any]] = None,
        ann_file_list: Optional[List[str]] = None,
        **kwargs: Any,  # pylint: disable=W0613
    ) -> None:
        # NOTE: The unused parameter above are necessary in order for mmdet to use this Dataset

        self.annotations: List[BaseAnnotation] = []

        self.ann_file_list = ann_file_list

        self.annotation_handler = AnnotationHandler(
            configuration=to_model(
                AnnotationHandlerConfig, annotation_handler_config_dict
            ),
        )

        CustomDataset.__init__(
            self,
            ann_file=ann_file,
            pipeline=pipeline,
            classes=None,
            data_root=None,
            img_prefix="",
            seg_prefix=None,
            proposal_file=None,
            test_mode=False,
            filter_empty_gt=True,
        )

        self.flag = np.ones(len(self), dtype=np.uint8)

        self.CLASSES = self.annotation_handler.mapper.get_model_class_names()

        logger.info("Finished SegmentationDataset init ...")

        self.img_directory_id_dict: Dict[str, int] = {}

    def __len__(self):  # type: ignore
        return len(self.data_infos)

    def load_annotations(self, ann_file) -> List:  # type: ignore
        """
        Overwrite from 'CustomDataset'.

        Parse all annotation data from the configured csv-files and save it to a Dict
        which is in the 'CustomDataset' format

        Args:
            ann_file: currently not used. Annotation is loaded through the AnnotationHandler
                Therefore, annotation location can be specified in AnnotationHandlerConfig

        Returns:
            A List of Image information (size, location) in CustomDataset format
        """

        img_infos = []
        if self.ann_file_list:
            for csv_file_path in self.ann_file_list:
                self.annotations.extend(
                    self.annotation_handler.parse_annotations_from_csv(
                        csv_file_path=csv_file_path
                    )
                )
        else:
            self.annotations = self.annotation_handler.parse_training_annotations()

        for i, annotation in enumerate(self.annotations):
            # Dict structure is based on 'CustomDataset'
            info = dict(
                height=annotation.get_height(),
                width=annotation.get_width(),
                filename=annotation.image_path,
            )

            img_infos.append(info)

        return img_infos

    def get_ann_info(self, idx: int) -> Dict[str, Any]:
        """
        Overwrite from 'CustomDataset' to get the annotations for mmdetection in the correct format

        Args:
            idx: Index of the item to load

        Returns:
            The annotation information at index=idx
        """

        gt_labels: List[int] = []
        gt_bboxes: List[List[float]] = []
        gt_masks_ann: List[Optional[List[List[float]]]] = []

        # No ground truth objects are ignored
        gt_bboxes_ignore: np.ndarray = np.zeros((0, 4), dtype=np.float32)  # type: ignore[type-arg]

        annotation = self.annotations[idx]

        for bounding_box in annotation.bounding_boxes:
            gt_labels.append(bounding_box.class_id)
            gt_bboxes.append(bounding_box.box.to_list(dst_type=float))
            gt_masks_ann.append(None)

        for segmentation in annotation.segmentations:
            gt_labels.append(segmentation.class_id)
            if segmentation.box is not None:
                gt_bboxes.append(segmentation.box.to_list(dst_type=float))
            else:
                gt_bboxes.append([0.0, 0.0, 0.0, 0.0])
            gt_masks_ann.append(segmentation.to_list(dst_type=float))

        if len(gt_bboxes) > 0:
            gt_labels_np = np.array(gt_labels, dtype=np.int64)
            gt_bboxes_np = np.array(gt_bboxes, dtype=np.float32)
        else:
            annotation_index, self.img_directory_id_dict = generate_img_id_map(
                image_path=annotation.image_path,
                img_directory_id_dict=self.img_directory_id_dict,
            )
            gt_labels_np = np.array([], dtype=np.int64)
            gt_bboxes_np = np.zeros((0, 4), dtype=np.float32)

        seg_map = annotation.image_path

        ann: Dict[str, Any] = dict(
            labels=gt_labels_np,
            bboxes=gt_bboxes_np,
            bboxes_ignore=gt_bboxes_ignore,
            masks=gt_masks_ann,
            masks_ignore=[],
            seg_map=seg_map,
        )

        return ann
