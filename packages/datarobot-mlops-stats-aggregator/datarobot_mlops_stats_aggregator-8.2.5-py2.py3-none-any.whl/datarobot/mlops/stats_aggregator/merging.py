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

from collections import Counter
from collections import defaultdict
from typing import TYPE_CHECKING
from typing import Tuple

from .aggregation import build_aggregated_stat_dict
from .aggregation import build_segment_stat_dict
from .constants import DEFAULT_DISTINCT_CATEGORY_COUNT
from .constants import DEFAULT_HISTOGRAM_BIN_COUNT
from .types import CategoricalAggregate
from .types import CentroidHistogram
from .types import NumericAggregate

if TYPE_CHECKING:
    from typing import Dict
    from typing import Iterable
    from typing import List
    from typing import Optional
    from typing import TypeVar
    from typing import Union

    from .types import AggregatedStats
    from .types import CategoricalFeatureStats
    from .types import NumericFeatureStats
    from .types import PredictionStats
    from .types import SegmentStats

    TKey = TypeVar("TKey")


# Create maps of functions used to accumulate statistics
def preserve_none(accumulate, default):
    """Accumulate values but preserve None values if both arguments are None"""

    def _preserve_none(x, y):
        if x is None and y is None:
            return None
        if x is None:
            x = default
        if y is None:
            y = default
        return accumulate(x, y)

    return _preserve_none


def update_and_return(x, y):
    # type: (Dict, Dict) -> Dict
    """Update dict x with dict y and return dict x"""
    x.update(y)
    return x


def add(x, y):
    """Adds two numbers (or really anything that can be added) together"""
    return x + y


numeric_accumulators = {
    "count": add,
    "missing_count": add,
    "min": preserve_none(min, float("+inf")),
    "max": preserve_none(max, float("-inf")),
    "sum": add,
    "sum_of_squares": add,
    "histogram": CentroidHistogram.merge,
}

category_accumulators = {
    "count": add,
    "missing_count": add,
    "text_word_count": preserve_none(add, 0),
    "category_counts": update_and_return,
}


def merge_numeric_feature_stats(numeric_feature_stats, histogram_bin_count):
    # type: (Iterable[Optional[Dict[TKey, NumericAggregate]]], Optional[int]) -> Optional[Dict[TKey, NumericAggregate]]
    """Merge numeric feature stats by accumulating stats for each feature"""
    if not any(numeric_feature_stats):
        return None

    # Map of feature name -> accumulated stats
    total_stats = defaultdict(
        lambda: dict(
            count=0,
            missing_count=0,
            min=None,
            max=None,
            sum=0.0,
            sum_of_squares=0.0,
            histogram=CentroidHistogram.from_values(
                [], max_length=histogram_bin_count or DEFAULT_HISTOGRAM_BIN_COUNT
            ),
        )
    )  # type: Dict[TKey, Dict[str, Union[int, float, CentroidHistogram, None]]]

    for feature_stats_item in numeric_feature_stats:
        if feature_stats_item:
            for feature, feature_stats in feature_stats_item.items():
                total_feature_stats = total_stats[feature]
                for stat, accumulate in numeric_accumulators.items():
                    # e.g. total_feature_stats['count'] = add(total_feature_stats['count'], feature_stats.count)
                    total_feature_stats[stat] = accumulate(
                        total_feature_stats[stat], getattr(feature_stats, stat)
                    )

    return {
        # Convert working dicts into NumericAggregate objects
        feature: NumericAggregate(**total_feature_stats)  # type: ignore
        for feature, total_feature_stats in total_stats.items()
    }


def merge_categorical_feature_stats(categorical_feature_stats, distinct_category_count):
    # type: (Iterable[Optional[CategoricalFeatureStats]], Optional[int]) -> Optional[CategoricalFeatureStats]
    """Merge categorical/text feature stats by accumulating stats for each feature"""
    if not any(categorical_feature_stats):
        return None

    # Map of feature name -> accumulated stats
    total_stats = defaultdict(
        lambda: dict(count=0, missing_count=0, text_word_count=None, category_counts=Counter())
    )  # type: Dict[str, Dict[str, Union[int, Dict, None]]]

    for feature_stats_item in categorical_feature_stats:
        if feature_stats_item:
            for feature, feature_stats in feature_stats_item.items():
                total_feature_stats = total_stats[feature]
                for stat, accumulate in category_accumulators.items():
                    # e.g. total_feature_stats['count'] = add(total_feature_stats['count'], feature_stats.count)
                    total_feature_stats[stat] = accumulate(
                        total_feature_stats[stat], getattr(feature_stats, stat)
                    )

    # Limit number of distinct categories/words to distinct_category_count
    return_value = {}
    for feature, total_feature_stats in total_stats.items():
        total_feature_stats["category_counts"] = dict(
            total_feature_stats["category_counts"].most_common(distinct_category_count or DEFAULT_DISTINCT_CATEGORY_COUNT)  # type: ignore
        )
        # Convert working dicts into CategoricalAggregate objects
        return_value[feature] = CategoricalAggregate(**total_feature_stats)  # type: ignore

    return return_value


def merge_prediction_stats(prediction_stats, histogram_bin_count):
    # type: (Iterable[Optional[PredictionStats]], Optional[int]) -> Optional[PredictionStats]
    """Merge prediction stats by accumulating stats for the series (regression) or each class"""
    if not any(prediction_stats):
        return None

    # Convert each list of prediction stats into a dictionary, keyed by index
    prediction_stats_dicts = [dict(enumerate(ps)) for ps in prediction_stats if ps]

    # Use numeric feature stats merging to merge the prediction stats
    merged_stats_dict = merge_numeric_feature_stats(prediction_stats_dicts, histogram_bin_count)

    # Convert the dict back into a list
    return_value = [v for _, v in sorted((merged_stats_dict or {}).items())]
    return return_value


def merge_feature_and_prediction_stats(
    input_numeric_feature_stats,
    input_categorical_feature_stats,
    input_prediction_stats,
    histogram_bin_count,
    distinct_category_count,
):
    # type: (...) -> Tuple[Optional[NumericFeatureStats], Optional[CategoricalFeatureStats], Optional[PredictionStats]]
    """Reorganize input feature/predictions stats into lists of numeric features, categorical
    features, and predictions, and then merge each specific type of data separately.
    """
    numeric_feature_stats = None  # type: Optional[NumericFeatureStats]
    categorical_feature_stats = None  # type: Optional[CategoricalFeatureStats]
    prediction_stats = None  # type: Optional[PredictionStats]

    # Merge numeric, categorical, and prediction stats separately
    if input_numeric_feature_stats:
        numeric_feature_stats = merge_numeric_feature_stats(
            input_numeric_feature_stats, histogram_bin_count
        )
    if input_categorical_feature_stats:
        categorical_feature_stats = merge_categorical_feature_stats(
            input_categorical_feature_stats, distinct_category_count
        )
    if input_prediction_stats:
        prediction_stats = merge_prediction_stats(input_prediction_stats, histogram_bin_count)

    return numeric_feature_stats, categorical_feature_stats, prediction_stats


def merge_segment_stats(segment_stats, histogram_bin_count, distinct_category_count):
    # type: (...) -> Optional[SegmentStats]
    """Merge stats per segment attribute and value"""
    if not any(segment_stats):
        return None

    # Transform List[Dict[str, Dict[str, Stats]]] into Dict[str, Dict[str, List[Stats]]]
    seg_stats_lists = defaultdict(
        lambda: defaultdict(list)
    )  # type: Dict[str, Dict[str, List[AggregatedStats]]]

    for seg_stats_item in segment_stats:
        if seg_stats_item:
            for seg_attribute, seg_stats_by_value in seg_stats_item.items():
                for seg_value, seg_stats in seg_stats_by_value.items():
                    # Create a tuple with the segment stats as the "main" stats
                    seg_stats_lists[seg_attribute][seg_value].append(
                        build_aggregated_stat_dict(
                            numeric_stats=seg_stats["numeric_stats"],
                            category_stats=seg_stats["categorical_stats"],
                            prediction_stats=seg_stats["prediction_stats"],
                        )
                    )

    # Merge each feature and prediction segment
    return_value = defaultdict(dict)  # type: SegmentStats
    for seg_attribute, seg_stats_lists_by_value in seg_stats_lists.items():
        for seg_value, seg_stats_list in seg_stats_lists_by_value.items():
            # Recursively merge features and predictions for each segment attribute/value
            seg_value_stats = merge_stats(
                seg_stats_list, histogram_bin_count, distinct_category_count
            )
            return_value[seg_attribute][seg_value] = build_segment_stat_dict(seg_value_stats)

    return return_value


def merge_stats(
    aggregated_stats,
    histogram_bin_count=None,
    distinct_category_count=None,
):
    # type: (Iterable[AggregatedStats], Optional[int], Optional[int]) -> AggregatedStats
    """
    Merges multiple outputs of `aggregate_stats` into a single instance of stats.

    Parameters
    ----------
    aggregated_stats
        Multiple outputs of `aggregate_stats` to merge into a single output.
    histogram_bin_count
        Count of histogram bins to populate for each numeric feature. If unspecified, a configured default is used.
    distinct_category_count
        Count of distinct categories to count for each categorical feature. If unspecified, a configured default is used.

    Returns
    -------
    Single instance of aggregated statistics.
    """
    _ = histogram_bin_count, distinct_category_count

    numeric_stats = None  # type: Optional[NumericFeatureStats]
    category_stats = None  # type: Optional[CategoricalFeatureStats]
    prediction_stats = None  # type: Optional[PredictionStats]
    segment_stats = None  # type: Optional[SegmentStats]

    if aggregated_stats:
        input_numeric_feature_stats = []
        input_categorical_feature_stats = []
        input_prediction_stats = []
        input_segment_stats = []

        for stats in aggregated_stats:
            if 'numeric_stats' in stats:
                input_numeric_feature_stats.append(stats['numeric_stats'])
            if 'categorical_stats' in stats:
                input_categorical_feature_stats.append(stats['categorical_stats'])
            if 'prediction_stats' in stats:
                input_prediction_stats.append(stats['prediction_stats'])
            if 'segment_stats' in stats:
                input_segment_stats.append(stats['segment_stats'])

        numeric_stats, category_stats, prediction_stats = merge_feature_and_prediction_stats(
            input_numeric_feature_stats,
            input_categorical_feature_stats,
            input_prediction_stats,
            histogram_bin_count,
            distinct_category_count,
        )
        segment_stats = merge_segment_stats(
            input_segment_stats, histogram_bin_count, distinct_category_count
        )

    return build_aggregated_stat_dict(
        numeric_stats, category_stats, prediction_stats, segment_stats
    )
