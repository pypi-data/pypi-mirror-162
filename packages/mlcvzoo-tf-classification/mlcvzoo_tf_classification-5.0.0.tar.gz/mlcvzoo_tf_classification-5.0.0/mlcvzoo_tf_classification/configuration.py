# Copyright 2021 Open Logistics Foundation
#
# Licensed under the Open Logistics License 1.0.
# For details on the licensing terms, see the LICENSE file.

"""
Definition of the Config that is used to configure the models of the
mlcvzoo_tf_classification package.
"""
import logging
from typing import Dict, List, Optional, Union

import related
from config_builder.BaseConfigClass import BaseConfigClass
from mlcvzoo_base.api.configuration import Configuration
from mlcvzoo_base.configuration.annotation_handler_config import AnnotationHandlerConfig
from mlcvzoo_base.configuration.class_mapping_config import ClassMappingConfig
from mlcvzoo_base.configuration.reduction_mapping_config import ReductionMappingConfig

from .const import LossTypes, OptimizerTypes

logger = logging.getLogger(__name__)


@related.mutable(strict=True)
class NetConfig(BaseConfigClass):
    """
    Here the base parameters for the model configuration are extracted.
    """

    model_path: str = related.StringField()

    build_custom_net: bool = related.BooleanField()

    input_shape: List[int] = related.SequenceField(cls=int)

    save_weights_only: Optional[bool] = related.BooleanField(
        required=False, default=True
    )

    def check_values(self) -> bool:
        success: bool = True

        if self.input_shape is not None:
            success = success and len(self.input_shape) == 3
            if not success:
                logger.error(
                    "\nCheck for attribute 'input_shape' failed\n"
                    "condition: len(input_shape) == 3, found input_shape=%s"
                    % self.input_shape
                )

        return success


@related.mutable(strict=True)
class InferenceConfig(BaseConfigClass):
    """
    Here the parameters for model inference are extracted.
    """

    top: Optional[int] = related.IntegerField(required=False, default=None)
    score_threshold: Optional[float] = related.FloatField(required=False, default=None)

    reduction_class_mapping: Optional[ReductionMappingConfig] = related.ChildField(
        cls=ReductionMappingConfig, required=False, default=None
    )

    def check_values(self) -> bool:
        success: bool = True

        if self.top is not None:
            success = success and self.top >= 1
            if not success:
                logger.error(
                    "\nCheck for attribute 'top' failed\n"
                    "condition: top >= 1, found top=%s" % self.top
                )

        if self.score_threshold is not None:
            success = success and 0.0 <= self.score_threshold <= 1.0
            if not success:
                logger.error(
                    "\nCheck for attribute 'top' failed\n"
                    "condition: 0.0 <= score_threshold <= 1.0, found score_threshold=%s"
                    % self.score_threshold
                )

        return success


@related.mutable(strict=True)
class FlowFromDirectoryConfig(BaseConfigClass):
    """
    Here the parameters for the training data are extracted, when it
    is available in a directory.
    """

    directory: str = related.StringField(default="")


@related.mutable(strict=True)
class FlowFromDataframeConfig(BaseConfigClass):
    """
    Here the parameters for the training data are extracted, when it
    is available in a specific file.
    """

    ann_file_list: List[str] = related.SequenceField(cls=str)
    annotation_handler_config_path: str = related.StringField(default="")
    annotation_handler_config: Optional[AnnotationHandlerConfig] = related.ChildField(
        cls=AnnotationHandlerConfig, required=False, default=None
    )


@related.mutable(strict=True)
class GeneratorConfig(BaseConfigClass):
    """
    Here the parameter for data source is extracted. Note that we have
    exclusive options here.
    """

    # mutually exclusive fields
    flow_from_directory: Optional[FlowFromDirectoryConfig] = related.ChildField(
        cls=FlowFromDirectoryConfig, default=None, required=False
    )

    flow_from_dataframe: Optional[FlowFromDataframeConfig] = related.ChildField(
        cls=FlowFromDataframeConfig, default=None, required=False
    )


@related.mutable(strict=True)
class ModelCheckpointConfig(BaseConfigClass):
    """
    Here the parameters for ModelCheckpoint callback are extracted.
    The parameters follow the definition of tensorflow. For detailed
    information on how to set the parameters have a look at their documentation:
    https://www.tensorflow.org/api_docs/python/tf/keras/callbacks/ModelCheckpoint

    Note that the parameter save_weights_only is listed under NetConfig class.
    """

    # specify directory where to store trained models
    work_dir: str = related.StringField()

    monitor: Optional[str] = related.StringField(required=False, default="val_loss")
    verbose: Optional[int] = related.IntegerField(required=False, default=1)
    save_best_only: Optional[bool] = related.BooleanField(required=False, default=False)
    mode: Optional[str] = related.StringField(required=False, default="auto")
    save_freq: Optional[Union[str, int]] = related.StringField(
        required=False, default="epoch"
    )
    initial_value_threshold: Optional[float] = related.FloatField(
        required=False, default=None
    )

    def check_values(self) -> bool:
        return self.verbose in [0, 1] and self.mode in ["auto", "min", "max"]


@related.mutable(strict=True)
class TrainConfig(BaseConfigClass):
    """
    Here the parameters for the data generators and training hyper-parameters
    are extracted.
    """

    batch_size: int = related.IntegerField()
    epochs: int = related.IntegerField()

    metrics: List[str] = related.SequenceField(cls=str)

    rotation_range: int = related.IntegerField()
    horizontal_flip: bool = related.BooleanField()
    zoom_range: float = related.FloatField()
    rescale: bool = related.BooleanField()

    train_generator_config: GeneratorConfig = related.ChildField(cls=GeneratorConfig)
    val_generator_config: GeneratorConfig = related.ChildField(cls=GeneratorConfig)
    test_generator_config: GeneratorConfig = related.ChildField(cls=GeneratorConfig)

    model_checkpoint_config: ModelCheckpointConfig = related.ChildField(
        cls=ModelCheckpointConfig
    )

    featurewise_center: Optional[bool] = related.BooleanField(
        required=False, default=False
    )
    featurewise_std_normalization: Optional[bool] = related.BooleanField(
        required=False, default=False
    )
    vertical_flip: Optional[bool] = related.BooleanField(required=False, default=True)
    width_shift_range: Optional[float] = related.FloatField(required=False, default=0.2)
    height_shift_range: Optional[float] = related.FloatField(
        required=False, default=0.2
    )

    seed: Optional[int] = related.IntegerField(required=False, default=None)

    color_mode: str = related.StringField(default="rgb")
    shuffle: bool = related.BooleanField(default=False)

    # specify a directory where to store augmented images
    save_to_dir: Optional[str] = related.StringField(required=False, default=None)
    save_prefix: Optional[str] = related.StringField(required=False, default="")
    save_format: Optional[str] = related.StringField(required=False, default="png")
    follow_links: Optional[bool] = related.BooleanField(required=False, default=False)
    interpolation: Optional[str] = related.StringField(
        required=False, default="nearest"
    )

    loss: str = related.StringField(default=LossTypes.CATEGORICAL_CROSSENTROPY)
    optimizer: str = related.StringField(default=OptimizerTypes.ADAM)
    learning_rate: float = related.FloatField(default=0.001)
    # momentum optional for training
    momentum: Optional[float] = related.FloatField(default=0.9)

    def check_values(self) -> bool:
        return (
            self.optimizer
            in OptimizerTypes.get_values_as_list(class_type=OptimizerTypes)
            and self.loss in LossTypes.get_values_as_list(class_type=LossTypes)
            and self.color_mode in ["grayscale", "rgb", "rgba"]
            and self.save_format in ["png", "jpeg"]
            and self.interpolation in ["nearest", "bilinear", "bicubic"]
        )


@related.mutable(strict=True)
class Config(BaseConfigClass, Configuration):
    """
    Here the parameter groups are extracted and the respective detailed
    config classes as listed above are called.
    """

    mutual_attribute_map: Dict[str, List[str]] = {
        "GeneratorConfig": ["flow_from_directory", "flow_from_dataframe"]
    }

    net_config: NetConfig = related.ChildField(cls=NetConfig)

    class_mapping: ClassMappingConfig = related.ChildField(ClassMappingConfig)

    inference_config: InferenceConfig = related.ChildField(cls=InferenceConfig)

    train_config: TrainConfig = related.ChildField(cls=TrainConfig)
