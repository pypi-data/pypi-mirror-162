"""A Metric is the output of a rule, and often the input to rules too.
Metrics can be stored in a Store, and can be retrieved by a MetricSource."""
import datetime
from uuid import uuid4

from sinai.types import JDict, MetricValue, SList


class Metric:
    """A measure to be observed."""

    name: str = "monitoring_metric"
    context: str = ""
    update: SList = []

    def __init__(
        self,
        value: MetricValue = None,
        name: str = "",
        ref: str = "",
        update: SList = [],
        checked: bool = False,
    ) -> None:
        if name:
            self.name = name
        if update:
            self.update = update
        self.annotations: SList = []
        self.monitor_id: str = ""
        self.ref = ref or str(uuid4())
        self.value = value
        self.checked = checked
        self.created_at = datetime.datetime.utcnow()
        self.updated_at = self.created_at

    def pre_save(self, monitor_id: str) -> JDict:
        """Readythe Metric for storage."""
        self.updated_at = datetime.datetime.utcnow()
        self.monitor_id = monitor_id
        return self.to_dict()

    def to_dict(self) -> JDict:
        """Serialise the Metric to a dictionary."""
        return {
            "name": self.name,
            "ref": self.ref,
            "value": self.value,
            "context": self.context,
            "annotations": self.annotations,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "monitor_id": self.monitor_id,
            "checked": self.checked,
        }

    @classmethod
    def from_dict(cls, metric_dict: JDict) -> "Metric":
        """Deserialise a dictionary back to a Metric."""
        metric = cls(
            name=metric_dict["name"],
            ref=metric_dict["ref"],
            value=metric_dict["value"],
            checked=metric_dict["checked"],
        )
        metric.context = metric_dict["context"]
        metric.created_at = metric_dict["created_at"]
        metric.updated_at = metric_dict["updated_at"]
        metric.annotations = metric_dict["annotations"]
        metric.monitor_id = metric_dict["monitor_id"]
        return metric

    def annotate(self, text: str) -> None:
        """Store a piece of text in the Metric."""
        self.annotations.append(text)

    def format_message(self):
        """Format the metric into text."""
        message = ""
        if self.context:
            message += f"{self.context}: "
        message += f"{self.name}\n"
        message += f"{self.__doc__}\n"
        if self.ref:
            message += f"Ref: {self.ref}\n"
        if self.value:
            message += f"Value: {self.value}"
        message += f"First Seen: {self._prettify_created_at()}"
        if self.checked:
            message += "Checked\n"
        if self.annotations:
            message += "Notes:\n"
            for note in self.annotations:
                message += note + "\n"
        return message

    def _prettify_created_at(self) -> str:
        formatted_date = self.created_at.strftime("%Y-%m-%d")
        if self.created_at.date() == datetime.date.today():
            return f"{formatted_date} - NEW TODAY!"
        else:
            return f"{formatted_date} - {(self.created_at - datetime.datetime.utcnow()).days} days ago"


class Sinner(Metric):
    """An unexpected or missing item between two sequences."""

    ...
