"""A Store is any output channel from a rule."""
from sinai import BaseView
from sinai.exceptions import MetricNotFound
from sinai.types import JDict, MetricId, MetricInstance, MetricResult


class Store(BaseView):
    """A class for storing data.
    This is a base class, it doesn't do much."""

    ...

    def save_metric(self, metric: MetricInstance) -> None:
        """Save a metric instance into the store.
        If this is not a metric store then don't implement this method.
        """
        ...


class MetricStore(Store):
    """A class for storing metrics.
    This is a base class, for reference, it doesn't do much either."""

    def save_metric(self, metric: MetricInstance) -> None:
        """Save a metric instance into the store."""
        if metric.update:
            self._upsert(metric)
        else:
            self._save(metric)

    def _upsert(self, metric: MetricInstance) -> None:
        try:
            existing, metric_id = self._get_metric_for_update(metric)
        except MetricNotFound:
            self._save(metric)
        else:
            self._replace(existing, metric_id)

    def _get_metric_for_update(self, metric: MetricInstance) -> MetricResult:
        metric_filter: JDict = {}
        for field in metric.update:
            metric_filter[field] = getattr(metric, field)
        return self._find_metric_by_filter(metric, metric_filter)

    def _save(self, metric: MetricInstance) -> None:
        ...

    def _find_metric_by_filter(
        self, metric: MetricInstance, metric_filter: JDict
    ) -> MetricResult:
        ...

    def _replace(self, metric: MetricInstance, metric_id: MetricId) -> None:
        ...
