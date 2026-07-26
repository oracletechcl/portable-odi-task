"""Standard-library HTTP façade for the portable Sucursales flow."""

from __future__ import annotations

import json
import threading
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Protocol


MAX_REQUEST_BYTES = 1024 * 1024
OUTPUT_NAMES = (
    "AtencionesZeroQ.csv",
    "MotivoAtencionZeroQ.csv",
    "AgendamientoZeroQ.csv",
    "MotivoAgendamientoZeroQ.csv",
)


class _UnsupportedMediaType(ValueError):
    pass


class Backend(Protocol):
    """Operations exposed by the mock HTTP boundary."""

    def periods(self, payload: dict[str, object]) -> dict[str, object]: ...

    def process_atenciones(
        self, payload: dict[str, object]
    ) -> dict[str, object]: ...

    def process_agendamientos(
        self, payload: dict[str, object]
    ) -> dict[str, object]: ...

    def validate(self, payload: dict[str, object]) -> dict[str, object]: ...

    def notify_error(self, payload: dict[str, object]) -> dict[str, object]: ...


class SucursalesBackend:
    """Adapter from HTTP payloads to the pure portable implementation."""

    def __init__(self, fixtures_dir: Path, output_dir: Path) -> None:
        self.fixtures_dir = Path(fixtures_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self._mutation_lock = threading.RLock()

    def periods(self, payload: dict[str, object]) -> dict[str, object]:
        from habitat_sucursales import calculate_periods

        as_of_date = self._required_text(payload, "as_of_date")
        self._inject_failure(payload, "periods")
        periods = calculate_periods(as_of_date)
        return {"periods": periods.to_dict(), "status": "ok"}

    def process_atenciones(
        self, payload: dict[str, object]
    ) -> dict[str, object]:
        from habitat_sucursales import calculate_periods, process_atenciones

        as_of_date = self._required_text(payload, "as_of_date")
        window = self._window(payload)
        self._inject_failure(payload, f"atenciones_{window}")
        window_values = calculate_periods(as_of_date).window(window)
        with self._mutation_lock:
            result = process_atenciones(
                window_values["period"], self.fixtures_dir, self.output_dir
            )
        return {
            "adapter_args": self._adapter_args(window_values),
            "result": result,
            "status": "ok",
        }

    def process_agendamientos(
        self, payload: dict[str, object]
    ) -> dict[str, object]:
        from habitat_sucursales import calculate_periods, process_agendamientos

        as_of_date = self._required_text(payload, "as_of_date")
        window = self._window(payload)
        self._inject_failure(payload, f"agendamientos_{window}")
        window_values = calculate_periods(as_of_date).window(window)
        with self._mutation_lock:
            result = process_agendamientos(
                window_values["period"], self.fixtures_dir, self.output_dir
            )
        return {
            "adapter_args": self._adapter_args(window_values),
            "result": result,
            "status": "ok",
        }

    def validate(self, payload: dict[str, object]) -> dict[str, object]:
        self._inject_failure(payload, "validate")
        requested = payload.get("files")
        if requested is not None:
            if not isinstance(requested, list) or not all(
                isinstance(item, str) for item in requested
            ):
                raise ValueError("files must be an array of relative paths")
            if len(requested) != len(set(requested)):
                raise ValueError("files must not contain duplicates")
            paths = [self._safe_output_path(item) for item in requested]
        else:
            from habitat_sucursales import calculate_periods

            as_of_date = self._required_text(payload, "as_of_date")
            periods = calculate_periods(as_of_date)
            expected = {
                Path(period) / name
                for period in (periods.previous, periods.current)
                for name in OUTPUT_NAMES
            }
            actual = {
                path.relative_to(self.output_dir)
                for path in self.output_dir.rglob("*.csv")
                if path.is_file()
            }
            missing = sorted(expected - actual)
            unexpected = sorted(actual - expected)
            if missing:
                raise ValueError(
                    "missing output files: "
                    + ", ".join(str(path) for path in missing)
                )
            if unexpected:
                raise ValueError(
                    "unexpected output files: "
                    + ", ".join(str(path) for path in unexpected)
                )
            paths = [self.output_dir / path for path in sorted(expected)]

        if not paths:
            raise ValueError("no output files are available for validation")
        missing = [
            str(path.relative_to(self.output_dir))
            for path in paths
            if not path.is_file()
        ]
        if missing:
            raise ValueError(f"missing output files: {', '.join(missing)}")
        return {
            "files": [str(path.relative_to(self.output_dir)) for path in paths],
            "status": "ok",
            "validated": len(paths),
        }

    def notify_error(self, payload: dict[str, object]) -> dict[str, object]:
        for field in ("status", "step", "message"):
            self._required_text(payload, field)
        notification_path = self.output_dir / "notifications.jsonl"
        with self._mutation_lock:
            with notification_path.open("a", encoding="utf-8") as stream:
                stream.write(
                    json.dumps(payload, ensure_ascii=False, sort_keys=True) + "\n"
                )
        return {
            "notification_file": notification_path.name,
            "status": "recorded",
        }

    def _safe_output_path(self, relative: str) -> Path:
        candidate = (self.output_dir / relative).resolve()
        output_root = self.output_dir.resolve()
        if candidate != output_root and output_root not in candidate.parents:
            raise ValueError("output file escapes the configured output directory")
        return candidate

    @staticmethod
    def _required_text(payload: dict[str, object], name: str) -> str:
        value = payload.get(name)
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{name} is required")
        return value

    @staticmethod
    def _window(payload: dict[str, object]) -> str:
        window = payload.get("window")
        if window not in {"previous", "current"}:
            raise ValueError("window must be previous or current")
        return str(window)

    @staticmethod
    def _inject_failure(payload: dict[str, object], step: str) -> None:
        requested = payload.get("fail_at")
        if requested == step or payload.get("inject_failure") is True:
            raise RuntimeError(f"injected failure at {step}")

    @staticmethod
    def _adapter_args(window_values: dict[str, str]) -> dict[str, object]:
        return {
            "end_date": window_values["end_date"],
            "flag": True,
            "period": window_values["period"],
            "start_date": window_values["start_date"],
        }


class _ReusableThreadingHTTPServer(ThreadingHTTPServer):
    allow_reuse_address = True
    daemon_threads = True


def create_server(
    host: str,
    port: int,
    *,
    backend: Backend | None = None,
    fixtures_dir: Path | str | None = None,
    output_dir: Path | str | None = None,
) -> ThreadingHTTPServer:
    """Create, but do not start, the mock server."""

    if backend is None:
        if fixtures_dir is None or output_dir is None:
            raise ValueError(
                "fixtures_dir and output_dir are required when backend is omitted"
            )
        backend = SucursalesBackend(Path(fixtures_dir), Path(output_dir))

    routes = {
        "/v1/periods": backend.periods,
        "/v1/process/atenciones": backend.process_atenciones,
        "/v1/process/agendamientos": backend.process_agendamientos,
        "/v1/validate": backend.validate,
        "/v1/notify-error": backend.notify_error,
    }

    class Handler(BaseHTTPRequestHandler):
        server_version = "HabitatSucursalesMock/1.0"

        def do_GET(self) -> None:  # noqa: N802
            if self.path == "/health":
                self._send_json(
                    HTTPStatus.OK,
                    {"service": "habitat-sucursales-mock", "status": "ok"},
                )
                return
            self._send_json(
                HTTPStatus.NOT_FOUND,
                {"error": "route not found", "status": "error"},
            )

        def do_POST(self) -> None:  # noqa: N802
            operation = routes.get(self.path)
            if operation is None:
                self._send_json(
                    HTTPStatus.NOT_FOUND,
                    {"error": "route not found", "status": "error"},
                )
                return
            try:
                payload = self._read_payload()
                response = operation(payload)
            except _UnsupportedMediaType as exc:
                self._send_json(
                    HTTPStatus.UNSUPPORTED_MEDIA_TYPE,
                    {"error": str(exc), "status": "error"},
                )
                return
            except (json.JSONDecodeError, UnicodeDecodeError) as exc:
                self._send_json(
                    HTTPStatus.BAD_REQUEST,
                    {"error": f"invalid JSON: {exc.msg}", "status": "error"},
                )
                return
            except ValueError as exc:
                self._send_json(
                    HTTPStatus.BAD_REQUEST,
                    {"error": str(exc), "status": "error"},
                )
                return
            except Exception as exc:  # Deliberate mock failure boundary.
                self._send_json(
                    HTTPStatus.INTERNAL_SERVER_ERROR,
                    {"error": str(exc), "status": "error"},
                )
                return
            self._send_json(HTTPStatus.OK, response)

        def _read_payload(self) -> dict[str, object]:
            content_type = self.headers.get_content_type()
            if content_type != "application/json":
                raise _UnsupportedMediaType(
                    "Content-Type must be application/json"
                )
            raw_length = self.headers.get("Content-Length")
            if raw_length is None:
                raise ValueError("Content-Length is required")
            length = int(raw_length)
            if length < 0 or length > MAX_REQUEST_BYTES:
                raise ValueError("request body exceeds the 1 MiB limit")
            payload: Any = json.loads(self.rfile.read(length).decode("utf-8"))
            if not isinstance(payload, dict):
                raise ValueError("request body must be a JSON object")
            return payload

        def _send_json(
            self, status: HTTPStatus, payload: dict[str, object]
        ) -> None:
            body = json.dumps(
                payload, ensure_ascii=False, separators=(",", ":"), sort_keys=True
            ).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, format: str, *args: object) -> None:
            return

    return _ReusableThreadingHTTPServer((host, port), Handler)
