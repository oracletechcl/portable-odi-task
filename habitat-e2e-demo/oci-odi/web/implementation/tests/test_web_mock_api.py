from __future__ import annotations

import json
import threading
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator
from urllib.error import HTTPError
from urllib.request import Request, urlopen

import pytest

from habitat_web.mock_api import create_server
from habitat_web.pipeline import ROUTES
from habitat_web.mock_release import build_release


@contextmanager
def running_mock() -> Iterator[str]:
    fixture_dir = (
        Path(__file__).parents[1] / "fixtures" / "mock-responses"
    )
    server = create_server("127.0.0.1", 0, fixture_dir)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        host, port = server.server_address
        yield f"http://{host}:{port}"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


def _post(base_url: str, route: str, body: object) -> tuple[int, object]:
    request = Request(
        base_url + route,
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urlopen(request, timeout=2) as response:
            return response.status, json.loads(response.read())
    except HTTPError as exc:
        return exc.code, json.loads(exc.read())


def test_mock_serves_every_web_dataset_route() -> None:
    with running_mock() as base_url:
        for dataset, route in ROUTES.items():
            status, body = _post(
                base_url, route, {"runDate": "2026-07-25"}
            )
            assert status == 200
            assert isinstance(body, dict)
            assert isinstance(body["records"], list)
            assert body["records"], dataset


def test_mock_accepts_trailing_slashes_and_has_health() -> None:
    route = next(iter(ROUTES.values()))
    with running_mock() as base_url:
        status, _ = _post(
            base_url, route + "/", {"runDate": "2026-07-25"}
        )
        assert status == 200
        with urlopen(base_url + "/health", timeout=2) as response:
            assert response.status == 200


@pytest.mark.parametrize(
    ("route", "body", "expected_status"),
    (
        ("/v1/web/not-a-dataset", {"runDate": "2026-07-25"}, 404),
        (next(iter(ROUTES.values())), {}, 400),
        (next(iter(ROUTES.values())), {"runDate": "25-07-2026"}, 400),
    ),
)
def test_mock_rejects_unknown_routes_and_invalid_payloads(
    route: str, body: object, expected_status: int
) -> None:
    with running_mock() as base_url:
        status, _ = _post(base_url, route, body)
        assert status == expected_status


def test_mock_release_is_deterministic(tmp_path: Path) -> None:
    implementation_root = Path(__file__).parents[1]
    first = tmp_path / "first.tar.gz"
    second = tmp_path / "second.tar.gz"

    first_digest = build_release(implementation_root, first)
    second_digest = build_release(implementation_root, second)

    assert first.read_bytes() == second.read_bytes()
    assert first_digest == second_digest
    assert first.with_suffix(".gz.sha256").read_text().endswith(
        "  first.tar.gz\n"
    )
