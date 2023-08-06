# Copyright 2021 Open Logistics Foundation
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
from typing import Any, Dict, Optional

from mlcvzoo_mmdetection.mlcvzoo_mmdet_dataset import MLCVZooMMDetDataset
from mmdet.datasets.builder import DATASETS

logger = logging.getLogger(__name__)


@DATASETS.register_module()
class MLCVZooMMOCRDataset(MLCVZooMMDetDataset):
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
        annotation_handler_config_dict: Optional[Dict[Any, Any]] = None,
        datasets: Optional[Any] = None,  # pylint: disable=W0613
        separate_eval: bool = True,  # pylint: disable=W0613
        show_mean_scores: str = "auto",  # pylint: disable=W0613
        force_apply: bool = False,  # pylint: disable=W0613
        **kwargs: Any,  # pylint: disable=W0613
    ) -> None:
        MLCVZooMMDetDataset.__init__(
            self,
            ann_file=ann_file,
            pipeline=pipeline,
            annotation_handler_config_dict=annotation_handler_config_dict,
        )
