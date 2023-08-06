# Copyright 2021 Open Logistics Foundation
#
# Licensed under the Open Logistics License 1.0.
# For details on the licensing terms, see the LICENSE file.

"""
The TrainableNetBasedModel class configures the model for training and inference.
The respective model is compiled from the provided configuration file and net class.
Input parameters are parsed via the AnnotationMapper.
Data flow is regulated via Generators.
"""
import logging
import os
import typing
from typing import Dict, Optional

import numpy as np
import tensorflow as tf
from mlcvzoo_base.configuration.utils import (
    create_configuration as create_basis_configuration,
)
from tensorflow.keras.applications.xception import Xception, preprocess_input

from mlcvzoo_tf_classification.base_model import BaseModel, ImageType
from mlcvzoo_tf_classification.xception.configuration import XceptionConfig

logger = logging.getLogger(__name__)


class XceptionModel(
    BaseModel[XceptionConfig],
):
    """
    The model is compiled from the respective net class and configuration file.
    Input details are parsed using the AnnotationClassMapper.
    """

    def __init__(
        self,
        from_yaml: str,
        configuration: Optional[XceptionConfig] = None,
        string_replacement_map: Optional[Dict[str, str]] = None,
    ):
        BaseModel.__init__(
            self,
            from_yaml=from_yaml,
            configuration=configuration,
            string_replacement_map=string_replacement_map,
        )

    def _init_inference_model(self) -> None:
        input_shape_config = tuple(self.configuration.net_config.input_shape)

        weights_config = None
        # check both, as model_path can be either the preconfigured keras weights or
        # pretrained weights at path
        if self.configuration.net_config.model_path == "imagenet" or os.path.isfile(
            self.configuration.net_config.model_path
        ):
            weights_config = self.configuration.net_config.model_path

        self.net = Xception(
            # custom_net implies (not include_top)
            include_top=not self.configuration.net_config.build_custom_net,
            weights=weights_config,
            input_tensor=None,
            input_shape=input_shape_config,
            pooling=None,
            classes=self.mapper.num_classes,
            classifier_activation="softmax",
        )

        if self.configuration.net_config.build_custom_net:
            self.net.trainable = False
            # set input shape
            inputs = tf.keras.Input(shape=self.net.input_shape[1:])

            # set custom top
            previous_net_output = self.net(inputs, training=False)
            in_between_layer = tf.keras.layers.Flatten()(previous_net_output)
            outputs = tf.keras.layers.Dense(self.mapper.num_classes)(in_between_layer)

            self.net = tf.keras.Model(inputs, outputs)

    def store(self, checkpoint_path: str) -> None:
        BaseModel.store(self, checkpoint_path)

    def restore(self, checkpoint_path: str) -> None:
        BaseModel.restore(self, checkpoint_path)

    @staticmethod
    def create_configuration(
        from_yaml: Optional[str] = None,
        configuration: Optional[XceptionConfig] = None,
        string_replacement_map: Optional[Dict[str, str]] = None,
    ) -> XceptionConfig:
        return typing.cast(
            XceptionConfig,
            create_basis_configuration(
                configuration_class=XceptionConfig,
                from_yaml=from_yaml,
                input_configuration=configuration,
                string_replacement_map=string_replacement_map,
            ),
        )

    @staticmethod
    def preprocess_data(input_data: ImageType) -> ImageType:
        return preprocess_input(input_data)  # type: ignore
