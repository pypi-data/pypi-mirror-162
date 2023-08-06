"""Custom Data Types for Sinai."""

from decimal import Decimal
from numbers import Number
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Dict,
    List,
    Sequence,
    Tuple,
    Type,
    Union,
)
from uuid import UUID

try:
    # Version 3.10 and above:
    from typing import TypeAlias
except ImportError:
    # Python 3.9 and below:
    try:
        from typing_extensions import TypeAlias
    except ImportError:
        # Don't need typing in runtime
        TypeAlias = None  # type: ignore


if TYPE_CHECKING:  # pragma: no cover
    from sinai.metrics import AggregationMetric, Metric  # noqa: F401
    from sinai.monitors import Monitor  # noqa: F401
    from sinai.rules import Rule
    from sinai.sources import MetricSource, Source  # noqa: F401
    from sinai.stores import Store

    try:
        from bson.objectid import ObjectId  # pylint: disable=W0611
    except ImportError:
        pass

    try:
        from requests import Response  # noqa: F401
    except ImportError:
        pass


# Common Data Types
JDict = Dict[str, Any]  # A JSON-Safe Dictionary
JDictOrNone = Union[JDict, None]  # A JSON-Safe Dictionary or none
FList = List[Any]  # A Freeform List
SList = List[str]  # A List of Strings
NullableBool = Union[bool, None]

# Metric types
MetricInstance: TypeAlias = "Metric"
MetricList = List[MetricInstance]
MetricClass = Type[MetricInstance]
MetricClasses = List[MetricClass]
MetricId = Union[UUID, "ObjectId", str]
MetricDict = Dict[MetricId, MetricInstance]
MetricResult = Tuple[MetricInstance, MetricId]
MetricValue = Union[Number, Decimal, None, int, float]
MetricValueList = List[MetricValue]
AggregationFunction = Callable[[MetricValueList], MetricValue]
AggregationMetrics = List["AggregationMetric"]
Evaluation = Union[Sequence[MetricInstance], AggregationMetrics, MetricInstance, None]

# Monitor Types
MonitorInstance: TypeAlias = "Monitor"
GlobalMemory = Dict[MetricId, JDict]

# Rule types
RuleClass = Type["Rule"]
RuleClasses = List[RuleClass]

# Store types
StoreClass = Type["Store"]
StoreClassList = List[StoreClass]
StoreDict = Dict[StoreClass, "Store"]
StoreClasses = Sequence[StoreClass]

# Source types
SourceInstance: TypeAlias = "Source"
SourceClass = Type[SourceInstance]
SourceClassList = List[SourceClass]
SourceDict = Dict[SourceClass, SourceInstance]
SourceClasses = Sequence[SourceClass]

# MetricSource types
MetricSourceInstance: TypeAlias = "MetricSource"
MetricSourceClass = Type[MetricSourceInstance]
MetricSourceClasses = Sequence[MetricSourceClass]


# ApiSource types
RequestHeader = Dict[str, str]

# Mongo adapter types
MongoResult: TypeAlias = Any

# ApiStore types
RequestResponse: TypeAlias = "Response"
PostResponse = Union[JDict, bytes]
