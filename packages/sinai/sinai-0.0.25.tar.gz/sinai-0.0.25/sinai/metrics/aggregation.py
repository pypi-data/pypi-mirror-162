from statistics import mean, median, mode

from sinai.metrics.base import Metric
from sinai.types import AggregationFunction, MetricValueList


class AggregationMetric(Metric):
    """A metric formed from summarizing a query of stored metrics."""

    name = "aggregation"
    aggregation: AggregationFunction = len

    def process_data_points(self, data_points: MetricValueList) -> None:
        """Turn multiple values into one."""
        self.value = self.aggregation(data_points)  # type:ignore


class CountMetric(AggregationMetric):
    """The total number of matching metrics."""

    name = "count"
    aggregation = len


class SumMetric(AggregationMetric):
    """The total values of matching metric."""

    name = "sum"
    aggregation = sum  # type:ignore


class MeanMetric(AggregationMetric):
    """The average of matching metric values."""

    name = "mean"
    aggregation = mean


class MaxMetric(AggregationMetric):
    """The maximum of the matching metric values."""

    name = "max"
    aggregation = max  # type:ignore


class MinMetric(AggregationMetric):
    """The minimum of the matching metric values."""

    name = "min"
    aggregation = min  # type:ignore


class MedianMetric(AggregationMetric):
    """The median of the matching metric values."""

    name = "median"
    aggregation = median


class ModeMetric(AggregationMetric):
    """The mode of the matching metric values."""

    name = "mode"
    aggregation = mode


AGGREGATION_CLASSES = {
    "count": CountMetric,
    "sum": SumMetric,
    "mean": MeanMetric,
    "max": MaxMetric,
    "min": MinMetric,
    "median": MedianMetric,
    "mode": ModeMetric,
}
