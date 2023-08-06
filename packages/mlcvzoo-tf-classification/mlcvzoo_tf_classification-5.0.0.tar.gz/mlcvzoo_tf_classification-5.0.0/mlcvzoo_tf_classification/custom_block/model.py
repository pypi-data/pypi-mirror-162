# Copyright 2021 Open Logistics Foundation
#
# Licensed under the Open Logistics License 1.0.
# For details on the licensing terms, see the LICENSE file.

"""
The CustomBlockModel configures the model for training and inference.
The respective model is compiled from the provided configuration file and net class.
Input data classes are parsed via the AnnotationClassMapper.
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
from tensorflow.keras.layers import Conv2D, Dense, Dropout, Flatten, Input, MaxPooling2D

from mlcvzoo_tf_classification.base_model import BaseModel, ImageType
from mlcvzoo_tf_classification.custom_block.configuration import CustomBlockConfig

logger = logging.getLogger(__name__)


class CustomBlockModel(
    BaseModel[CustomBlockConfig],
):
    """
    The model is compiled from the respective net class and configuration file.
    Input details are parsed using the AnnotationClassMapper.
    """

    def __init__(
        self,
        from_yaml: str,
        configuration: Optional[CustomBlockConfig] = None,
        string_replacement_map: Optional[Dict[str, str]] = None,
    ):
        BaseModel.__init__(
            self,
            from_yaml=from_yaml,
            configuration=configuration,
            string_replacement_map=string_replacement_map,
        )

    def _init_inference_model(self) -> None:
        """
        Initializes the networks architecture and sets the instance's attribute self.net
        to a keras model which is initialized with the first and last layers of
        the defined architecture.

        Idea of using building blocks is inspired by VGG16.
        See respective arXiv paper: https://arxiv.org/pdf/1409.1556.pdf
        """

        # 1st block
        input1 = Input(
            shape=self.configuration.net_config.input_shape
        )  # (100, 100, 3))
        conv1_1 = Conv2D(
            filters=32,
            kernel_size=3,
            activation="relu",
            kernel_initializer="he_uniform",
            padding="same",
        )(input1)
        maxpool_1 = MaxPooling2D(pool_size=2)(conv1_1)
        drop_1 = Dropout(0.2)(maxpool_1)  # learns slower, but breaks in at end

        # 2nd block
        conv2_1 = Conv2D(
            filters=64,
            kernel_size=3,
            activation="relu",
            kernel_initializer="he_uniform",
            padding="same",
        )(drop_1)
        maxpool_2 = MaxPooling2D(pool_size=2)(conv2_1)
        drop_2 = Dropout(0.2)(maxpool_2)

        # 3rd block
        conv3_1 = Conv2D(
            filters=128,
            kernel_size=3,
            activation="relu",
            kernel_initializer="he_uniform",
            padding="same",
        )(drop_2)
        maxpool_3 = MaxPooling2D(pool_size=2)(conv3_1)
        drop_3 = Dropout(0.2)(maxpool_3)

        flatten = Flatten()(drop_3)
        dense_1 = Dense(units=128, activation="relu", kernel_initializer="he_uniform")(
            flatten
        )
        drop_4 = Dropout(0.5)(dense_1)
        dense_2 = Dense(units=self.mapper.num_classes, activation="softmax")(drop_4)

        self.net = tf.keras.Model(inputs=input1, outputs=dense_2, name="custom_model")

        if os.path.isfile(self.configuration.net_config.model_path):
            # Where to add weights into the custom model?
            self.restore(checkpoint_path=self.configuration.net_config.model_path)

    def store(self, checkpoint_path: str) -> None:
        BaseModel.store(self, checkpoint_path)

    def restore(self, checkpoint_path: str) -> None:
        BaseModel.restore(self, checkpoint_path)

    @staticmethod
    def create_configuration(
        from_yaml: Optional[str] = None,
        configuration: Optional[CustomBlockConfig] = None,
        string_replacement_map: Optional[Dict[str, str]] = None,
    ) -> CustomBlockConfig:
        return typing.cast(
            CustomBlockConfig,
            create_basis_configuration(
                configuration_class=CustomBlockConfig,
                from_yaml=from_yaml,
                input_configuration=configuration,
                string_replacement_map=string_replacement_map,
            ),
        )

    @staticmethod
    def preprocess_data(input_data: ImageType) -> ImageType:
        return input_data
