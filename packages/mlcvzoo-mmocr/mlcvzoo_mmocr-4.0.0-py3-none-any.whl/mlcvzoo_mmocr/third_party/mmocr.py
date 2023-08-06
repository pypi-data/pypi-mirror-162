# Copyright (c) OpenMMLab. All rights reserved.
# Copyright 2022 Open Logistics Foundation

"""
This module is used to source out methods that are used in the context of the training
of an mmdetection model. Inspired by
https://github.com/open-mmlab/mmdetection/blob/master/tools/train.py
"""

import copy
import logging
from typing import Any

from mmcv import Config
from mmocr.utils import is_2dlist

logger = logging.getLogger(__name__)


def build_val_dataset(cfg: Config) -> Any:
    val_dataset = copy.deepcopy(cfg.data.val)
    if cfg.data.train.get("pipeline", None) is None:
        if is_2dlist(cfg.data.train.datasets):
            train_pipeline = cfg.data.train.datasets[0][0].pipeline
        else:
            train_pipeline = cfg.data.train.datasets[0].pipeline
    elif is_2dlist(cfg.data.train.pipeline):
        train_pipeline = cfg.data.train.pipeline[0]
    else:
        train_pipeline = cfg.data.train.pipeline

    if val_dataset["type"] in ["ConcatDataset", "UniformConcatDataset"]:
        for dataset in val_dataset["datasets"]:
            dataset.pipeline = train_pipeline
    else:
        val_dataset.pipeline = train_pipeline

    return val_dataset
