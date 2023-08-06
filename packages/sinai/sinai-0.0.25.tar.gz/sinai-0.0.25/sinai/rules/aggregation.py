from __future__ import annotations

from sinai.metrics import AGGREGATION_CLASSES
from sinai.rules.base import Rule
from sinai.types import (
    AggregationMetrics,
    Evaluation,
    JDict,
    MetricClasses,
    MetricList,
    MetricSourceClass,
    MetricSourceClasses,
    MetricSourceInstance,
    SList,
)


class MetricAggregationRule(Rule):
    """A rule that aggregates stored metrics and produces a metric."""

    sources: MetricSourceClasses = []
    update: SList = []
    count: MetricClasses = []
    sum: MetricClasses = []
    max: MetricClasses = []
    min: MetricClasses = []
    mean: MetricClasses = []
    mode: MetricClasses = []
    median: MetricClasses = []
    last_only = False
    exclude_checked = False

    def evaluate(self) -> Evaluation:
        self.metrics: AggregationMetrics = []
        for agg in AGGREGATION_CLASSES:
            met_cls = getattr(self, agg)
            if met_cls:
                base_name = "+".join([cls.name for cls in met_cls])
                self._process_agg(agg, base_name)
        return self.metrics

    def _process_agg(self, aggregation_name: str, base_name: str) -> None:
        metric_instances = []
        for source_cls in self.sources:
            metric_instances.extend(
                self._get_metric_instances(source_cls, aggregation_name)
            )
        data_points = [metric.value for metric in metric_instances]
        metric_cls = AGGREGATION_CLASSES[aggregation_name]
        metric = metric_cls(name=f"{base_name}:{metric_cls.name}", update=self.update)
        metric.process_data_points(data_points)
        self.metrics.append(metric)

    def _get_metric_instances(
        self, source_cls: MetricSourceClass, aggregation_name: str
    ) -> MetricList:
        metric_instances = []
        source: MetricSourceInstance = self.monitor.source(source_cls)  # type: ignore
        for target_class in getattr(self, aggregation_name):
            filter: JDict = {"name": target_class.name}
            if self.last_only:
                filter["monitor_id"] = self.monitor.id
            if self.exclude_checked:
                filter["checked"] = False
            instances = source.get(**filter)
            metric_instances.extend(instances)
        return metric_instances
