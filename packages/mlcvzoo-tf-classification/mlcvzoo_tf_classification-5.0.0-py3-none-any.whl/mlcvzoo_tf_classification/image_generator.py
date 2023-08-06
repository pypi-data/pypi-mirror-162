# Copyright 2021 Open Logistics Foundation
#
# Licensed under the Open Logistics License 1.0.
# For details on the licensing terms, see the LICENSE file.

"""
Module for handling the generation of images for the training of
tensorflow classification models.
"""

import logging
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from keras_preprocessing.image import DataFrameIterator, DirectoryIterator, Iterator
from mlcvzoo_base.api.data.annotation import BaseAnnotation
from mlcvzoo_base.data_preparation.annotation_handler import AnnotationHandler
from tensorflow.keras.preprocessing.image import ImageDataGenerator

from mlcvzoo_tf_classification.annotation_utils import annotation_list_to_dataframe
from mlcvzoo_tf_classification.configuration import Config, NetConfig, TrainConfig
from mlcvzoo_tf_classification.const import (
    DataGeneratorConfig,
    DataSubsets,
    ImageDataFrameColumns,
    ImageDataFromDirectory,
)

logger = logging.getLogger(__name__)


def setup_generators(
    net_config: NetConfig, configuration: Config, number_classes: int
) -> Tuple[Iterator, Iterator]:
    """
    Sets up data generators based on the model's configuration

    Returns:
        A training data generator
        A validation data generator
    """
    img_gen = Generators(
        net_config=net_config,
        train_config=configuration.train_config,
        string_replacement_map=configuration.string_replacement_map,
        number_classes=number_classes,
    )
    return img_gen.get_train_generator(), img_gen.get_val_generator()


class Generators:
    """
    A wrapper for the DataIterators offered by keras.preprocessing
    How data will be generated is specified in the respective model config file.
    """

    def __init__(
        self,
        net_config: NetConfig,
        train_config: TrainConfig,
        number_classes: int,
        string_replacement_map: Optional[Dict[str, str]] = None,
    ) -> None:
        self.img_size = net_config.input_shape[:2]
        self.number_classes = number_classes

        self.train_config = train_config

        self.string_replacement_map: Optional[Dict[str, str]] = string_replacement_map

        self._build_train_generator()
        self._build_val_generator()
        self._build_test_generator()

    def _build_train_generator(self) -> None:
        if self.train_config.train_generator_config.flow_from_directory is not None:
            self.train_generator = self.build_generator(
                subset=DataSubsets.TRAINING,
                directory=self.train_config.train_generator_config.flow_from_directory.directory,
            )
        elif self.train_config.train_generator_config.flow_from_dataframe is not None:
            self.annotation_handler = AnnotationHandler(
                configuration=self.train_config.train_generator_config.flow_from_dataframe.annotation_handler_config,
                yaml_config_path=self.train_config.train_generator_config.flow_from_dataframe.annotation_handler_config_path,
                string_replacement_map=self.string_replacement_map,
            )

            self.train_generator = self.build_generator(
                subset=DataSubsets.TRAINING,
                ann_file_list=self.train_config.train_generator_config.flow_from_dataframe.ann_file_list,
            )

            log_message = (
                "ANNOTATION HANDLER CONFIG: "
                f"{self.train_config.train_generator_config.flow_from_dataframe.annotation_handler_config}\n"
                "ANNOTATION HANDLER CONFIG PATH: "
                f"{self.train_config.train_generator_config.flow_from_dataframe.annotation_handler_config_path}"
            )

            logger.info(log_message)

    def _build_val_generator(self) -> None:
        if self.train_config.val_generator_config.flow_from_directory is not None:
            self.val_generator = self.build_generator(
                subset=DataSubsets.VALIDATION,
                directory=self.train_config.val_generator_config.flow_from_directory.directory,
            )
        elif self.train_config.val_generator_config.flow_from_dataframe is not None:
            self.val_generator = self.build_generator(
                subset=DataSubsets.VALIDATION,
                ann_file_list=self.train_config.val_generator_config.flow_from_dataframe.ann_file_list,
            )

    def _build_test_generator(self) -> None:
        if self.train_config.test_generator_config.flow_from_directory is not None:
            self.test_generator = self.build_generator(
                subset=DataSubsets.TEST,
                directory=self.train_config.test_generator_config.flow_from_directory.directory,
            )
        elif self.train_config.test_generator_config.flow_from_dataframe is not None:
            self.test_generator = self.build_generator(
                subset=DataSubsets.TEST,
                ann_file_list=self.train_config.test_generator_config.flow_from_dataframe.ann_file_list,
            )

    def get_train_generator(self) -> Iterator:
        """Returns the generator for training"""
        return self.train_generator

    def get_val_generator(self) -> Iterator:
        """Returns the generator for validation"""
        return self.val_generator

    def get_test_generator(self) -> Iterator:
        """Returns the generator for test"""
        return self.test_generator

    def build_generator(
        self,
        subset: str,
        directory: Optional[str] = None,
        ann_file_list: Optional[List[str]] = None,
    ) -> Iterator:
        """
        Takes a parameter which indicates the subset of the data
        (Training, Validation or Test, see const.DataSubsets),
        and the directory or annotation file, which holds the data.
        Returns an iterator for the specified subset with the specified data.
        Note that the iterator for the training subset is more configurable than
        the other two subset generators.

        Args:
            subset: String that indicates processed subset one of DataSubsets,
            directory: Optional path where the data for the generator is located,
            ann_file_list: Optional list that holds the data

        Returns:
            Iterator, either DirectoryIterator or DataFrameIterator depending on data source

        Raises:
            ValueError, if the provided subset is not in DataSubsets or none of the data sources
             is given.
        """
        logger.info(
            " - annotation file: %s,\n - data subset: %s", ann_file_list, subset
        )

        if subset == DataSubsets.TRAINING:
            # Base train/validation generator
            data_generator = ImageDataGenerator(
                rescale=self.train_config.rescale,
                validation_split=DataGeneratorConfig.VALIDATION_SPLIT,
                featurewise_center=self.train_config.featurewise_center,
                featurewise_std_normalization=self.train_config.featurewise_std_normalization,
                rotation_range=self.train_config.rotation_range,
                width_shift_range=self.train_config.width_shift_range,
                height_shift_range=self.train_config.height_shift_range,
                horizontal_flip=self.train_config.horizontal_flip,
                vertical_flip=self.train_config.vertical_flip,
                zoom_range=self.train_config.zoom_range,
            )

        elif subset in (DataSubsets.VALIDATION, DataSubsets.TEST):
            # to avoid augmentation of data in validation split
            data_generator = ImageDataGenerator(
                rescale=self.train_config.rescale,
                validation_split=DataGeneratorConfig.VALIDATION_SPLIT,
            )
        else:
            raise ValueError(
                f"The subset '{subset}' is not support, "
                f"use either of: {DataSubsets.get_values_as_list(class_type=DataSubsets)}"
            )

        if ann_file_list is not None:
            logger.info(" - source: dataframe -> df generator")
            return self._build_df_generator(
                data_generator=data_generator, ann_file_list=ann_file_list
            )
        if directory is not None:
            logger.info(" - source: directory (%s) -> dir generator", directory)
            return self._build_dir_generator(
                data_generator=data_generator, directory=directory
            )
        raise ValueError(
            "Either provide data for parameter 'ann_file_list' or 'directory'"
        )

    def _build_df_generator(
        self, data_generator: ImageDataGenerator, ann_file_list: List[str]
    ) -> DataFrameIterator:

        annotations: List[BaseAnnotation] = []

        for csv_file_path in ann_file_list:
            annotations.extend(
                self.annotation_handler.parse_annotations_from_csv(
                    csv_file_path=csv_file_path
                )
            )

        train_df = annotation_list_to_dataframe(annotations=annotations)

        logger.info(
            " => created dataframe of shape: %s, with columns: %s",
            train_df.shape,
            train_df.columns,
        )

        one_hot_df = self._create_one_hot_encodings(train_df=train_df)
        train_df = train_df.join(one_hot_df)

        logger.info(
            "dataframe columns \n %s \n and column types \n %s",
            train_df.columns,
            train_df.dtypes,
        )

        logger.info("build generator from dataframe")

        df_generator = data_generator.flow_from_dataframe(
            dataframe=train_df,
            directory=None,
            x_col=ImageDataFrameColumns.IMAGE_PATH,
            y_col=list(train_df.iloc[:, 2:].columns),
            subset=None,
            class_mode=ImageDataFrameColumns.CLASS_MODE,
            target_size=self.img_size,
            color_mode=self.train_config.color_mode,
            shuffle=self.train_config.shuffle,
            batch_size=self.train_config.batch_size,
            seed=self.train_config.seed,
            save_to_dir=self.train_config.save_to_dir,
            save_prefix=self.train_config.save_prefix,
            save_format=self.train_config.save_format,
            follow_links=self.train_config.follow_links,
            interpolation=self.train_config.interpolation,
        )

        return df_generator

    def _create_one_hot_encodings(self, train_df: pd.DataFrame) -> pd.DataFrame:
        labels = []

        for i in range(len(train_df)):
            one_hot_enc = np.zeros(self.number_classes)
            class_id = int(train_df.loc[i, ImageDataFrameColumns.CLASS_ID])
            one_hot_enc[class_id] = 1
            labels.append(one_hot_enc)

        labels_as_array = np.asarray(labels)

        one_hot_df = pd.DataFrame(labels_as_array)

        return one_hot_df

    def _build_dir_generator(
        self, data_generator: ImageDataGenerator, directory: str
    ) -> DirectoryIterator:

        logger.info("build generator from directory")

        dir_generator = data_generator.flow_from_directory(
            directory=directory,
            target_size=self.img_size,
            classes=None,
            subset=None,
            class_mode=ImageDataFromDirectory.CLASS_MODE,
            color_mode=self.train_config.color_mode,
            shuffle=self.train_config.shuffle,
            batch_size=self.train_config.batch_size,
            seed=self.train_config.seed,
            save_to_dir=self.train_config.save_to_dir,
            save_prefix=self.train_config.save_prefix,
            save_format=self.train_config.save_format,
            follow_links=self.train_config.follow_links,
            interpolation=self.train_config.interpolation,
        )
        return dir_generator
