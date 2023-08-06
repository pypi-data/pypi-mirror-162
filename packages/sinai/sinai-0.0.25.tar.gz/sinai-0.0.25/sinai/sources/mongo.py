"""Retrieving data and metics from MongoDB."""

from sinai.adaptors.mongo import Mongo
from sinai.metrics import Metric
from sinai.sources import MetricSource, Source
from sinai.types import (
    FList,
    JDict,
    JDictOrNone,
    MetricInstance,
    MetricList,
    MongoResult,
)


class MongoSource(Mongo, Source):
    """Gets arbitrary documents from MongoDB."""

    def find_one(
        self,
        collection: str,
        mongo_filter: JDictOrNone = None,
        *args: FList,
        **kwargs: JDict,
    ) -> MongoResult:
        """Find a single document from MongoFB."""
        return self.db[collection].find_one(mongo_filter, *args, **kwargs)

    def find(
        self,
        collection: str,
        mongo_filter: JDictOrNone = None,
        *args: FList,
        **kwargs: JDict,
    ) -> MongoResult:
        """Find documents from MongoFB."""
        return self.db[collection].find(mongo_filter, *args, **kwargs)


class MongoMetricSource(MongoSource, MetricSource):
    """Gets metrics from MongoDB."""

    def _execute_query(self, metric_filter: JDict) -> MetricList:
        return [
            self._document_to_metric(document)
            for document in self.collection.find(metric_filter)
        ]

    @staticmethod
    def _document_to_metric(document: JDict) -> MetricInstance:
        del document["_id"]
        return Metric.from_dict(document)
