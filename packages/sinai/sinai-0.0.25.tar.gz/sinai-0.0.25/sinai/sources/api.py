"""The Api source gets data from an API endpoints.
Requires the requests library to be installed.
"""
from sinai.adaptors.api import ApiConnection
from sinai.exceptions import SourceError
from sinai.sources.base import Source
from sinai.types import JDict, MonitorInstance


class ApiSource(Source, ApiConnection):
    """Get data from an API endpoint."""

    def __init__(self, monitor: MonitorInstance):
        super().__init__(monitor)
        self.content: JDict = {}
        self.get()

    def get(self) -> None:
        """Get the required data from the specified API."""
        response = self.requests.get(self.url, headers=self.get_headers())
        if response.status_code == 200:
            self.content = response.json()
        else:
            raise SourceError(
                f"The URL {self.url} returned status {response.status_code}."
            )
