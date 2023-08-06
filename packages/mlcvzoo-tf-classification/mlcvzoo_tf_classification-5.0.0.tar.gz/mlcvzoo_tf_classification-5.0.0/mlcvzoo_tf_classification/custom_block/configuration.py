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
class CustomBlockTrainConfig(TrainConfig):
    """
    Here the hyper parameters for training are extracted.
    """

    optimizer: str = related.StringField(default=OptimizerTypes.SGD)


@related.mutable(strict=True)
class CustomBlockConfig(Config):
    """
    Here the model specific training configuration is extracted and the respective
    detailed config class as listed above is called.
    """

    train_config: CustomBlockTrainConfig = related.ChildField(
        cls=CustomBlockTrainConfig
    )

    base_config: DetectorConfig = related.ChildField(
        cls=DetectorConfig, default=DetectorConfig()
    )
