# Copyright 2021 Open Logistics Foundation
#
# Licensed under the Open Logistics License 1.0.
# For details on the licensing terms, see the LICENSE file.

"""
Module for defining the model classes that are used to wrap the mmocr framework.
"""

import logging
import typing
from abc import ABC
from time import time
from typing import Any, Callable, Dict, Generic, List, Optional, Tuple, Union, cast

from mlcvzoo_base.api.model import PredictionType
from mlcvzoo_base.configuration.utils import (
    create_configuration as create_basis_configuration,
)
from mlcvzoo_mmdetection.model import MMDetectionModel
from mmcv import Config
from mmcv.utils import Registry
from mmocr.apis.inference import model_inference
from mmocr.models.builder import DETECTORS as mmocr_models
from nptyping import Int, NDArray, Shape

from mlcvzoo_mmocr.configuration import MMOCRConfig
from mlcvzoo_mmocr.mlcvzoo_mmocr_dataset import MLCVZooMMOCRDataset
from mlcvzoo_mmocr.third_party.mmocr import build_val_dataset

logger = logging.getLogger(__name__)

#################################
# TODO: This is only a workaround and should be fixed by mmdetection or mmocr
mmocr_models.module_dict.update(mmocr_models.parent.module_dict)
#################################

ImageType = NDArray[Shape["Height, Width, Any"], Int]


class MMOCRModel(MMDetectionModel, ABC, Generic[PredictionType]):
    def __init__(
        self,
        from_yaml: str,
        configuration: Optional[MMOCRConfig] = None,
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
        self.configuration: MMOCRConfig = cast(  # type: ignore[redundant-cast]
            MMOCRConfig, self.configuration
        )

    @staticmethod
    def create_configuration(
        from_yaml: Optional[str] = None,
        configuration: Optional[MMOCRConfig] = None,
        string_replacement_map: Optional[Dict[str, str]] = None,
    ) -> MMOCRConfig:
        return typing.cast(
            MMOCRConfig,
            create_basis_configuration(
                configuration_class=MMOCRConfig,
                from_yaml=from_yaml,
                input_configuration=configuration,
                string_replacement_map=string_replacement_map,
            ),
        )

    def _train_pre_init(self, cfg: Config) -> Config:
        if self.configuration.train_config.argparse_config.load_from:
            cfg.load_from = self.configuration.train_config.argparse_config.load_from

        return cfg

    @staticmethod
    def _get_dataset_type() -> str:
        return "MLCVZooMMOCRDataset"

    @staticmethod
    def _get_framework_version() -> Any:
        from mmocr import __version__ as framework_version

        return framework_version

    def _build_val_dataset(self, cfg: Config) -> Any:
        return build_val_dataset(cfg=cfg)

    @staticmethod
    def _register_dataset() -> None:
        """
        Register the custom dataset of the MLCVZoo in the registry of mmcv

        Returns:
            None
        """

        MMDetectionModel._register_dataset()

        mmdet_registry = Registry("dataset")
        mmdet_registry.register_module(MLCVZooMMOCRDataset.__name__)

    def _predict(
        self,
        data_item: Union[Union[str, ImageType], List[Union[str, ImageType]]],
    ) -> Any:
        start = time()
        results = model_inference(model=self.net, imgs=data_item)
        end = time() - start

        logger.debug(
            "Model prediction time: %.4f | result: %s",
            end,
            results,
        )

        return results

    @staticmethod
    def _get_framework_imports() -> Tuple[
        Callable[[Any], Any],
        Callable[[Any], Any],
        Callable[[Any], Any],
        Callable[[Any], Any],
        Callable[[Any], Any],
        Callable[[Any], Any],
    ]:
        from mmocr.apis import init_detector, init_random_seed, train_detector
        from mmocr.datasets import build_dataset
        from mmocr.models import build_detector
        from mmocr.utils import collect_env

        return (
            init_detector,
            init_random_seed,
            train_detector,
            build_dataset,
            build_detector,
            collect_env,
        )
