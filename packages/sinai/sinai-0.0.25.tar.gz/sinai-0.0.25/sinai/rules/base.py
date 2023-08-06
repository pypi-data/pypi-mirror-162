"""A Rule takes data from sources, makes metrics and puts them into stores."""
from __future__ import annotations

from sinai.types import Evaluation, MonitorInstance, SourceClasses, StoreClasses


class Rule:
    """The sources and stores are defined in the rule, instantiated by the monitor."""

    sources: SourceClasses = []
    stores: StoreClasses = []

    def __init__(self, monitor: MonitorInstance):
        self.monitor = monitor

    def evaluate(self) -> Evaluation:
        """The evalutation function is called by the monitor, which stores any returned metrics."""
        return None
