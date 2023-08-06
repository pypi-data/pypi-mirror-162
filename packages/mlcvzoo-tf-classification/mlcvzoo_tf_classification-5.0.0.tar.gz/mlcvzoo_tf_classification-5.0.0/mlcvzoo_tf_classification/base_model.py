# Copyright 2021 Open Logistics Foundation
#
# Licensed under the Open Logistics License 1.0.
# For details on the licensing terms, see the LICENSE file.

"""
Module for handling the implementation of a generic base model that wraps tensorflow
classification models.
"""

import logging
import os
from abc import ABC, abstractmethod
from typing import Dict, Generic, List, Optional, Tuple, Type, TypeVar, Union, cast

import numpy as np
import tensorflow as tf
from mlcvzoo_base.api.data.annotation_class_mapper import AnnotationClassMapper
from mlcvzoo_base.api.data.class_identifier import ClassIdentifier
from mlcvzoo_base.api.data.classification import Classification
from mlcvzoo_base.api.interfaces import NetBased, Trainable
from mlcvzoo_base.api.model import ClassificationModel
from nptyping import Int, NDArray, Shape
from tensorflow.keras.callbacks import ModelCheckpoint
from tensorflow.keras.optimizers import SGD, Adam
from tensorflow.keras.preprocessing.image import array_to_img, img_to_array, load_img

from mlcvzoo_tf_classification.const import OptimizerTypes
from mlcvzoo_tf_classification.custom_block.configuration import CustomBlockConfig
from mlcvzoo_tf_classification.image_generator import setup_generators
from mlcvzoo_tf_classification.xception.configuration import XceptionConfig

logger = logging.getLogger(__name__)

ConfigurationType = TypeVar("ConfigurationType", CustomBlockConfig, XceptionConfig)

ImageType = NDArray[Shape["Height, Width, Any"], Int]


class BaseModel(
    ClassificationModel[ConfigurationType, Union[str, ImageType]],
    NetBased[tf.keras.Model],
    Trainable,
    ABC,
    Generic[ConfigurationType],
):
    """
    Generic base model that wraps tensorflow classification models. It provides the functionality
    for handling the configuration, prediction and training of models.
    """

    def __init__(
        self,
        from_yaml: str,
        configuration: Optional[ConfigurationType] = None,
        string_replacement_map: Optional[Dict[str, str]] = None,
    ):
        self.net: Optional[tf.keras.Model] = None
        self.configuration: ConfigurationType = self.create_configuration(  # type: ignore
            from_yaml=from_yaml,
            configuration=configuration,
            string_replacement_map=string_replacement_map,
        )
        ClassificationModel.__init__(
            self,
            unique_name=os.path.basename(from_yaml),
            configuration=self.configuration,
            init_for_inference=True,
            mapper=AnnotationClassMapper(
                class_mapping=self.configuration.class_mapping,
                reduction_mapping=self.configuration.inference_config.reduction_class_mapping,
            ),
        )
        NetBased.__init__(
            self,
            net=self.net,
        )
        Trainable.__init__(self)

    def store(self, checkpoint_path: str) -> None:
        if self.net is None:
            raise ValueError(
                "In order to store a checkpoint, the net attribute has"
                "to be initialized!"
            )

        if self.configuration.net_config.save_weights_only:
            self.net.save_weights(checkpoint_path)
        else:
            tf.keras.models.save_model(self.net, filepath=checkpoint_path)

    def restore(self, checkpoint_path: str) -> None:

        if self.net is None:
            raise ValueError(
                "In order to restore a checkpoint, the net attribute has"
                "to be initialized!"
            )

        if self.configuration.net_config.save_weights_only:
            self.net.load_weights(checkpoint_path)
        else:
            self.net = tf.keras.models.load_model(filepath=checkpoint_path)

    @property
    def num_classes(self) -> int:
        return self.mapper.num_classes

    def get_classes_id_dict(self) -> Dict[int, str]:
        return self.mapper.annotation_class_id_to_model_class_name_map

    @staticmethod
    @abstractmethod
    def create_configuration(
        from_yaml: Optional[str] = None,
        configuration: Optional[ConfigurationType] = None,
        string_replacement_map: Optional[Dict[str, str]] = None,
    ) -> ConfigurationType:
        raise NotImplementedError(
            "Must be implemented by sub-class: create_configuration(...)."
        )

    @staticmethod
    @abstractmethod
    def preprocess_data(input_data: ImageType) -> ImageType:
        """
        Preprocesses the given input data

        Args:
            input_data: The input data to preprocess

        Returns:
            The preprocessed data
        """
        raise NotImplementedError(
            "Must be implemented by sub-class: preprocess_data(...)."
        )

    def predict(
        self, data_item: Union[str, ImageType]
    ) -> Tuple[Union[str, ImageType], List[Classification]]:
        """
        Predicts a class for the given data_item.

        Arguments:
            data_item: Input data. It could be:
                - A string to the image file
                - A Numpy array representation of the image
        Returns:
            The data_item and also a list of predictions which length depends
            on the configuration of the model. That is to consider the top x classes
            with the highest scores or only classes with a score not less than the
            configured score value. If these are not set the model will output
            prediction scores for each class.
        """

        assert self.net is not None

        predictions: List[Classification] = []
        target_size = tuple(self.configuration.net_config.input_shape[:2])

        if isinstance(data_item, str):
            image = load_img(
                path=data_item,
                grayscale=False,
                color_mode="rgb",
                target_size=None,
                interpolation="nearest",
            )

            image = image.resize(target_size)
            data_array = img_to_array(image)
            data_array = np.expand_dims(data_array, axis=0)

        elif isinstance(data_item, np.ndarray):
            image = array_to_img(x=data_item)
            image = image.resize(target_size)
            data_array = img_to_array(image)
            data_array = np.expand_dims(data_array, axis=0)

        else:
            # This should be impossible
            logger.warning("Cannot predict on data_item of type: %s", type(data_item))
            return data_item, predictions

        # preprocessing according to  Xception implementation in keras
        data = self.preprocess_data(input_data=data_array)

        # predict labels on data, returns a Tensor with shape (1,nb_classes)
        net_predictions = self.net(data)

        # sort indices by score
        ids_by_score = tf.argsort(net_predictions, axis=1, direction="DESCENDING")
        ids_by_score = tf.keras.backend.eval(ids_by_score)[0]

        for i, _ in enumerate(net_predictions[0]):
            class_id = ids_by_score[i]

            score = tf.cast(net_predictions[0][class_id], float, name=None)

            if (
                self.configuration.inference_config.score_threshold is not None
                and score >= self.configuration.inference_config.score_threshold
            ):
                continue

            class_identifiers = (
                self.mapper.map_model_class_id_to_output_class_identifier(
                    class_id=class_id
                )
            )

            model_class_identifier = ClassIdentifier(
                class_id=class_id,
                class_name=self.mapper.map_annotation_class_id_to_model_class_name(
                    class_id=class_id
                ),
            )

            for class_identifier in class_identifiers:
                predictions.append(
                    Classification(
                        class_identifier=class_identifier,
                        model_class_identifier=model_class_identifier,
                        score=score,
                    )
                )

        if self.configuration.inference_config.top is not None:
            predictions = predictions[: self.configuration.inference_config.top]

        return data_item, predictions

    def train(self) -> None:
        """
        Trains the model specified in self.net with the parameters given in self.configuration.
        """

        assert self.net is not None

        train_generator, validation_generator = setup_generators(
            net_config=self.configuration.net_config,
            configuration=self.configuration,
            number_classes=self.mapper.num_classes,
        )

        if train_generator is not None:
            # set optimizer
            if self.configuration.train_config.optimizer == OptimizerTypes.SGD:
                optimizer = SGD(
                    learning_rate=self.configuration.train_config.learning_rate,
                    momentum=self.configuration.train_config.momentum,
                )
            elif self.configuration.train_config.optimizer == OptimizerTypes.ADAM:
                optimizer = Adam(
                    learning_rate=self.configuration.train_config.learning_rate
                )
            else:
                optimizer = None

            if optimizer is not None:

                # compile model
                self.net.compile(
                    optimizer=optimizer,
                    loss=self.configuration.train_config.loss,
                    metrics=list(self.configuration.train_config.metrics),
                )

                # train the model
                logger.info(
                    "train params: \n"
                    "- epochs: %s,\n"
                    "- batch size: %s,\n"
                    "- validation generator: %s,\n"
                    "- number of val samples: %s, \n"
                    "- number of train samples: %s",
                    self.configuration.train_config.epochs,
                    self.configuration.train_config.batch_size,
                    validation_generator,
                    validation_generator.n,
                    train_generator.n,
                )

                steps_per_epoch = int(
                    train_generator.n / self.configuration.train_config.batch_size
                )
                validation_steps = int(
                    validation_generator.n / self.configuration.train_config.batch_size
                )

                checkpoint_path = os.path.join(
                    self.configuration.train_config.model_checkpoint_config.work_dir,
                    "cp-{epoch:04d}.ckpt",
                )

                callback = ModelCheckpoint(
                    filepath=checkpoint_path,
                    monitor=self.configuration.train_config.model_checkpoint_config.monitor,
                    verbose=self.configuration.train_config.model_checkpoint_config.verbose,
                    save_best_only=self.configuration.train_config.model_checkpoint_config.save_best_only,
                    save_weights_only=self.configuration.net_config.save_weights_only,
                    mode=self.configuration.train_config.model_checkpoint_config.mode,
                    save_freq=self.configuration.train_config.model_checkpoint_config.save_freq,
                    options=None,
                    initial_value_threshold=self.configuration.train_config.model_checkpoint_config.initial_value_threshold,
                )

                self.net.fit(
                    train_generator,
                    callbacks=[callback],
                    epochs=self.configuration.train_config.epochs,
                    steps_per_epoch=steps_per_epoch,
                    validation_data=validation_generator,
                    validation_steps=validation_steps,
                )

            else:
                logger.error(
                    "Could not run training, no optimizer could be initialized"
                )

        else:
            logger.warning(
                "Training data generator is None. Training will not be executed"
            )
