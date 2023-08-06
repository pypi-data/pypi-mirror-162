"""Metric Store using MongoDB."""

from sinai.adaptors import Mongo
from sinai.exceptions import MetricNotFound
from sinai.metrics import Metric
from sinai.stores import MetricStore
from sinai.types import JDict, MetricId, MetricInstance, MetricResult


class MongoMetricStore(Mongo, MetricStore):
    """Metric store using MongoDB. Don't forget to set `database_name` and `connection_string`."""

    def _save(self, metric: MetricInstance) -> None:
        self.collection.insert_one(metric.pre_save(self.monitor.id))

    def _find_metric_by_filter(
        self, metric: MetricInstance, metric_filter: JDict
    ) -> MetricResult:
        if result := self.collection.find_one(metric_filter):
            mongo_id = result.pop("_id")
            existing_metric = Metric.from_dict(result)
            metric.created_at = existing_metric.created_at
            metric.checked = existing_metric.checked
            return metric, mongo_id
        raise MetricNotFound(f"Metric with fields: {metric_filter} not found.")

    def _replace(self, metric: MetricInstance, metric_id: MetricId) -> None:
        self.collection.replace_one(
            {"_id": metric_id}, metric.pre_save(self.monitor.id)
        )
