from __future__ import annotations

import json
from datetime import date
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

from .pipeline import ROUTES

DATASETS_BY_ROUTE = {route: dataset for dataset, route in ROUTES.items()}
MAX_REQUEST_BYTES = 64 * 1024


class MockHandler(BaseHTTPRequestHandler):
    fixture_dir: Path

    def log_message(self, format: str, *args: object) -> None:
        return

    def _send(self, status: int, body: object) -> None:
        payload = json.dumps(
            body, ensure_ascii=False, separators=(",", ":"), sort_keys=True
        ).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def do_GET(self) -> None:
        if urlsplit(self.path).path.rstrip("/") == "/health":
            self._send(200, {"service": "habitat-web-mock", "status": "ok"})
            return
        self._send(404, {"error": "unknown route"})

    def do_POST(self) -> None:
        route = urlsplit(self.path).path.rstrip("/")
        dataset = DATASETS_BY_ROUTE.get(route)
        if dataset is None:
            self._send(404, {"error": "unknown route"})
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            self._send(400, {"error": "invalid content length"})
            return
        if length <= 0 or length > MAX_REQUEST_BYTES:
            self._send(400, {"error": "invalid request size"})
            return
        try:
            request = json.loads(self.rfile.read(length))
            run_date = request["runDate"]
            if not isinstance(run_date, str):
                raise TypeError
            date.fromisoformat(run_date)
        except (KeyError, TypeError, ValueError, json.JSONDecodeError):
            self._send(400, {"error": "runDate must use YYYY-MM-DD"})
            return
        fixture_path = self.fixture_dir / f"{dataset}.json"
        try:
            response = json.loads(fixture_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            self._send(500, {"error": f"fixture unavailable: {dataset}"})
            return
        self._send(200, response)


def create_server(
    host: str, port: int, fixture_dir: Path
) -> ThreadingHTTPServer:
    handler = type(
        "ConfiguredMockHandler",
        (MockHandler,),
        {"fixture_dir": fixture_dir},
    )
    return ThreadingHTTPServer((host, port), handler)


def serve(host: str, port: int, fixture_dir: Path) -> None:
    create_server(host, port, fixture_dir).serve_forever()
