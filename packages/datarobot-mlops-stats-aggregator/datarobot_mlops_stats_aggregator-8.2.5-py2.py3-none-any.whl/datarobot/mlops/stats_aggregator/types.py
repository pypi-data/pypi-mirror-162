#  --------------------------------------------------------------------------------
#  Copyright (c) 2021 DataRobot, Inc. and its affiliates. All rights reserved.
#  Last updated 2022.
#
#  DataRobot, Inc. Confidential.
#  This is proprietary source code of DataRobot, Inc. and its affiliates.
#
#  This file and its contents are subject to DataRobot Tool and Utility Agreement.
#  For details, see
#  https://www.datarobot.com/wp-content/uploads/2021/07/DataRobot-Tool-and-Utility-Agreement.pdf.
#
#  --------------------------------------------------------------------------------

from __future__ import absolute_import

from typing import Dict
from typing import List
from typing import NamedTuple
from typing import Optional
from typing import Union

from .histogram import CentroidHistogram

_ = CentroidHistogram

NumericAggregate = NamedTuple(
    "NumericAggregate",
    [
        ("count", int),
        ("missing_count", int),
        ("min", float),
        ("max", float),
        ("sum", float),
        ("sum_of_squares", float),
        ("histogram", CentroidHistogram),
    ],
)

CategoricalAggregate = NamedTuple(
    "CategoricalAggregate",
    [
        ("count", int),
        ("missing_count", int),
        ("text_word_count", Optional[int]),  # Only populated for text features
        ("category_counts", Dict[str, int]),
    ],
)

NumericFeatureStats = Dict[str, NumericAggregate]  # Map of feature names to stats
CategoricalFeatureStats = Dict[str, CategoricalAggregate]  # Map of feature names to stats
PredictionStats = List[NumericAggregate]  # One for regression; per class for classification

FeatureAndPredictionStats = Dict[
    str,
    Union[
        NumericFeatureStats,
        CategoricalFeatureStats,
        PredictionStats,
    ],
]
SegmentStats = Dict[str, Dict[str, FeatureAndPredictionStats]]
AggregatedStats = Dict[
    str,
    Union[
        NumericFeatureStats,
        CategoricalFeatureStats,
        PredictionStats,
        Optional[SegmentStats],
    ],
]


class FeatureType:
    """Type of feature, used to determine how to convert and aggregate feature values.

    Mostly corresponds to EdaTypeEnum, except text is split based on how it is tokenized.
    """

    DATE = "date"
    PERCENTAGE = "percentage"
    LENGTH = "length"
    CURRENCY = "currency"
    NUMERIC = "numeric"
    CATEGORY = "category"
    TEXT_WORDS = "text-words"  # Text that should be split on word boundaries
    TEXT_CHARS = "text-chars"  # Chinese/Japanese text that should be split by characters


class FeatureDescriptor(NamedTuple):
    name: str
    feature_type: str
    format: str = ""


FeatureTypes = List[FeatureDescriptor]
