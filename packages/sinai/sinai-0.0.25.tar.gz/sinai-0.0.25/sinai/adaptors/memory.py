"""In Memory Store."""

from sinai.metrics import Metric
from sinai.types import GlobalMemory, JDict, MetricDict


class Memory:
    """A simple global memory dict.
    For persistence, use a database instead.
    """

    memory: GlobalMemory = {}

    def find_metric(self, metric_filter: JDict) -> MetricDict:
        """Find a dictionary in the in-memory store."""
        results = {}
        for metric_id, metric_dict in self.memory.items():
            for filter_key in metric_filter:
                if metric_dict[filter_key] != metric_filter[filter_key]:
                    continue
                metric = Metric.from_dict(metric_dict)
                results[metric_id] = metric
        return results

    def clear(self) -> None:
        self.memory = {}
