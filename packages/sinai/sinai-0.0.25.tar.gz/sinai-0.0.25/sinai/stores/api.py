"""The Api store posts data to an API endpoint.
Requires the requests library to be installed.
"""

from sinai.adaptors.api import ApiConnection
from sinai.exceptions import SourceError
from sinai.stores.base import Store
from sinai.types import JDict, MonitorInstance, PostResponse, RequestResponse


class ApiStore(Store, ApiConnection):
    """Send data to an API endpoint."""

    def __init__(self, monitor: MonitorInstance):
        super().__init__(monitor)
        self.content: JDict = {}
        self.response: RequestResponse = self.requests.Response()

    def post(self, data: JDict) -> PostResponse:
        """Post the data to the specified API."""
        self.response = self.requests.post(
            self.url, headers=self.get_headers(), json=data
        )
        if self.response.status_code != 200:
            raise SourceError(
                f"The URL {self.url} returned status {self.response.status_code}."
            )
        try:
            json_response: JDict = self.response.json()
        except self.requests.JSONDecodeError:
            return self.response.content
        return json_response
