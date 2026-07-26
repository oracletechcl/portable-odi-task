"""Locally runnable orchestration matching ``cargaArchivoExterno.kjb``."""

from __future__ import annotations

import csv
from collections.abc import Callable
from pathlib import Path
from typing import Any

from .contracts import (
    AGENDAMIENTOS_BASE_FIELDS,
    AGENDAMIENTOS_MOTIVO_FIELDS,
    AGENDAMIENTOS_SOURCE_FIELDS,
    ATENCIONES_BASE_FIELDS,
    ATENCIONES_MOTIVO_FIELDS,
    ATENCIONES_SOURCE_FIELDS,
    OUTPUT_ENCODING,
    OUTPUT_SEPARATOR,
)
from .periods import calculate_periods
from .transformations import (
    transform_agendamientos_base,
    transform_agendamientos_motivos,
    transform_atenciones_base,
    transform_atenciones_motivos,
)

NotificationCallback = Callable[[dict[str, str]], None]
PROCESSING_STEPS = (
    "atenciones_previous",
    "atenciones_current",
    "agendamientos_previous",
    "agendamientos_current",
)
FAILURE_STEPS = frozenset(("periods", *PROCESSING_STEPS, "validate"))


class PipelineExecutionError(RuntimeError):
    """Failure carrying the Pentaho-equivalent pipeline step name."""

    def __init__(self, step: str, message: str) -> None:
        super().__init__(f"{step}: {message}")
        self.step = step
        self.message = message
        self.notification_error: str | None = None


def process_atenciones(
    period: str,
    fixtures_dir: str | Path,
    output_dir: str | Path,
) -> dict[str, Any]:
    """Process one Atenciones month and write its base and motivo outputs."""

    source = _read_source(
        Path(fixtures_dir) / period / f"AtencionesZeroQ_{period}.csv",
        ATENCIONES_SOURCE_FIELDS,
    )
    base_rows = transform_atenciones_base(source, period)
    motivo_rows = transform_atenciones_motivos(source, period)
    period_dir = Path(output_dir) / period
    base_path = period_dir / "AtencionesZeroQ.csv"
    motivo_path = period_dir / "MotivoAtencionZeroQ.csv"
    _write_rows(base_path, base_rows, ATENCIONES_BASE_FIELDS)
    _write_rows(motivo_path, motivo_rows, ATENCIONES_MOTIVO_FIELDS)
    return {
        "period": period,
        "row_counts": {"base": len(base_rows), "motivos": len(motivo_rows)},
        "outputs": [
            str(base_path.relative_to(output_dir)),
            str(motivo_path.relative_to(output_dir)),
        ],
    }


def process_agendamientos(
    period: str,
    fixtures_dir: str | Path,
    output_dir: str | Path,
) -> dict[str, Any]:
    """Process one Agendamientos month and write base and motivo outputs."""

    source = _read_source(
        Path(fixtures_dir) / period / f"AgendamientoZeroQ_{period}.csv",
        AGENDAMIENTOS_SOURCE_FIELDS,
    )
    base_rows = transform_agendamientos_base(source, period)
    motivo_rows = transform_agendamientos_motivos(source, period)
    period_dir = Path(output_dir) / period
    base_path = period_dir / "AgendamientoZeroQ.csv"
    motivo_path = period_dir / "MotivoAgendamientoZeroQ.csv"
    _write_rows(base_path, base_rows, AGENDAMIENTOS_BASE_FIELDS)
    _write_rows(motivo_path, motivo_rows, AGENDAMIENTOS_MOTIVO_FIELDS)
    return {
        "period": period,
        "row_counts": {"base": len(base_rows), "motivos": len(motivo_rows)},
        "outputs": [
            str(base_path.relative_to(output_dir)),
            str(motivo_path.relative_to(output_dir)),
        ],
    }


def run_pipeline(
    as_of_date: str,
    fixtures_dir: str | Path,
    output_dir: str | Path,
    *,
    fail_at: str | None = None,
    notifier: NotificationCallback | None = None,
) -> dict[str, Any]:
    """Run the complete success path, or notify and abort at an injected step."""

    fixtures_path = Path(fixtures_dir)
    output_path = Path(output_dir)
    if fail_at is not None and fail_at not in FAILURE_STEPS:
        allowed = ", ".join(sorted(FAILURE_STEPS))
        raise ValueError(f"unsupported fail_at {fail_at!r}; expected one of: {allowed}")
    steps = ["periods"]
    if fail_at == "periods":
        raise PipelineExecutionError("periods", "Injected failure at periods")
    periods = calculate_periods(as_of_date)

    outputs: list[str] = []
    process_steps = (
        ("atenciones_previous", process_atenciones, periods.previous),
        ("atenciones_current", process_atenciones, periods.current),
        ("agendamientos_previous", process_agendamientos, periods.previous),
        ("agendamientos_current", process_agendamientos, periods.current),
    )
    for step, processor, period in process_steps:
        try:
            if fail_at == step:
                raise PipelineExecutionError(
                    step, f"Injected failure at {step}"
                )
            result = processor(period, fixtures_path, output_path)
            outputs.extend(result["outputs"])
            steps.append(step)
        except Exception as exc:
            failure = (
                exc
                if isinstance(exc, PipelineExecutionError)
                else PipelineExecutionError(step, str(exc))
            )
            if notifier is not None:
                try:
                    notifier(
                        {
                            "status": "FAILED",
                            "step": failure.step,
                            "message": failure.message,
                        }
                    )
                except Exception as notification_error:
                    failure.notification_error = str(notification_error)
            raise failure from exc

    if fail_at == "validate":
        raise PipelineExecutionError(
            "validate", "Injected failure at validate"
        )
    _validate_outputs(output_path, outputs)
    steps.extend(("validate", "success"))
    return {
        "status": "SUCCEEDED",
        "periods": periods.to_dict(),
        "steps": steps,
        "outputs": outputs,
    }


def _read_source(
    path: Path, expected_fields: tuple[str, ...]
) -> list[dict[str, str]]:
    if not path.is_file():
        raise FileNotFoundError(f"mock source file not found: {path}")
    with path.open("r", encoding=OUTPUT_ENCODING, newline="") as stream:
        reader = csv.reader(stream, delimiter=";")
        try:
            header = next(reader)
        except StopIteration as exc:
            raise ValueError(f"source file has no header: {path}") from exc
        if tuple(header) != expected_fields:
            raise ValueError(
                f"source header does not match the Pentaho schema: {path}"
            )
        rows: list[dict[str, str]] = []
        for values in reader:
            if len(values) != len(expected_fields):
                raise ValueError(
                    f"source row {reader.line_num} has {len(values)} fields; "
                    f"expected {len(expected_fields)}: {path}"
                )
            rows.append(dict(zip(expected_fields, values, strict=True)))
        return rows


def _write_rows(
    path: Path,
    rows: list[dict[str, Any]],
    fields: tuple[str, ...],
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding=OUTPUT_ENCODING, newline="") as stream:
        for row in rows:
            values = [_serialize(row.get(field)) for field in fields]
            if any(
                OUTPUT_SEPARATOR in value or "\n" in value or "\r" in value
                for value in values
            ):
                raise ValueError(
                    "output values cannot contain the Pentaho separator "
                    "or a line break"
                )
            stream.write(OUTPUT_SEPARATOR.join(values))
            stream.write("\n")


def _serialize(value: Any) -> str:
    return "" if value is None else str(value)


def _validate_outputs(output_dir: Path, outputs: list[str]) -> None:
    if len(outputs) != 8:
        raise PipelineExecutionError(
            "validate", f"expected 8 output files, found {len(outputs)}"
        )
    for relative_path in outputs:
        output = output_dir / relative_path
        # Pentaho emits a valid zero-byte, headerless file for a zero-row source.
        if not output.is_file():
            raise PipelineExecutionError(
                "validate", f"missing output: {relative_path}"
            )
