# Copyright 2021 Open Logistics Foundation
#
# Licensed under the Open Logistics License 1.0.
# For details on the licensing terms, see the LICENSE file.

"""
This configuration class is for building python objects from the configuration file.
The respective config fields are parsed via the related component from config_builder module.
"""

from typing import Dict, Optional

import related
from mlcvzoo_base.configuration.detector_configs import DetectorConfig
from mlcvzoo_base.configuration.replacement_config import ReplacementConfig

from mlcvzoo_tf_classification.configuration import Config, TrainConfig
from mlcvzoo_tf_classification.const import LossTypes, OptimizerTypes


@related.mutable(strict=True)
class XceptionTrainConfig(TrainConfig):
    """
    Here the parameters for training are extracted.
    """

    optimizer: str = related.StringField(default=OptimizerTypes.ADAM)
    learning_rate: int = related.FloatField(default=0.002)


@related.mutable(strict=True)
class XceptionConfig(Config):
    """
    Here the model specific training configuration is extracted and the respective
    detailed config class as listed above is called.
    """

    train_config: XceptionTrainConfig = related.ChildField(cls=XceptionTrainConfig)

    base_config: DetectorConfig = related.ChildField(
        cls=DetectorConfig, default=DetectorConfig()
    )
