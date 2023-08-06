"""The Api adaptors provide sources and stores using API endpoints.
Requires the requests library to be installed.
"""
try:
    import requests
except ImportError:
    HAS_REQUESTS = False
else:
    HAS_REQUESTS = True

from types import ModuleType

from sinai import BaseView
from sinai.exceptions import DependencyMissing
from sinai.types import MonitorInstance, RequestHeader


class ApiConnection(BaseView):
    """Base class to share common connection information between API Stores and Sources"""

    url: str = ""
    headers: RequestHeader = {}
    token: str = ""

    def __init__(self, monitor: MonitorInstance):
        self.monitor = monitor
        super().__init__(monitor)
        if not HAS_REQUESTS:
            raise DependencyMissing("Requests library required for API calls.")
        self.requests: ModuleType = requests

    def get_headers(self) -> RequestHeader:
        """The required authentication, by default uses a bearer token."""
        if self.token:
            return self.bearer_headers(self.token)
        return self.headers

    @staticmethod
    def bearer_headers(token: str) -> RequestHeader:
        """Headers for APIs with bearer token authentication."""
        return {
            "accept": "application/json",
            "Authorization": "Bearer " + token,
        }
