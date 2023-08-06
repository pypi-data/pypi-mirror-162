# Copyright 2021 Open Logistics Foundation
#
# Licensed under the Open Logistics License 1.0.
# For details on the licensing terms, see the LICENSE file.

"""
Module for enumerating options for different configurations for different parameters.
The constant classes listed here are e.g. used in data generators to
limit the options in configuration.
"""

from mlcvzoo_base.configuration.structs import BaseType


class OptimizerTypes(BaseType):
    """Constants for supported Optimizer Types"""

    # other optimizers: https://keras.io/api/optimizers/
    ADAM = "Adam"
    SGD = "SGD"


class LossTypes(BaseType):
    """Constants for supported loss Types"""

    # other losses: https://keras.io/losses/
    CATEGORICAL_CROSSENTROPY = "categorical_crossentropy"


class DataSubsets(BaseType):
    """
    Data subsets for differentiating setups of the data generators
    in Generator class in image_generator.py
    """

    TRAINING = "training"
    VALIDATION = "validation"
    TEST = "test"


class DataGeneratorConfig(BaseType):
    """
    Validation split is not used in our implementation as we offer an interface
    by the net_config.yaml files where a user can define separate directories for
    training, validation and test.

    It is only a necessary value for initializing the ImageDataGenerator from
    tensorflow.keras.preprocessing.image.
    """

    VALIDATION_SPLIT = 0.0


class ImageDataFrameColumns(BaseType):
    """
    Constants for dataframe column names for loading annotation from file into
    dataframe, which is the interface of the keras generator from dataframe
    """

    # the constants are variables of the keras image data generator function flow_from_dataframe
    # the CLASS_ID is for creating the class label column in the used dataframe and the
    #  respective parameter 'classes' in the flow_from_dataframe function
    # IMAGE_PATH is the name of the column in the dataframe which holds the respective
    #  information about the image paths and is used in the 'x_col' parameter of flow_from_dataframe
    # CLASS_MODE is for setting the respective parameter in flow_from_dataframe which describes the
    #  mode of how the label information is given
    # keras api description of the parameters classes, x_col and class_mode can be found here:
    # https://www.tensorflow.org/api_docs/python/tf/keras/preprocessing/image/ImageDataGenerator
    CLASS_ID = "class_id"
    IMAGE_PATH = "image_path"
    CLASS_MODE = "raw"  # one of "binary", "categorical", "input", "multi_output", "raw", sparse" or None


class ImageDataFromDirectory(BaseType):
    """Constants for the class mode when loading data from directory"""

    # class_mode is a variable of the keras image data generator function flow_from_directory
    # keras api description of class mode can be found here:
    # https://www.tensorflow.org/api_docs/python/tf/keras/preprocessing/image/ImageDataGenerator
    CLASS_MODE = (
        "categorical"  # one of "categorical", "binary", "sparse", "input", or None
    )
