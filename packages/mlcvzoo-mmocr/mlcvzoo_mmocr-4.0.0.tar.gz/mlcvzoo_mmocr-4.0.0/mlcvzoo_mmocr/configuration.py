# Copyright 2021 Open Logistics Foundation
#
# Licensed under the Open Logistics License 1.0.
# For details on the licensing terms, see the LICENSE file.

"""
Definition of the MMOCRConfig that is used to configure the MMOCRModel (and subclasses).
"""

import logging
from typing import Dict, List, Optional

import related
from mlcvzoo_base.configuration.class_mapping_config import (
    ClassMappingConfig,
    ClassMappingModelClassesConfig,
)
from mlcvzoo_base.configuration.detector_configs import DetectorConfig
from mlcvzoo_mmdetection.configuration import (
    MMDetectionConfig,
    MMDetectionDistributedTrainConfig,
    MMDetectionInferenceConfig,
    MMDetectionTrainArgparseConfig,
    MMDetectionTrainConfig,
)

logger = logging.getLogger(__name__)


@related.mutable(strict=True)
class MMOCRTrainArgparseConfig(MMDetectionTrainArgparseConfig):
    # argparse parameter from mmdetection:

    # The checkpoint file to load from.
    load_from: Optional[str] = related.StringField(required=False, default=None)

    # Memory cache config for image loading speed-up during training.
    mc_config: Optional[str] = related.StringField(required=False, default=None)

    # NOTE: The following argparse arguments from mmdet.tools.train will not be used in this
    #       configuration.
    #
    # - local_rank: int = related.StringField(default=0) rank for distributed training

    def check_values(self) -> bool:
        if self.load_from is not None:
            logger.warning(
                "DEPRECATED: The load_from config attribute is no longer supported "
                "and will be removed in future versions"
            )

        if self.mc_config is not None:
            logger.warning(
                "DEPRECATED: The mc_config config attribute is no longer supported "
                "and will be removed in future versions"
            )

        return True


@related.mutable(strict=True)
class MMOCRTrainConfig(MMDetectionTrainConfig):
    """
    argparse parameter from mmdetection/tools/train.py
    """

    argparse_config: MMOCRTrainArgparseConfig = related.ChildField(
        cls=MMOCRTrainArgparseConfig
    )

    multi_gpu_config: Optional[MMDetectionDistributedTrainConfig] = related.ChildField(
        cls=MMDetectionDistributedTrainConfig, required=False, default=None
    )


@related.mutable(strict=True)
class MMOCRInferenceConfig(MMDetectionInferenceConfig):
    # Whether the output polygon should be formatted to represent a rect, or
    # the polygon should be kept as it is
    to_rect_polygon: bool = related.BooleanField(default=False, required=False)


@related.mutable(strict=True)
class MMOCRConfig(MMDetectionConfig):
    # NOTE: only the "gpus" OR the "gpu_ids" parameter is used by the mmdetection train routine
    #       therefore make them mutual exclusive in the configuration
    mutual_attribute_map: Dict[str, List[str]] = {}

    text_class_id: int = 0
    text_class_name: str = "text"

    inference_config: MMOCRInferenceConfig = related.ChildField(
        cls=MMOCRInferenceConfig
    )

    train_config: MMOCRTrainConfig = related.ChildField(cls=MMOCRTrainConfig)

    base_config: DetectorConfig = related.ChildField(
        cls=DetectorConfig, default=DetectorConfig()
    )

    class_mapping: ClassMappingConfig = related.ChildField(
        cls=ClassMappingConfig,
        default=ClassMappingConfig(  # type: ignore[call-arg]
            mapping=[],
            model_classes=[
                # OCR models only detect text,
                # therefore it has this default class mapping.
                ClassMappingModelClassesConfig(  # type: ignore[call-arg]
                    class_id=text_class_id,
                    class_name=text_class_name,
                )
            ],
            number_model_classes=1,
        ),
    )
