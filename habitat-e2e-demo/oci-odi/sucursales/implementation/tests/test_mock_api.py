from __future__ import annotations

import json
import sys
import threading
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

import pytest


IMPLEMENTATION_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(IMPLEMENTATION_ROOT))

from habitat_sucursales.cli import main
from habitat_sucursales.mock_api import SucursalesBackend, create_server


class RecordingBackend:
    def __init__(self) -> None:
        self.calls: list[tuple[str, dict[str, object]]] = []

    def periods(self, payload: dict[str, object]) -> dict[str, object]:
        return self._record("periods", payload)

    def process_atenciones(self, payload: dict[str, object]) -> dict[str, object]:
        return self._record("process_atenciones", payload)

    def process_agendamientos(self, payload: dict[str, object]) -> dict[str, object]:
        return self._record("process_agendamientos", payload)

    def validate(self, payload: dict[str, object]) -> dict[str, object]:
        return self._record("validate", payload)

    def notify_error(self, payload: dict[str, object]) -> dict[str, object]:
        return self._record("notify_error", payload)

    def _record(
        self, operation: str, payload: dict[str, object]
    ) -> dict[str, object]:
        self.calls.append((operation, payload))
        return {"status": "ok", "operation": operation, "request": payload}


@pytest.fixture
def running_server():
    backend = RecordingBackend()
    server = create_server("127.0.0.1", 0, backend=backend)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_port}", backend
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def _get_json(url: str) -> tuple[int, dict[str, object]]:
    with urlopen(url, timeout=3) as response:
        return response.status, json.load(response)


def _post_json(
    url: str, payload: object, content_type: str = "application/json"
) -> tuple[int, dict[str, object]]:
    request = Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": content_type},
        method="POST",
    )
    with urlopen(request, timeout=3) as response:
        return response.status, json.load(response)


def test_health_endpoint_is_json_and_does_not_call_backend(running_server) -> None:
    base_url, backend = running_server

    status, body = _get_json(f"{base_url}/health")

    assert status == 200
    assert body == {"service": "habitat-sucursales-mock", "status": "ok"}
    assert backend.calls == []


@pytest.mark.parametrize(
    ("path", "operation"),
    [
        ("/v1/periods", "periods"),
        ("/v1/process/atenciones", "process_atenciones"),
        ("/v1/process/agendamientos", "process_agendamientos"),
        ("/v1/validate", "validate"),
        ("/v1/notify-error", "notify_error"),
    ],
)
def test_post_routes_dispatch_json_payload(
    running_server, path: str, operation: str
) -> None:
    base_url, backend = running_server
    payload = {"as_of_date": "2026-07-24", "window": "previous"}

    status, body = _post_json(f"{base_url}{path}", payload)

    assert status == 200
    assert body["status"] == "ok"
    assert body["operation"] == operation
    assert backend.calls[-1] == (operation, payload)


def test_rejects_non_object_json_body(running_server) -> None:
    base_url, _ = running_server

    with pytest.raises(HTTPError) as error:
        _post_json(f"{base_url}/v1/periods", ["not", "an", "object"])

    assert error.value.code == 400
    assert json.load(error.value)["error"] == "request body must be a JSON object"


def test_rejects_non_json_content_type(running_server) -> None:
    base_url, _ = running_server

    with pytest.raises(HTTPError) as error:
        _post_json(
            f"{base_url}/v1/periods",
            {"as_of_date": "2026-07-24"},
            content_type="text/plain",
        )

    assert error.value.code == 415


def test_unknown_route_returns_json_404(running_server) -> None:
    base_url, _ = running_server

    with pytest.raises(HTTPError) as error:
        _get_json(f"{base_url}/not-found")

    assert error.value.code == 404
    assert json.load(error.value) == {"error": "route not found", "status": "error"}


def test_default_backend_returns_derived_shell_adapter_arguments(
    tmp_path: Path,
) -> None:
    backend = SucursalesBackend(
        IMPLEMENTATION_ROOT / "fixtures/raw", tmp_path / "output"
    )

    response = backend.process_atenciones(
        {"as_of_date": "2026-07-24", "window": "previous"}
    )

    assert response["status"] == "ok"
    assert response["adapter_args"] == {
        "end_date": "2026-06-30",
        "flag": True,
        "period": "202606",
        "start_date": "2026-06-01",
    }


def test_validate_requires_exact_eight_period_outputs(tmp_path: Path) -> None:
    backend = SucursalesBackend(
        IMPLEMENTATION_ROOT / "fixtures/raw", tmp_path / "output"
    )
    for window in ("previous", "current"):
        request = {"as_of_date": "2026-07-24", "window": window}
        backend.process_atenciones(request)
        backend.process_agendamientos(request)

    result = backend.validate({"as_of_date": "2026-07-24"})

    assert result["validated"] == 8
    (tmp_path / "output/stale.csv").write_text("stale", encoding="utf-8")
    with pytest.raises(ValueError, match="unexpected output files"):
        backend.validate({"as_of_date": "2026-07-24"})


def test_validate_accepts_eight_zero_row_outputs(tmp_path: Path) -> None:
    fixture_root = tmp_path / "fixtures"
    for period in ("202606", "202607"):
        period_dir = fixture_root / period
        period_dir.mkdir(parents=True)
        for source_name in (
            f"AtencionesZeroQ_{period}.csv",
            f"AgendamientoZeroQ_{period}.csv",
        ):
            source = IMPLEMENTATION_ROOT / "fixtures/raw" / period / source_name
            header = source.read_text(encoding="utf-8").splitlines()[0]
            (period_dir / source_name).write_text(f"{header}\n", encoding="utf-8")

    backend = SucursalesBackend(fixture_root, tmp_path / "output")
    for window in ("previous", "current"):
        request = {"as_of_date": "2026-07-24", "window": window}
        backend.process_atenciones(request)
        backend.process_agendamientos(request)

    result = backend.validate({"as_of_date": "2026-07-24"})

    assert result["validated"] == 8
    assert all(path.stat().st_size == 0 for path in (tmp_path / "output").rglob("*.csv"))


@pytest.mark.parametrize(
    "payload",
    [
        {},
        {"status": "error", "step": "", "message": "failure"},
        {"status": "error", "step": "atenciones_previous", "message": ""},
    ],
)
def test_notification_requires_complete_error_contract(
    tmp_path: Path, payload: dict[str, object]
) -> None:
    backend = SucursalesBackend(tmp_path / "fixtures", tmp_path / "output")

    with pytest.raises(ValueError):
        backend.notify_error(payload)


def test_run_cli_executes_full_mock_pipeline(tmp_path: Path, capsys) -> None:
    output_dir = tmp_path / "output"

    status = main(
        [
            "run",
            "--as-of-date",
            "2026-07-24",
            "--fixtures-dir",
            str(IMPLEMENTATION_ROOT / "fixtures/raw"),
            "--output-dir",
            str(output_dir),
        ]
    )

    response = json.loads(capsys.readouterr().out)
    assert status == 0
    assert response["status"] == "SUCCEEDED"
    assert len(list(output_dir.rglob("*.csv"))) == 8
