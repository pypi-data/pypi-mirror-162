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

import functools
import re
from typing import TYPE_CHECKING
from typing import cast

# We're already importing centroid_histogram from drfaster, so we may as well also get date2int
import drfaster.dateToInt.date_to_int_wrapper as d2iw
import numpy as np
import pandas as pd
import six
from datarobot.mlops.stats_aggregator.types import FeatureType

if TYPE_CHECKING:
    from typing import Dict
    from typing import Mapping
    from typing import Optional
    from typing import Tuple
    from typing import Union

    from .types import FeatureTypes


def date2int(x, fmt, skip_tz=False):
    """
    Convert a date string into its integer (ordinal) representation.
    Return np.nan if value can't be converted.

    Based on common.utilities.metadata.date2int, but without fancy error handling.
    """
    if x == "" or x is None or pd.isnull(x) or x == "nan":
        return np.nan

    if isinstance(x, (float, np.float, np.float32, np.float64)):
        if float.is_integer(x):
            x = int(x)
    try:
        return d2iw.date2intWrapper(six.text_type(x), fmt.encode("utf-8"), skip_tz=skip_tz)

    except (ValueError, TypeError):
        # Unlike common.utilities.metadata.date2int, always return np.nan if a value won't convert
        return np.nan


def convert_date_feature(feature, feature_format):
    # type: (pd.Series, str) -> pd.Series
    """Convert a series of dates into a series of integers (i.e. ordinal representations of dates)

    Based on common.utilities.metadata.dateParser, but without format detection, since this code
    is for converting rather than detecting data types.
    """

    if "%M" in feature_format:
        # if there's no timezone info, skip the timezone check for the series
        skip_tz = False
        first_valid = next(
            (x for x in feature if x != "" and x is not None and pd.notna(x) and x != "nan"),
            None,
        )
        if first_valid is None:
            # no valid dates found
            return pd.Series(np.nan, index=feature.index)
        if not re.search(r"[\+-][0-9]+$", six.text_type(first_valid)):
            skip_tz = True
        return feature.map(lambda x: date2int(x, feature_format, skip_tz), na_action="ignore")
    else:
        # use faster date2int for series without time components
        uniques = feature.dropna().unique()

        # there's no timezone information in ordinal dates
        replace = [date2int(val, feature_format, True) for val in uniques]
        replace_series = pd.Series(replace, index=uniques)

        ret = feature.map(replace_series)
        try:
            return ret.astype(int, copy=False)
        except (ValueError, TypeError):
            return ret.astype(float, copy=False)


def float_or_nan(value):
    """Convert a value to a float, returning NaN if the value cannot be converted"""
    try:
        return float(value)
    except (ValueError, OverflowError):
        return np.nan


def convert_pct(value):
    """Convert a percentage value (with or without the % symbol) into a float

    Based on ModelingMachine.engine.pandas_data_utils.convert_pct, but without Py2/Py3 float
    conversion logic, since this code is for converting rather than detecting data types.
    """
    try:
        value = value.replace("%", "")
    except AttributeError:
        pass

    return float_or_nan(value)


def convert_length(value):
    """Convert a length value (with ' and/or " denoting feet and/or inches) into a float

    Based on ModelingMachine.engine.pandas_data_utils.convert_length, but without Py2/Py3 float
    conversion logic, since this code is for converting rather than detecting data types.

    (JMB) For what it's worth, I don't like this logic. Passing "6'2" returns 744.0, which is
    obviously incorrect. However, this is the logic that the rest of DataRobot uses for length
    conversion, so I don't believe we should deviate from it.
    """
    try:
        if '"' in value and "'" in value:
            split_value = value.split("'")
            return float_or_nan(split_value[0]) * 12 + float_or_nan(split_value[1].replace('"', ""))
        else:
            if "'" in value:
                return float_or_nan(value.replace("'", "")) * 12
            else:
                return float_or_nan(value.replace('"', ""))
    except (TypeError, AttributeError):
        return float_or_nan(value)


def convert_percentage_feature(feature, _):
    # type: (pd.Series, str) -> pd.Series
    return cast(
        pd.Series,
        feature.astype(np.float64)
        if np.issubdtype(feature.dtype, np.number)
        else feature.apply(convert_pct),
    )


def convert_length_feature(feature, _):
    # type: (pd.Series, str) -> pd.Series
    return cast(
        pd.Series,
        feature.astype(np.float64)
        if np.issubdtype(feature.dtype, np.number)
        else feature.apply(convert_length),
    )


def convert_currency_feature(feature, feature_format):
    # type: (pd.Series, str) -> pd.Series
    """Convert a series of currency values into a series of float values

    Based on ModelingMachine.engine.pandas_data_utils.currencyParser, but without Py2/Py3 float
    conversion logic, since this code is for converting rather than detecting data types.
    """
    _, currency_symbol, cents_separator = feature_format.split("__")

    def _clean_spaces_symbol(val):
        val = val.replace(currency_symbol, "", 1)
        val = val.replace(" ", "")
        return val

    def _replace_cents_period(val):
        return val.replace(",", "")

    def _replace_cents_comma(val):
        val = val.replace(".", "")
        val = val.replace(",", ".")
        return val

    def _replace_no_cents(val):
        val = val.replace(",", "")
        val = val.replace(".", "")
        return val

    def _currency_val_to_float(val, replace_fn=None):
        try:
            if np.isnan(val):
                return val
        except TypeError:
            pass
        try:
            val = _clean_spaces_symbol(val)
            val = replace_fn(val)
            val = float_or_nan(val)
        except ValueError:
            val = np.nan
        return val

    if not cents_separator:
        fn = _replace_no_cents
    elif cents_separator == ",":
        fn = _replace_cents_comma
    else:
        fn = _replace_cents_period

    converter = functools.partial(_currency_val_to_float, replace_fn=fn)
    return cast(pd.Series, feature.apply(converter))


# Transformers loosely mimic the functionality of common.utilities.data_prep.convert_column
feature_type_converters = {
    FeatureType.DATE: convert_date_feature,
    FeatureType.PERCENTAGE: convert_percentage_feature,
    FeatureType.LENGTH: convert_length_feature,
    FeatureType.CURRENCY: convert_currency_feature,
}


def convert_features_for_aggregation(features, feature_types):
    # type: (pd.DataFrame, FeatureTypes) -> Tuple[pd.DataFrame, Mapping[str, str]]
    """
    Prepare features for aggregation by converting "numeric-adjacent" features into true numerics.

    The returned `feature_types` dictionary will contain every feature and values will be constrained
    to NUMERIC, CATEGORY, TEXT_WORDS, or TEXT_CHARS types. The returned `features` dictionary will
    have values converted into these types as necessary.
    """
    # Prevent modification of the original arguments
    # (Copy features that don't have specified types i.e. for segment analysis)
    converted_features = pd.DataFrame(
        {name: features[name] for name in features if name not in feature_types}
    )
    converted_feature_types = {}  # type: Dict[str, str]

    for feature_desc in feature_types:
        name = feature_desc.name
        feature_type = feature_desc.feature_type
        feature_format = feature_desc.format

        # Verify that feature types that require formats have them specified
        if feature_type in [FeatureType.DATE, FeatureType.CURRENCY] and not feature_format:
            raise ValueError(
                "Feature type {feature_type} requires a format to be specified".format(
                    feature_type=feature_type
                )
            )

        feature = features[name]
        feature_converter = feature_type_converters.get(feature_type)
        if feature_converter:
            # Transform the feature into a numeric value
            converted_features[name] = feature_converter(feature, feature_format or "")
            converted_feature_types[name] = FeatureType.NUMERIC
        else:
            # Don't convert the feature and don't change its type
            converted_features[name] = feature
            converted_feature_types[name] = feature_type

    return converted_features, converted_feature_types
