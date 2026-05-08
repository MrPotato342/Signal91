import requests
from typing import List, Dict, Any, Optional

from .exceptions import Signal91APIError


class Signal91Client:

    def __init__(
        self,
        base_url: str = "http://localhost:8000",
        timeout: int = 30,
        api_key: Optional[str] = None
    ):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()

        self.headers = {
            "Content-Type": "application/json"
        }

        if api_key:
            self.headers["Authorization"] = f"Bearer {api_key}"

    # -----------------------------------------
    # Internal request handler
    # -----------------------------------------

    def _request(
        self,
        method: str,
        endpoint: str,
        json: Optional[dict] = None
    ) -> Dict[str, Any]:

        url = f"{self.base_url}{endpoint}"

        try:

            response = self.session.request(
                method=method,
                url=url,
                json=json,
                headers=self.headers,
                timeout=self.timeout
            )

        except requests.RequestException as exc:
            raise Signal91APIError(str(exc))

        try:
            data = response.json()

        except Exception:
            raise Signal91APIError(
                f"Invalid JSON response: {response.text}"
            )

        if response.status_code >= 400:

            message = data.get("error", "Unknown API error")

            raise Signal91APIError(
                f"{response.status_code}: {message}"
            )

        return data

    # -----------------------------------------
    # Health
    # -----------------------------------------

    def health(self):

        return self._request(
            "GET",
            "/health"
        )

    # -----------------------------------------
    # Version
    # -----------------------------------------

    def version(self):

        return self._request(
            "GET",
            "/version"
        )

    # -----------------------------------------
    # Single Analyze
    # -----------------------------------------

    def analyze(self, phone: str):

        return self._request(
            "POST",
            "/analyze",
            json={
                "phone": phone
            }
        )

    # -----------------------------------------
    # Bulk Analyze
    # -----------------------------------------

    def bulk_analyze(self, numbers: List[str]):

        return self._request(
            "POST",
            "/bulk-analyze",
            json={
                "numbers": numbers
            }
        )