"""Simple Slack Store using Webhooks
For setup see: https://api.slack.com/messaging/webhooks
"""

from sinai.stores.api import ApiStore
from sinai.stores.base import MetricStore
from sinai.types import MetricInstance


class Slack(ApiStore, MetricStore):
    # An example, set your own.
    url = (
        "https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXXXXXX"
    )

    def save_metric(self, metric: MetricInstance) -> None:
        self.post({"message": metric.format_message()})
