"""Support for using Mongo Databases as a source or store for data."""

from __future__ import annotations

try:
    import pymongo
except ImportError:
    HAS_MONGO = False
else:
    HAS_MONGO = True

try:
    import certifi
except ImportError:
    HAS_CERTIFI = False
else:
    HAS_CERTIFI = True

from sinai.exceptions import DependencyMissing
from sinai.types import MonitorInstance


class Mongo:
    """A connection to MongoDB."""

    connection_string = ""
    database_name = ""
    use_certificates = False

    def __init__(self, monitor: MonitorInstance) -> None:
        self.monitor = monitor
        if not HAS_MONGO:
            raise DependencyMissing(
                "Pymongo library required for using Mongo databases."
            )
        if self.use_certificates:
            if not HAS_CERTIFI:
                raise DependencyMissing(
                    "The certifi library is required for using SSL certifications with Mongo database connections."
                )
            self.client = pymongo.MongoClient(self.connection_string, tlsCAFile=certifi.where())  # type: ignore
        else:
            self.client = pymongo.MongoClient(self.connection_string)  # type: ignore
        self.db = self.client[self.database_name]
        self.collection = self.db["metrics"]
