from uuid import uuid4

from sinai.adaptors import Memory
from sinai.exceptions import MetricNotFound
from sinai.stores import MetricStore
from sinai.types import JDict, MetricId, MetricInstance, MetricResult


class MemoryMetricStore(MetricStore, Memory):
    """Basic in memory metric store.
    Use a database-backed store to get persistence."""

    def _save(self, metric: MetricInstance) -> None:
        self.memory[uuid4()] = metric.pre_save(self.monitor.id)

    def _replace(self, metric: MetricInstance, metric_id: MetricId) -> None:
        self.memory[metric_id] = metric.pre_save(self.monitor.id)

    def _find_metric_by_filter(
        self, metric: MetricInstance, metric_filter: JDict
    ) -> MetricResult:
        if results := self.find_metric(metric_filter):
            for metric_id, existing_metric in results.items():
                metric.created_at = existing_metric.created_at
                metric.checked = existing_metric.checked
                # This could support updating multiple metrics, for now support only the first
                return metric, metric_id
        raise MetricNotFound(f"Metric with fields: {metric_filter} not found.")
