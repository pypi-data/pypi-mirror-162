# Copyright 2021 Open Logistics Foundation
#
# Licensed under the Open Logistics License 1.0.
# For details on the licensing terms, see the LICENSE file.

"""
Module for handling annotation utility methods that are used across the
mlcvzoo_tf_classification package.
"""

from typing import Any, Dict, List

import pandas as pd
from mlcvzoo_base.api.data.annotation import BaseAnnotation

from mlcvzoo_tf_classification.const import ImageDataFrameColumns


def annotation_list_to_dataframe(annotations: List[BaseAnnotation]) -> pd.DataFrame:
    """
    Build a pandas dataframe object out of a given list of annotations.

    Args:
        annotations: List of BaseAnnotation that should be transformed to a dataframe

    Returns:
        A pandas.DataFrame representation of the input annotations

    """

    annotation_dict: Dict[str, List[Any]] = dict()

    annotation_dict[ImageDataFrameColumns.CLASS_ID] = []
    annotation_dict[ImageDataFrameColumns.IMAGE_PATH] = []

    # TODO: both possibilities to use either classifications or max bounding_boxes

    for annotation in annotations:
        for bounding_box in annotation.get_bounding_boxes(include_segmentations=True):

            # TODO: may change class id to global class id induced by mapping
            annotation_dict[ImageDataFrameColumns.CLASS_ID].append(
                bounding_box.class_id
            )
            annotation_dict[ImageDataFrameColumns.IMAGE_PATH].append(
                annotation.image_path
            )

    annotation_df: pd.DataFrame = pd.DataFrame(annotation_dict)
    annotation_df[ImageDataFrameColumns.CLASS_ID] = annotation_df[
        ImageDataFrameColumns.CLASS_ID
    ].astype(
        "string"
    )  # int64, category
    annotation_df[ImageDataFrameColumns.IMAGE_PATH] = annotation_df[
        ImageDataFrameColumns.IMAGE_PATH
    ].astype("string")

    return annotation_df
