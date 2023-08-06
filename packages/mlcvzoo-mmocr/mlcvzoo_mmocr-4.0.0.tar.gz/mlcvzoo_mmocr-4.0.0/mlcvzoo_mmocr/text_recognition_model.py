# Copyright 2021 Open Logistics Foundation
#
# Licensed under the Open Logistics License 1.0.
# For details on the licensing terms, see the LICENSE file.

"""
Module for defining the model classes that are used to wrap the mmocr framework.
"""

import logging
from statistics import mean
from typing import Any, Dict, List, Optional, Tuple, Union

from mlcvzoo_base.api.data.ocr_perception import OCRPerception
from mlcvzoo_base.api.model import OCRModel
from nptyping import Int, NDArray, Shape

from mlcvzoo_mmocr.configuration import MMOCRConfig
from mlcvzoo_mmocr.model import MMOCRModel

logger = logging.getLogger(__name__)

ImageType = NDArray[Shape["Height, Width, Any"], Int]


class MMOCRTextRecognitionModel(
    MMOCRModel[OCRPerception],
    OCRModel[MMOCRConfig, Union[str, ImageType]],
):
    def __init__(
        self,
        from_yaml: str,
        configuration: Optional[MMOCRConfig] = None,
        string_replacement_map: Optional[Dict[str, str]] = None,
        init_for_inference: bool = False,
        is_multi_gpu_instance: bool = False,
    ) -> None:
        MMOCRModel.__init__(
            self,
            from_yaml=from_yaml,
            configuration=configuration,
            string_replacement_map=string_replacement_map,
            init_for_inference=init_for_inference,
            is_multi_gpu_instance=is_multi_gpu_instance,
        )
        OCRModel.__init__(
            self,
            unique_name=self.configuration.base_config.MODEL_SPECIFIER,
            configuration=self.configuration,
            init_for_inference=init_for_inference,
        )

    def __process_result(self, result: Dict[str, Any]) -> Optional[OCRPerception]:

        if isinstance(result["score"], list):
            score = mean(result["score"])
        else:
            score = result["score"]

        if score >= self.configuration.inference_config.score_threshold:
            return OCRPerception(content=result["text"], score=score)

        return None

    def predict(
        self, data_item: Union[str, ImageType]
    ) -> Tuple[Union[str, ImageType], List[OCRPerception]]:

        assert self.net is not None

        ocr_texts: List[OCRPerception] = []

        ocr_perception = self.__process_result(
            result=self._predict(data_item=data_item)
        )

        if ocr_perception is not None:
            ocr_texts.append(ocr_perception)

        return data_item, ocr_texts

    def predict_many(
        self, data_items: List[Union[str, ImageType]]
    ) -> List[Tuple[Union[str, ImageType], List[OCRPerception]]]:

        assert self.net is not None

        prediction_list: List[Tuple[Union[str, ImageType], List[OCRPerception]]] = []

        results = self._predict(data_item=data_items)

        for data_item, result in zip(data_items, results):

            ocr_perception = self.__process_result(result=result)

            if ocr_perception is not None:

                prediction_list.append(
                    (
                        data_item,
                        [ocr_perception],
                    )
                )
            else:
                prediction_list.append(
                    (
                        data_item,
                        [],
                    )
                )

        return prediction_list
