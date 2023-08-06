"""A `Source` provides the input data to the Rule."""

from typing import Any

from sinai import BaseView
from sinai.adaptors import Memory
from sinai.types import JDict, MetricList, NullableBool


class Source(BaseView):
    """Any data source (base class)."""

    def get_data(self, request: JDict) -> Any:
        """Some sources can get their data at initialisation,
        others need to wait for the Rule to request it.
        This method is for that latter case.
        """


class MetricSource(Source, Memory):
    """In memory source of Metrics, use an adaptor instead when you need persistence."""

    def get(
        self,
        name: str = "",
        ref: str = "",
        value: str = "",
        checked: NullableBool = None,
        context: str = "",
        monitor_id: str = "",
    ) -> MetricList:
        """Get a metric/metrics from the Source"""
        metric_filter: JDict = {}
        if name:
            metric_filter["name"] = name
        if ref:
            metric_filter["ref"] = ref
        if value:
            metric_filter["value"] = value
        if context:
            metric_filter["context"] = context
        if checked is not None:
            metric_filter["checked"] = checked
        if monitor_id:
            metric_filter["monitor_id"] = monitor_id
        return self._execute_query(metric_filter)

    def _execute_query(self, metric_filter: JDict) -> MetricList:
        results = self.find_metric(metric_filter)
        return list(results.values())
