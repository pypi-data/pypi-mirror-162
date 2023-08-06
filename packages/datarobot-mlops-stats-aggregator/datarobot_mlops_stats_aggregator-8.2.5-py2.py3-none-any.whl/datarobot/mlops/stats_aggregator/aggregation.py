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

import re
from collections import Counter
from collections import defaultdict
from math import isinf
from math import isnan
from typing import TYPE_CHECKING
from typing import cast

import numpy as np
import six

from .constants import DEFAULT_DISTINCT_CATEGORY_COUNT
from .constants import DEFAULT_DISTINCT_SEGMENT_VALUE_COUNT
from .constants import DEFAULT_HISTOGRAM_BIN_COUNT
from .type_conversion import FeatureType
from .type_conversion import convert_features_for_aggregation
from .types import CategoricalAggregate
from .types import CentroidHistogram
from .types import NumericAggregate

if TYPE_CHECKING:
    from typing import Any
    from typing import Counter as TypedCounter
    from typing import Dict
    from typing import List
    from typing import Mapping
    from typing import Optional
    from typing import Tuple

    import pandas as pd

    from .types import AggregatedStats
    from .types import CategoricalFeatureStats
    from .types import FeatureAndPredictionStats
    from .types import FeatureTypes
    from .types import NumericFeatureStats


true_false_mapper = {"true": 1.0, "false": 0.0}


def floatify(value):
    # type: (Any) -> float
    """Convert a boolean or string (or maybe integer, etc.) value into a Numpy float"""
    try:
        # EDA treats case-insensitive booleans as numerics, so convert
        # any true/false values (case-insensitive) to 1/0 values.
        return true_false_mapper[value.lower()]
    except (KeyError, AttributeError):
        pass

    try:
        # Otherwise, just try to convert the value to a float
        return float(value)
    except ValueError:
        return float('nan')


def convert_series_to_numeric(series):
    # type: (pd.Series) -> pd.Series
    """Convert a Series of mixed/non-float values into a series of type Numpy float"""
    # https://stackoverflow.com/questions/19900202/how-to-determine-whether-a-column-variable-is-numeric-or-not-in-pandas-numpy/46423535
    if not series.dtype.kind in "biufc":
        series = series.map(floatify)
    if not series.dtype == "float64":
        series = series.astype(np.float64)
    return series


def compute_counts(series):
    # type: (pd.Series) -> Tuple[int, int]
    """Count missing (i.e. NA/null) and non-missing values in a series"""
    value_count = cast(int, series.count())
    missing_count = len(series) - value_count
    return value_count, missing_count


def aggregate_numeric_stats(series, histogram_bin_count):
    # type: (pd.Series, Optional[int]) -> NumericAggregate
    """Aggregate a numeric feature series into statistics"""
    value_count, missing_count = compute_counts(series)
    series = series.dropna()
    series = convert_series_to_numeric(series)

    def unreal_to_none(value):
        # type: (Any) -> Any
        return None if isnan(value) or isinf(value) else value

    result = NumericAggregate(
        count=value_count,
        missing_count=missing_count,
        min=unreal_to_none(series.min()),
        max=unreal_to_none(series.max()),
        sum=unreal_to_none(series.sum()),
        sum_of_squares=unreal_to_none(series.pow(2).sum()),
        histogram=CentroidHistogram.from_values(
            series, max_length=histogram_bin_count or DEFAULT_HISTOGRAM_BIN_COUNT
        ),
    )
    return result


def aggregate_category_stats(series, distinct_category_count=None):
    # type: (pd.Series, Optional[int]) -> CategoricalAggregate
    """Aggregate a categorical feature into statistics"""
    value_count, missing_count = compute_counts(series)

    series = series[series.notnull()]
    series = series.astype(six.text_type)
    category_counts = (
        series.value_counts(ascending=False)
        .iloc[: distinct_category_count or DEFAULT_DISTINCT_CATEGORY_COUNT]
        .to_dict()
    )
    # Unlike the original function in feature_aggregations, this does not call safe_unicode.
    # I believe it's unnecessary in the library; it should be called downstream in modmon worker.

    result = CategoricalAggregate(
        count=value_count,
        missing_count=missing_count,
        text_word_count=None,
        category_counts=category_counts,
    )
    return result


# Compiled regular expressions for text tokenization
digit_pattern = re.compile(r"\d", flags=re.UNICODE)
word_pattern = re.compile(r"\b\w+\b", flags=re.UNICODE)
char_pattern = re.compile(r"\w", flags=re.UNICODE)


def aggregate_text_stats(series, feature_type, distinct_category_count):
    # type: (pd.Series, str, Optional[int]) -> CategoricalAggregate
    """Aggregate a text (words or characters) feature into statistics"""
    value_count, missing_count = compute_counts(series)

    # Remove numbers from the text (Port behavior of remove_numbers_from_text)
    series = series.fillna("").astype(six.text_type).str.replace(digit_pattern, "").str.lower()

    # Split each document into words or characters, depending on feature type
    # Original implementation is keyed off of language: If logographic, tokenize by characters.
    # Rather than passing in an extra map of languages, I chose to just split the feature type.
    pattern = word_pattern if feature_type == FeatureType.TEXT_WORDS else char_pattern
    series = series.str.findall(pattern)

    # Count unique words in each document (similar to CountVectorizer with binary=True)
    unigram_counter = Counter()  # type: TypedCounter[str]
    for unigrams in series:
        unigram_counter.update(set(unigrams))

    # Limit number of distinct words to distinct_category_count
    total_word_count = sum(unigram_counter.values())
    category_counts = dict(
        unigram_counter.most_common(distinct_category_count or DEFAULT_DISTINCT_CATEGORY_COUNT)
    )

    result = CategoricalAggregate(
        count=value_count,
        missing_count=missing_count,
        text_word_count=total_word_count,
        category_counts=category_counts,
    )
    return result


def aggregate_feature_stats(
    features,  # type: pd.DataFrame
    feature_types,  # type: Mapping[str, str]
    histogram_bin_count,  # type: Optional[int]
    distinct_category_count,  # type: Optional[int]
):
    # type: (...) -> Tuple[NumericFeatureStats, CategoricalFeatureStats]
    """Aggregate each feature with a specified feature type

    Columns in the `features` DataFrame that don't have matching keys in `feature_types` will
    not be aggregated. These features may be included for segment analysis, for instance.
    """
    numeric_stats, category_stats = {}, {}
    for name in feature_types:
        feature = features.loc[:, name]
        feature_type = feature_types[name]
        if feature_type == FeatureType.NUMERIC:
            numeric_stats[name] = aggregate_numeric_stats(feature, histogram_bin_count)
        elif feature_type == FeatureType.CATEGORY:
            category_stats[name] = aggregate_category_stats(feature, distinct_category_count)
        elif feature_type in (FeatureType.TEXT_WORDS, FeatureType.TEXT_CHARS):
            category_stats[name] = aggregate_text_stats(
                feature, feature_type, distinct_category_count
            )
    return numeric_stats, category_stats


def validate_counts(**kwargs):
    """Validate that each specified argument is either a positive int or None"""
    for name, value in kwargs.items():
        if value is not None and value <= 0:
            raise ValueError("If specified, {name} must be a positive integer".format(name=name))


def build_aggregated_stat_dict(numeric_stats, category_stats, prediction_stats, seg_stats=None):
    # type: (...) -> AggregatedStats
    aggregated_stats = {
        "numeric_stats": numeric_stats or {},
        "categorical_stats": category_stats or {},
        "prediction_stats": prediction_stats or [],
        "segment_stats": seg_stats or {},
    }  # type: AggregatedStats
    return aggregated_stats


def build_segment_stat_dict(aggregated_stats):
    # type: (...) -> FeatureAndPredictionStats
    segment_stats = {
        "numeric_stats": aggregated_stats["numeric_stats"] or {},
        "categorical_stats": aggregated_stats["categorical_stats"] or {},
        "prediction_stats": aggregated_stats["prediction_stats"] or [],
    }  # type: FeatureAndPredictionStats
    return segment_stats


def aggregate_stats(
    features=None,  # type: Optional[pd.DataFrame]
    feature_types=None,  # type: Optional[FeatureTypes]
    predictions=None,  # type: Optional[pd.DataFrame]
    segment_attributes=None,  # type: Optional[List[str]]
    histogram_bin_count=None,  # type: Optional[int]
    distinct_category_count=None,  # type: Optional[int]
    segment_value_per_attribute_count=None,  # type: Optional[int]
):
    # type: (...) -> AggregatedStats
    """
    Aggregates features and predictions into statistics for model monitoring.

    Parameters
    ----------
    features
        DataFrame of feature values (and segment values if those are not aggregated as features).
        Columns in this DataFrame that are not included in `feature_types` will not be aggregated.
    feature_types
        List of feature names, types and format. following this format
        [
          {
            "name": "f1"
            "featureType": "numeric"
          },
          {
            "name": "f2_date"
            "featureType": "date"
            "format": "MM-dd-yy"
          }
          ....
        ]
    predictions
        DataFrame of prediction values.
        - For regression models, the DataFrame will contain a single column for the prediction values.
        - For classification models, each column contains prediction probabilities for a particular class.
    segment_attributes
        Feature names that should be used to slice statistics by those feature values.
    histogram_bin_count
        Count of histogram bins to populate for each numeric feature. If unspecified, a configured default is used.
    distinct_category_count
        Count of distinct categories to count for each categorical feature. If unspecified, a configured default is used.
    segment_value_per_attribute_count
        Count of segment values tracked per segment attribute. If unspecified, a configured default is used.

    Returns
    -------
    Statistics about features and predictions, both overall and segmented by the specified attributes. For classification
    models, prediction statistics are ordered in the same order as columns in the input `predictions` DataFrame.
    """
    # Validate arguments
    if (
        features is not None
        and predictions is not None
        and features.shape[0] != predictions.shape[0]
    ):
        raise ValueError("Different numbers of rows for features and predictions specified")

    if predictions is not None and predictions.isna().values.any():
        raise ValueError("Missing values are not permitted in predictions")

    if segment_attributes is not None:
        if features is None:
            raise ValueError("Features must be specified when segment attributes are specified")
        elif set(segment_attributes).difference(features.columns):
            raise ValueError("All segment attributes must be specified in features")

    validate_counts(
        histogram_bin_count=histogram_bin_count,
        distinct_category_count=distinct_category_count,
        segment_value_per_attribute_count=segment_value_per_attribute_count,
    )

    # Aggregate features
    numeric_stats = None  # type: Optional[Dict[str, NumericAggregate]]
    category_stats = None  # type: Optional[Dict[str, CategoricalAggregate]]
    converted_types = None  # type: Optional[Mapping[str, str]]
    if features is not None and feature_types is not None:
        features, converted_types = convert_features_for_aggregation(features, feature_types)
        numeric_stats, category_stats = aggregate_feature_stats(
            features, converted_types, histogram_bin_count, distinct_category_count
        )

    # Aggregate predictions
    prediction_stats = None  # type: Optional[List[NumericAggregate]]
    if predictions is not None:
        prediction_stats = [
            aggregate_numeric_stats(predictions[col], histogram_bin_count) for col in predictions
        ]

    # Aggregate feature and prediction segments
    seg_stats = None  # type: Optional[Dict[str, Dict[str, FeatureAndPredictionStats]]]
    if segment_attributes and features is not None:
        seg_stats = defaultdict(dict)

        for seg_attribute in segment_attributes:
            # Reprocess the segment feature without limiting the number of categories to keep
            seg_feature = features[seg_attribute]
            seg_value_counts = Counter(
                aggregate_category_stats(seg_feature).category_counts
            )  # type: TypedCounter[str]
            seg_values = [
                value
                for value, _ in seg_value_counts.most_common(
                    segment_value_per_attribute_count or DEFAULT_DISTINCT_SEGMENT_VALUE_COUNT
                )
            ]

            for seg_value in seg_values:
                # Filter features and predictions to only those for the specified segment value
                seg_filter = seg_feature == seg_value
                seg_features = features[seg_filter]
                seg_predictions = predictions[seg_filter] if predictions is not None else None

                # Recursively aggregate features and predictions for the current segment value
                seg_value_stats = aggregate_stats(
                    seg_features,
                    feature_types,
                    seg_predictions,
                    histogram_bin_count=histogram_bin_count,
                    distinct_category_count=distinct_category_count,
                )
                seg_stats[seg_attribute][seg_value] = build_segment_stat_dict(seg_value_stats)

    return build_aggregated_stat_dict(numeric_stats, category_stats, prediction_stats, seg_stats)
