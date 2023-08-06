"""
The Monitor connects to sources, evaluates rules, sends the resulting metrics to the stores.
"""
from collections.abc import Iterable
from uuid import uuid4

from sinai.exceptions import SourceNotFound
from sinai.metrics import Metric
from sinai.rules import Rule
from sinai.types import (
    Evaluation,
    RuleClass,
    RuleClasses,
    SourceClass,
    SourceClassList,
    SourceDict,
    SourceInstance,
    StoreClass,
    StoreClassList,
    StoreDict,
)


class Monitor:
    """The monitor controls the monitoring run."""

    rules: RuleClasses = []
    context: str = "global"

    def __init__(self) -> None:
        self.id = str(uuid4())
        self.sources: SourceClassList = []
        self.stores: StoreClassList = []
        self._store_instances: StoreDict = {}
        self._source_instances: SourceDict = {}
        self._resolve_rules()

    def _add_source(self, source_cls: SourceClass) -> None:
        if source_cls not in self.sources:
            self.sources.append(source_cls)

    def _add_store(self, store_cls: StoreClass) -> None:
        if store_cls not in self.stores:
            self.stores.append(store_cls)

    def _resolve_rules(self) -> None:
        for rule in self.rules:
            for source_cls in rule.sources:
                self._add_source(source_cls)
            for store_cls in rule.stores:
                self._add_store(store_cls)

    def _connect_sources(self) -> None:
        for source_class in self.sources:
            self._source_instances[source_class] = source_class(monitor=self)

    def _connect_stores(self) -> None:
        for store_class in self.stores:
            self._store_instances[store_class] = store_class(monitor=self)

    def _evaluate_rules(self) -> None:
        for rule_class in self.rules:
            self._evaluate_rule(rule_class)

    def _evaluate_rule(self, rule_class: RuleClass) -> None:
        rule = rule_class(self)
        result: Evaluation = rule.evaluate()
        if isinstance(result, Iterable):
            for metric in result:
                self.store_metric(rule, metric)
        elif not result:
            return
        else:
            self.store_metric(rule, result)

    def execute(self) -> None:
        """Start monitoring."""
        self._connect_stores()
        self._connect_sources()
        self._evaluate_rules()

    def source(self, source: SourceClass) -> SourceInstance:
        """Return an instatatied source."""
        try:
            return self._source_instances[source]
        except KeyError:
            raise SourceNotFound(f"Could not find {source.__name__} source instance.")

    def store_metric(self, rule: Rule, metric: Metric) -> None:
        """Store a metric."""
        if not metric.context:
            metric.context = self.context
        for store_class in rule.stores:
            store = self._store_instances[store_class]
            store.save_metric(metric)
