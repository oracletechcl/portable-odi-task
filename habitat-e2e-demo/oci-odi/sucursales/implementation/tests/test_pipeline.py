import csv
from pathlib import Path

import pytest

from habitat_sucursales.contracts import (
    AGENDAMIENTOS_SOURCE_FIELDS,
    ATENCIONES_BASE_FIELDS,
    ATENCIONES_SOURCE_FIELDS,
)
from habitat_sucursales.pipeline import (
    PipelineExecutionError,
    process_agendamientos,
    process_atenciones,
    run_pipeline,
)


FIXTURES_DIR = Path(__file__).resolve().parents[1] / "fixtures" / "raw"


def _write_source(
    fixtures_dir: Path,
    period: str,
    filename: str,
    fields: tuple[str, ...],
    rows: list[dict[str, str]],
) -> Path:
    path = fixtures_dir / period / filename
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="iso-8859-1", newline="") as stream:
        writer = csv.DictWriter(
            stream,
            fieldnames=fields,
            delimiter=";",
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(rows)
    return path


def test_process_helpers_write_base_and_motivo_outputs(tmp_path: Path) -> None:
    atenciones = process_atenciones("202606", FIXTURES_DIR, tmp_path)
    agendamientos = process_agendamientos("202606", FIXTURES_DIR, tmp_path)

    assert atenciones["row_counts"] == {"base": 1, "motivos": 2}
    assert agendamientos["row_counts"] == {"base": 1, "motivos": 1}
    assert (tmp_path / "202606" / "AtencionesZeroQ.csv").read_text(
        encoding="iso-8859-1"
    ).startswith("20260601~|T-202606")
    assert (tmp_path / "202606" / "MotivoAtencionZeroQ.csv").exists()
    assert (tmp_path / "202606" / "AgendamientoZeroQ.csv").exists()
    assert (tmp_path / "202606" / "MotivoAgendamientoZeroQ.csv").exists()


def test_run_pipeline_preserves_job_order_and_emits_eight_files(
    tmp_path: Path,
) -> None:
    result = run_pipeline("2026-07-15", FIXTURES_DIR, tmp_path)

    assert result["status"] == "SUCCEEDED"
    assert result["periods"] == {
        "as_of_date": "2026-07-15",
        "previous": "202606",
        "current": "202607",
        "previous_start_date": "2026-06-01",
        "previous_end_date": "2026-06-30",
        "current_start_date": "2026-07-01",
        "current_end_date": "2026-07-31",
    }
    assert result["steps"] == [
        "periods",
        "atenciones_previous",
        "atenciones_current",
        "agendamientos_previous",
        "agendamientos_current",
        "validate",
        "success",
    ]
    assert len(result["outputs"]) == 8
    assert all((tmp_path / relative_path).is_file() for relative_path in result["outputs"])


def test_run_pipeline_notifies_and_aborts_on_injected_failure(
    tmp_path: Path,
) -> None:
    notifications: list[dict[str, str]] = []

    with pytest.raises(PipelineExecutionError, match="atenciones_current"):
        run_pipeline(
            "2026-07-15",
            FIXTURES_DIR,
            tmp_path,
            fail_at="atenciones_current",
            notifier=notifications.append,
        )

    assert notifications == [
        {
            "status": "FAILED",
            "step": "atenciones_current",
            "message": "Injected failure at atenciones_current",
        }
    ]
    assert not (tmp_path / "202607" / "AtencionesZeroQ.csv").exists()


def test_period_failure_aborts_without_notification(tmp_path: Path) -> None:
    notifications: list[dict[str, str]] = []

    with pytest.raises(PipelineExecutionError, match="periods"):
        run_pipeline(
            "2026-07-15",
            FIXTURES_DIR,
            tmp_path,
            fail_at="periods",
            notifier=notifications.append,
        )

    assert notifications == []


@pytest.mark.parametrize(
    "failure_step",
    [
        "atenciones_previous",
        "atenciones_current",
        "agendamientos_previous",
        "agendamientos_current",
    ],
)
def test_every_processing_failure_notifies_then_aborts(
    tmp_path: Path, failure_step: str
) -> None:
    notifications: list[dict[str, str]] = []

    with pytest.raises(PipelineExecutionError) as caught:
        run_pipeline(
            "2026-07-15",
            FIXTURES_DIR,
            tmp_path,
            fail_at=failure_step,
            notifier=notifications.append,
        )

    assert caught.value.step == failure_step
    assert notifications[0]["step"] == failure_step


def test_validate_failure_aborts_without_notification(tmp_path: Path) -> None:
    notifications: list[dict[str, str]] = []

    with pytest.raises(PipelineExecutionError) as caught:
        run_pipeline(
            "2026-07-15",
            FIXTURES_DIR,
            tmp_path,
            fail_at="validate",
            notifier=notifications.append,
        )

    assert caught.value.step == "validate"
    assert notifications == []


def test_unknown_failure_stage_is_rejected_before_work(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="unsupported fail_at"):
        run_pipeline(
            "2026-07-15",
            FIXTURES_DIR,
            tmp_path,
            fail_at="typo",
        )

    assert list(tmp_path.iterdir()) == []


def test_notification_callback_failure_preserves_processing_failure(
    tmp_path: Path,
) -> None:
    def broken_notifier(_: dict[str, str]) -> None:
        raise OSError("mock notification sink unavailable")

    with pytest.raises(PipelineExecutionError) as caught:
        run_pipeline(
            "2026-07-15",
            FIXTURES_DIR,
            tmp_path,
            fail_at="atenciones_previous",
            notifier=broken_notifier,
        )

    assert caught.value.step == "atenciones_previous"
    assert caught.value.notification_error == "mock notification sink unavailable"


def test_source_header_must_match_exact_schema_and_order(tmp_path: Path) -> None:
    fixture_dir = tmp_path / "fixtures"
    fields = list(ATENCIONES_SOURCE_FIELDS)
    fields[0], fields[1] = fields[1], fields[0]
    path = fixture_dir / "202606" / "AtencionesZeroQ_202606.csv"
    path.parent.mkdir(parents=True)
    path.write_text(";".join(fields) + "\n", encoding="iso-8859-1")

    with pytest.raises(ValueError, match="header"):
        process_atenciones("202606", fixture_dir, tmp_path / "output")


@pytest.mark.parametrize("row_suffix", ["", ";unexpected"])
def test_source_row_width_must_match_schema(
    tmp_path: Path, row_suffix: str
) -> None:
    fixture_dir = tmp_path / "fixtures"
    path = fixture_dir / "202606" / "AtencionesZeroQ_202606.csv"
    path.parent.mkdir(parents=True)
    values = ["T-1"] if not row_suffix else [""] * len(ATENCIONES_SOURCE_FIELDS)
    path.write_text(
        ";".join(ATENCIONES_SOURCE_FIELDS)
        + "\n"
        + ";".join(values)
        + row_suffix
        + "\n",
        encoding="iso-8859-1",
    )

    with pytest.raises(ValueError, match="row 2"):
        process_atenciones("202606", fixture_dir, tmp_path / "output")


def test_zero_row_sources_produce_valid_empty_outputs(tmp_path: Path) -> None:
    fixture_dir = tmp_path / "fixtures"
    for period in ("202606", "202607"):
        _write_source(
            fixture_dir,
            period,
            f"AtencionesZeroQ_{period}.csv",
            ATENCIONES_SOURCE_FIELDS,
            [],
        )
        _write_source(
            fixture_dir,
            period,
            f"AgendamientoZeroQ_{period}.csv",
            AGENDAMIENTOS_SOURCE_FIELDS,
            [],
        )

    result = run_pipeline("2026-07-15", fixture_dir, tmp_path / "output")

    assert result["status"] == "SUCCEEDED"
    assert all(
        (tmp_path / "output" / relative_path).read_bytes() == b""
        for relative_path in result["outputs"]
    )


def test_output_is_byte_exact_pentaho_format(tmp_path: Path) -> None:
    fixture_dir = tmp_path / "fixtures"
    with (
        FIXTURES_DIR.joinpath(
            "202606", "AtencionesZeroQ_202606.csv"
        ).open(encoding="iso-8859-1", newline="") as stream
    ):
        row = next(csv.DictReader(stream, delimiter=";"))
    row["Oficina"] = "Ñuñoa"
    _write_source(
        fixture_dir,
        "202606",
        "AtencionesZeroQ_202606.csv",
        ATENCIONES_SOURCE_FIELDS,
        [row],
    )

    process_atenciones("202606", fixture_dir, tmp_path / "output")
    payload = (
        tmp_path / "output" / "202606" / "AtencionesZeroQ.csv"
    ).read_bytes()
    expected_values = [
        "20260601",
        "T-202606",
        "CALL-202606",
        "10",
        "101",
        "Ñuñoa",
        "20",
        "Atencion",
        "30",
        "A",
        "4",
        "12345678-9",
        "Ada Mock",
        "20260618",
        "A",
        "42",
        "9.876.543-2",
        "1",
        "Afiliado",
        "Cliente Junio",
        "cliente.junio@example.test",
        "09:00:00",
        "09:02:00",
        "09:12:00",
        "00:02:00",
        "00:10:00",
        "N",
        "N",
        "Sucursal",
        "Presencial",
    ]
    assert len(expected_values) == len(ATENCIONES_BASE_FIELDS)
    assert payload == ("~|".join(expected_values) + "\n").encode("iso-8859-1")
    assert b"\r" not in payload


@pytest.mark.parametrize("unsafe_value", ["Ada~|Mock", "Ada\nMock", "Ada\rMock"])
def test_output_rejects_separator_and_line_injection(
    tmp_path: Path, unsafe_value: str
) -> None:
    fixture_dir = tmp_path / "fixtures"
    with (
        FIXTURES_DIR.joinpath(
            "202606", "AtencionesZeroQ_202606.csv"
        ).open(encoding="iso-8859-1", newline="") as stream
    ):
        row = next(csv.DictReader(stream, delimiter=";"))
    row["Nombre_Ejecutivo"] = unsafe_value
    _write_source(
        fixture_dir,
        "202606",
        "AtencionesZeroQ_202606.csv",
        ATENCIONES_SOURCE_FIELDS,
        [row],
    )

    with pytest.raises(ValueError, match="separator|line break"):
        process_atenciones("202606", fixture_dir, tmp_path / "output")
