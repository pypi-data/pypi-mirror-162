# Copyright 2021 Open Logistics Foundation
#
# Licensed under the Open Logistics License 1.0.
# For details on the licensing terms, see the LICENSE file.

"""
Module for defining the DarknetDetectionModel. It is a ObjectDetectionModel
which can be trained on custom data.
"""

import importlib.util
import logging
import os
import shutil
import subprocess
import typing
from types import ModuleType
from typing import Any, Dict, List, Optional, Tuple, Union

import cv2
import numpy as np
from mlcvzoo_base.api.data.annotation import BaseAnnotation
from mlcvzoo_base.api.data.annotation_class_mapper import AnnotationClassMapper
from mlcvzoo_base.api.data.bounding_box import BoundingBox
from mlcvzoo_base.api.data.class_identifier import ClassIdentifier
from mlcvzoo_base.api.interfaces import Trainable
from mlcvzoo_base.api.model import ObjectDetectionModel
from mlcvzoo_base.configuration.replacement_config import ReplacementConfig
from mlcvzoo_base.configuration.structs import ObjectDetectionBBoxFormats
from mlcvzoo_base.configuration.utils import (
    create_configuration as create_basis_configuration,
)
from mlcvzoo_base.data_preparation.annotation_handler import AnnotationHandler

from mlcvzoo_darknet.configuration import DarknetConfig
from mlcvzoo_darknet.darknetdatafile import DarknetDataFile

logger = logging.getLogger(__name__)

DARKNET_MODULE_NAME = "dk"


class DarknetDetectionModel(
    ObjectDetectionModel[DarknetConfig, Union[np.ndarray, str]], Trainable  # type: ignore[type-arg]
):
    """
    Model which wraps the darknet framework https://github.com/AlexeyAB. The
    main functionality is based on their provided python wrapper as defined in:

    https://github.com/AlexeyAB/darknet/blob/359001d360df2fe8b77ce56c60bb3d48b6d1faea/darknet.py
    """

    def __init__(
        self,
        from_yaml: Optional[str] = None,
        configuration: Optional[DarknetConfig] = None,
        init_for_inference: bool = False,
        string_replacement_map: Optional[Dict[str, str]] = None,
    ):
        self.darknet_module: Optional[ModuleType] = None
        self.annotation_handler: Optional[AnnotationHandler] = None

        self.configuration: DarknetConfig = DarknetDetectionModel.create_configuration(
            from_yaml=from_yaml,
            configuration=configuration,
            string_replacement_map=string_replacement_map,
        )

        if (
            ReplacementConfig.DARKNET_DIR_KEY
            not in self.configuration.string_replacement_map
        ):
            raise ValueError(
                f"Please provide a valid value "
                f"for the key '{ReplacementConfig.DARKNET_DIR_KEY}' "
                f"in your replacement configuration file."
            )

        self.darknet_dir = self.configuration.string_replacement_map[
            ReplacementConfig.DARKNET_DIR_KEY
        ]

        ObjectDetectionModel.__init__(
            self,
            unique_name=self.configuration.base_config.MODEL_SPECIFIER,
            configuration=self.configuration,
            init_for_inference=init_for_inference,
            mapper=AnnotationClassMapper(
                class_mapping=self.configuration.class_mapping,
                reduction_mapping=self.configuration.inference_config.reduction_class_mapping,
            ),
        )
        Trainable.__init__(self)

    @staticmethod
    def create_configuration(
        from_yaml: Optional[str] = None,
        configuration: Optional[DarknetConfig] = None,
        string_replacement_map: Optional[Dict[str, str]] = None,
    ) -> DarknetConfig:
        return typing.cast(
            DarknetConfig,
            create_basis_configuration(
                configuration_class=DarknetConfig,
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

    def _init_inference_model(self) -> None:
        df = DarknetDataFile(**self.configuration.inference_config.data_file.__dict__)
        df.write_file(self.configuration.inference_config.data_path)

        darknet_script_path = os.path.join(self.darknet_dir, "darknet.py")

        # Load the darknet script as a python module
        darknet_spec = importlib.util.spec_from_file_location(
            DARKNET_MODULE_NAME, darknet_script_path
        )

        self.darknet_module = importlib.util.module_from_spec(darknet_spec)  # type: ignore
        darknet_spec.loader.exec_module(self.darknet_module)  # type: ignore

        (
            self.network,
            self.class_names,
            self.colors,
        ) = self.darknet_module.load_network(
            self.configuration.inference_config.config_path,
            self.configuration.inference_config.data_path,
            self.configuration.inference_config.checkpoint_path,
        )

    def _init_training_model(self) -> None:

        self.annotation_handler = AnnotationHandler(
            configuration=self.configuration.train_config.train_annotation_handler_config
        )

    def _numpy_to_darknet_image(self, img: np.ndarray) -> Tuple[np.ndarray, Any]:  # type: ignore[type-arg]
        """
        NOTE: the output image "dk_image" is of type "self.darknet_module.IMAGE".
        Since this module is loaded during runtime, a type hint is not available

        Args:
            img: the numpy image which should be transformed to a darknet image

        Returns:
            the transformed darknet image
        """

        if self.darknet_module is None:
            raise ValueError("The darknet_module=None attribute is not initialized!")

        transposed_img = img.transpose((2, 0, 1)).flat
        normalized_image = np.ascontiguousarray(transposed_img, dtype=np.float32)
        normalized_image /= 255.0
        raw_data = normalized_image.ctypes.data_as(
            self.darknet_module.POINTER(self.darknet_module.c_float)
        )
        dk_image = self.darknet_module.IMAGE(
            img.shape[1], img.shape[0], img.shape[2], raw_data
        )

        # NOTE: we need to return the normalized_image object as well, otherwise
        #       the pointer of the darknet image get confused
        return normalized_image, dk_image

    def _write_darknet_config(
        self,
        train_work_dir: str,
        train_txt_path: str,
        test_txt_path: str,
        model_specifier: str,
    ) -> Tuple[str, str]:

        cfg_in_path = self.configuration.train_config.config_path

        data_path = os.path.join(train_work_dir, f"{model_specifier}.data")
        cfg_out_path = os.path.join(train_work_dir, f"{model_specifier}.cfg")

        # TODO: differentiate between valid and eval paths
        df = DarknetDataFile(
            classes=self.mapper.num_classes,
            names=f"{model_specifier}.names",
            train=train_txt_path,
            valid=test_txt_path,
            eval=test_txt_path,
            backup=train_work_dir,
        )
        df.write_file(data_path)

        logger.info(
            "Copy darknet training cfg-path \n from '%s' to '%s'",
            cfg_in_path,
            cfg_out_path,
        )
        shutil.copy(cfg_in_path, cfg_out_path)

        return data_path, cfg_out_path

    def train(self) -> None:

        train_annotation_handler_config = (
            self.configuration.train_config.train_annotation_handler_config
        )

        if (
            train_annotation_handler_config is None
            or train_annotation_handler_config.write_output is None
            or train_annotation_handler_config.write_output.darknet_train_set is None
        ):
            raise ValueError(
                "train_config is None! In order to be able to train a darknet model a valid "
                "train_config.train_annotation_handler_config.write_output.darknet_train_set "
                "has to be provided!"
            )

        dk_exe = os.path.join(self.darknet_dir, "darknet")

        self.annotation_handler = AnnotationHandler(
            configuration=train_annotation_handler_config
        )

        annotations: List[
            BaseAnnotation
        ] = self.annotation_handler.parse_training_annotations()

        if len(annotations) == 0:
            raise ValueError(
                "Could not parse any annotations using the provided "
                "annotation-handler configuration at train_config.train_annotation_handler_config"
            )

        self.annotation_handler.generate_darknet_train_set(annotations=annotations)

        train_txt_path = (
            train_annotation_handler_config.write_output.darknet_train_set.get_train_file_path()
        )
        test_txt_path = (
            train_annotation_handler_config.write_output.darknet_train_set.get_test_file_path()
        )

        data_path, cfg_path = self._write_darknet_config(
            train_work_dir=self.configuration.train_config.work_dir,
            train_txt_path=train_txt_path,
            test_txt_path=test_txt_path,
            model_specifier=self.configuration.base_config.MODEL_SPECIFIER,
        )

        # Example call: ./darknet detector train darknet.data darknet.cfg -gpus 0,1,2,3
        cmd_list = [
            dk_exe,
            "detector",
            "train",
            data_path,
            cfg_path,
            "-dont_show -mjpeg_port 8090",
        ]
        cmd_string = " ".join(cmd_list)

        darknet_process: subprocess.Popen[bytes] = subprocess.Popen(
            args=cmd_string,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )

        while True:
            return_code = darknet_process.poll()

            if return_code is not None:
                logger.info("darknet return_code: %s", return_code)
                break

            if darknet_process.stdout is not None:
                line: Union[bytes, str] = darknet_process.stdout.readline()

                if not isinstance(line, str):
                    line = line.decode("utf-8")

                logger.info(line)

                if line == "" and darknet_process.poll() is not None:
                    break

    def predict(
        self, data_item: Union[np.ndarray, str]  # type: ignore[type-arg]
    ) -> Tuple[Union[np.ndarray, str], List[BoundingBox]]:  # type: ignore[type-arg]

        """
        Predicts objects in given data_item
        Args:
            data_item: N-dimensional array or string containing the image path

        Returns:
            Data_item which served as input
            List of BoundingBox objects containing bounding box information
            for every prediction made by the model. Only contains bounding boxes which
            are above the thresholds specified in configuration file.
        """

        if self.darknet_module is None:
            raise ValueError("The darknet_module=None attribute is not initialized!")

        bounding_boxes: List[BoundingBox] = list()

        if isinstance(data_item, np.ndarray):
            image: np.ndarray = data_item  # type: ignore[type-arg]
        else:
            image = cv2.imread(data_item)

        _, darknet_image = self._numpy_to_darknet_image(img=image)

        predictions = self.darknet_module.detect_image(
            self.network,
            self.mapper.get_model_class_names(),
            darknet_image,
            thresh=self.configuration.inference_config.score_threshold,
            hier_thresh=self.configuration.inference_config.hier_threshold,
            nms=self.configuration.inference_config.nms_threshold,
        )

        for prediction in predictions:
            x = prediction[2][0]
            y = prediction[2][1]
            w = prediction[2][2]
            h = prediction[2][3]

            x -= w / 2
            y -= h / 2

            model_class_name: str = prediction[0]

            bounding_boxes.extend(
                self.build_bounding_boxes(
                    box_list=(x, y, w, h),
                    box_format=ObjectDetectionBBoxFormats.XYWH,
                    class_identifiers=self.mapper.map_model_class_name_to_output_class_identifier(
                        class_name=model_class_name
                    ),
                    model_class_identifier=ClassIdentifier(
                        class_id=self.mapper.map_annotation_class_name_to_model_class_id(
                            class_name=model_class_name
                        ),
                        class_name=model_class_name,
                    ),
                    score=float(prediction[1]) / 100,
                    difficult=False,
                    occluded=False,
                    content="",
                )
            )

        return data_item, bounding_boxes
