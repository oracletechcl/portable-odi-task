from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen


class BoundaryError(RuntimeError):
    """Raised when the configured backend cannot satisfy its HTTP contract."""


@dataclass(frozen=True)
class JsonHttpClient:
    base_url: str
    timeout_seconds: float

    def __post_init__(self) -> None:
        parsed = urlparse(self.base_url)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise ValueError("base_url must be an absolute HTTP(S) URL")
        if self.timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be positive")

    def post_json(self, route: str, payload: dict[str, str]) -> Any:
        target = urljoin(self.base_url.rstrip("/") + "/", route.lstrip("/"))
        request = Request(
            target,
            data=json.dumps(payload, sort_keys=True, separators=(",", ":")).encode(),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urlopen(request, timeout=self.timeout_seconds) as response:
                body = response.read()
        except (HTTPError, URLError, TimeoutError) as exc:
            raise BoundaryError(f"POST {route} failed: {exc}") from exc
        try:
            return json.loads(body)
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise BoundaryError(f"POST {route} returned invalid JSON") from exc

