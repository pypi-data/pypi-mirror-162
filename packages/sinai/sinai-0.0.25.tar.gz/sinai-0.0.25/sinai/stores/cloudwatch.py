"""
Publishes sinai metrics as metric data points in Amazon CloudWatch.

For more information:

https://boto3.amazonaws.com/v1/documentation/api/latest/reference/
services/cloudwatch.html#CloudWatch.Client.put_metric_data
"""

try:
    import boto3
except ImportError:
    HAS_BOTO = False
else:
    HAS_BOTO = True

from sinai.exceptions import DependencyMissing
from sinai.stores.base import Store
from sinai.types import MetricInstance, MonitorInstance


class CloudWatch(Store):
    namespace = "metrics"
    dimension = "context"

    def __init__(self, monitor: MonitorInstance):
        super().__init__(monitor)
        if not HAS_BOTO:
            raise DependencyMissing(
                "Sorry, boto3 library required to store metrics in Cloudwatch."
            )

    def save_metric(self, metric: MetricInstance) -> None:
        client = boto3.client("cloudwatch")
        client.put_metric_data(
            Namespace=self.namespace,
            MetricData=[
                {
                    "MetricName": metric.name,
                    "Value": metric.value,
                    "Unit": "Count",
                    "Dimensions": [{"Name": self.dimension, "Value": metric.context}],
                }
            ],
        )
        return super().save_metric(metric)
