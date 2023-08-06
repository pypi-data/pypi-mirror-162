# Copyright 2021 Open Logistics Foundation
#
# Licensed under the Open Logistics License 1.0.
# For details on the licensing terms, see the LICENSE file.

"""
Module for defining the model classes that are used to wrap the mmocr framework.
"""

import logging
from typing import Any, Dict, List, Optional, Tuple, Union

from mlcvzoo_base.api.data.annotation_class_mapper import AnnotationClassMapper
from mlcvzoo_base.api.data.class_identifier import ClassIdentifier
from mlcvzoo_base.api.data.segmentation import PolygonType, Segmentation
from mlcvzoo_base.api.model import SegmentationModel
from nptyping import Int, NDArray, Shape

from mlcvzoo_mmocr.configuration import MMOCRConfig
from mlcvzoo_mmocr.model import MMOCRModel

logger = logging.getLogger(__name__)

ImageType = NDArray[Shape["Height, Width, Any"], Int]


class MMOCRTextDetectionModel(
    MMOCRModel[Segmentation],
    SegmentationModel[MMOCRConfig, Union[str, ImageType]],
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
        SegmentationModel.__init__(
            self,
            unique_name=self.configuration.base_config.MODEL_SPECIFIER,
            configuration=self.configuration,
            init_for_inference=init_for_inference,
            mapper=AnnotationClassMapper(
                class_mapping=self.configuration.class_mapping,
            ),
        )

    @property
    def num_classes(self) -> int:
        return self.mapper.num_classes

    def get_classes_id_dict(self) -> Dict[int, str]:
        return self.mapper.annotation_class_id_to_model_class_name_map

    @staticmethod
    def __decode_mmocr_result_to_list_of_points(
        text_detection_result: List[float],
    ) -> PolygonType:
        """
        Converts MMOCR result to list of tuples. MMOCR stores the result as
        [x,y,x,y,x,y,x,y, ..., score]. This function takes all but the last
        element (the score) of the MMOCR result and reshapes them.
        The returned format is [(x, y), (x, y), ...].
        """

        # we skip last entry because this is a confidence value
        return list(zip(text_detection_result[:-1:2], text_detection_result[1:-1:2]))

    def __process_text_detection_result(
        self, result: Dict[str, Any]
    ) -> List[Segmentation]:

        segmentations: List[Segmentation] = list()

        for text_detection_result in result["boundary_result"]:
            score: float = text_detection_result[-1]

            polygon: PolygonType = (
                MMOCRTextDetectionModel.__decode_mmocr_result_to_list_of_points(
                    text_detection_result=text_detection_result
                )
            )

            if score >= self.configuration.inference_config.score_threshold:
                segmentations.extend(
                    self.build_segmentations(
                        class_identifiers=[
                            ClassIdentifier(
                                class_id=MMOCRConfig.text_class_id,
                                class_name=MMOCRConfig.text_class_name,
                            )
                        ],
                        score=score,
                        polygon=polygon,
                    )
                )

                if self.configuration.inference_config.to_rect_polygon:
                    for segmentation in segmentations:
                        segmentation.to_rect_polygon()

        return segmentations

    def predict(
        self, data_item: Union[str, ImageType]
    ) -> Tuple[Union[str, ImageType], List[Segmentation]]:

        assert self.net is not None

        return data_item, self.__process_text_detection_result(
            result=self._predict(data_item=data_item)
        )

    def predict_many(
        self, data_items: List[Union[str, ImageType]]
    ) -> List[Tuple[Union[str, ImageType], List[Segmentation]]]:

        assert self.net is not None

        prediction_list: List[Tuple[Union[str, ImageType], List[Segmentation]]] = []

        results = self._predict(data_item=data_items)

        for data_item, result in zip(data_items, results):

            segmentations = self.__process_text_detection_result(result=result)

            prediction_list.append(
                (
                    data_item,
                    segmentations,
                )
            )

        return prediction_list
