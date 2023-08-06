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
from __future__ import division
from __future__ import unicode_literals

import itertools
from typing import List
from typing import Optional
from typing import Union
from typing import cast

import six
from drfaster import centroid_histogram as ch


class CentroidBucket(object):

    # this lines saves about 70% of memory compared to regular class
    __slots__ = ("centroid", "count")

    def __init__(self, centroid, count=0):
        assert isinstance(centroid, (int, float))
        assert isinstance(count, int)

        self.centroid = float(centroid)
        self.count = count

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.centroid == other.centroid and self.count == other.count
        else:
            return False

    def __hash__(self):
        return hash((self.centroid, self.count))

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        v = six.text_type(tuple([self.centroid, self.count]))
        return "<CentroidBucket {}>".format(v)


class CentroidHistogram(object):

    __slots__ = ("buckets", "_max_length")

    def __init__(self, buckets, max_length=None):
        # type: (List[Union[CentroidBucket, tuple, list]], Optional[int]) -> None
        assert all(isinstance(bucket, (CentroidBucket, tuple, list)) for bucket in buckets)
        max_length = CentroidHistogram._sanitize_max_length(max_length)

        # Convert tuples to CentroidBucket instances
        for index in range(len(buckets)):
            bucket = buckets[index]
            if isinstance(bucket, (tuple, list)):
                bucket = CentroidBucket(bucket[0], bucket[1])
                buckets[index] = bucket

        self.buckets = cast(List[CentroidBucket], buckets)
        self._max_length = max_length  # type: int

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.buckets == other.buckets
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(tuple(self.buckets))

    def __repr__(self):
        centroids = six.text_type([(b.centroid, b.count) for b in self.buckets])
        return "<CentroidHistogram {}>".format(centroids)

    def __iter__(self):
        return self.buckets.__iter__()

    def __len__(self):
        return self.buckets.__len__()

    @property
    def max_length(self):
        return self._max_length

    @property
    def total_count(self):
        return sum(b.count for b in self.buckets)

    @staticmethod
    def _sanitize_max_length(max_length):
        # type: (Optional[int]) -> int
        default_max_length = 1000

        assert max_length is None or (isinstance(max_length, int) and max_length > 0)
        return max_length or default_max_length

    @classmethod
    def from_values(cls, values, max_length=None):
        """Return a CentroidHistogram built from valid values (i.e. not None's and not NaN's)."""

        max_length = cls._sanitize_max_length(max_length)
        # delegate creation of the histogram to the code from drfaster (implemented in C++).
        # It will also filter out None's and NaN's
        return cls(ch.histogram_from_values(max_length, values).buckets, max_length)

    @staticmethod
    def merge(*histograms):
        """
        Merge centroid histograms into one histogram

        This function mirrors the bh_tt_combine aggregate function used internally.
        Multiple Ben-Haim/Tom-Tov histograms should be combined client-side before sending
        them to the database, to minimize network traffic. When reading histograms from the database
        though, the internal function should be used to combine them there, rather than reading
        them all into Python and combining them.

        Parameters
        ----------
        histograms: (each) CentroidHistogram
            Histograms that will be combined into the destination
        """

        # delegate creation of the new histogram to the code from drfaster (implemented in C++).
        # histogram_from_buckets() expects (centroid, count) tuples as its input, and does not
        # currently handle zero counts, so we need to filter them out
        buckets = (
            (b.centroid, b.count)
            for b in itertools.chain(*[histogram.buckets for histogram in histograms])
            if b.count
        )
        max_length = histograms[0]._max_length
        new_buckets = ch.histogram_from_buckets(max_length, buckets).buckets

        buckets = [CentroidBucket(b.centroid, b.count) for b in new_buckets]
        return CentroidHistogram(buckets, max_length=max_length)

    def combine(self, *histograms):
        """
        Combines other centroid histograms into this histogram

        This function mirrors the bh_tt_combine aggregate function defined internally.
        Multiple Ben-Haim/Tom-Tov histograms should be combined client-side before sending
        them to the database, to minimize network traffic. When reading histograms from the database
        though, the internal function should be used to combine them there, rather than reading
        them all into Python and combining them.

        Parameters
        ----------
        histograms: (each) CentroidHistogram
            Histograms that will be combined into the destination
        """
        merged_histogram = self.merge(self, *histograms)
        self.buckets = merged_histogram.buckets
        return self

    def round(self, ndigits=0):
        """
        Round each centroid to the specified number of digits using the round() function.

        :param ndigits: Number of decimal digits to round each centroid to.
        :return: The histogram
        """
        for bucket in self.buckets:
            bucket.centroid = round(bucket.centroid, ndigits)

        return self
