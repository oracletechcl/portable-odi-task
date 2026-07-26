"""Pure-Python equivalents of the five Pentaho Sucursales transformations."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from datetime import datetime
from typing import Any

from .contracts import (
    AGENDAMIENTOS_BASE_FIELDS,
    AGENDAMIENTOS_DATE_FIELDS,
    AGENDAMIENTOS_INTEGER_FIELDS,
    AGENDAMIENTOS_MOTIVO_FIELDS,
    AGENDAMIENTOS_TIME_FIELDS,
    ATENCIONES_BASE_FIELDS,
    ATENCIONES_DATE_FIELDS,
    ATENCIONES_INTEGER_FIELDS,
    ATENCIONES_MOTIVO_FIELDS,
    ATENCIONES_TIME_FIELDS,
)

Row = Mapping[str, Any]
TransformedRow = dict[str, Any]


def transform_atenciones_base(
    rows: Iterable[Row], period: str
) -> list[TransformedRow]:
    return _transform_base(
        rows,
        period,
        ATENCIONES_BASE_FIELDS,
        ATENCIONES_DATE_FIELDS,
        ATENCIONES_INTEGER_FIELDS,
        ATENCIONES_TIME_FIELDS,
    )


def transform_agendamientos_base(
    rows: Iterable[Row], period: str
) -> list[TransformedRow]:
    return _transform_base(
        rows,
        period,
        AGENDAMIENTOS_BASE_FIELDS,
        AGENDAMIENTOS_DATE_FIELDS,
        AGENDAMIENTOS_INTEGER_FIELDS,
        AGENDAMIENTOS_TIME_FIELDS,
    )


def transform_atenciones_motivos(
    rows: Iterable[Row], period: str
) -> list[TransformedRow]:
    return _transform_motivos(
        rows,
        period,
        id_field="ID_Ticket",
        output_fields=ATENCIONES_MOTIVO_FIELDS,
    )


def transform_agendamientos_motivos(
    rows: Iterable[Row], period: str
) -> list[TransformedRow]:
    return _transform_motivos(
        rows,
        period,
        id_field="ID_Reserva",
        output_fields=AGENDAMIENTOS_MOTIVO_FIELDS,
    )


def _transform_base(
    rows: Iterable[Row],
    period: str,
    output_fields: tuple[str, ...],
    date_fields: tuple[str, ...],
    integer_fields: tuple[str, ...],
    time_fields: tuple[str, ...],
) -> list[TransformedRow]:
    closing_date = _closing_date(period)
    transformed: list[TransformedRow] = []
    for source in rows:
        normalized = dict(source)
        normalized["fechaCierre"] = closing_date
        normalized["DNI_Ejecutivo"] = str(
            normalized.get("DNI_Ejecutivo", "")
        ).replace(".", "")
        for field in date_fields:
            normalized[field] = _compact_date(normalized.get(field, ""), field)
        for field in integer_fields:
            normalized[field] = _optional_integer(
                normalized.get(field, ""), field
            )
        for field in time_fields:
            normalized[field] = _validated_time(
                normalized.get(field, ""), field
            )
        transformed.append(
            {field: normalized.get(field, "") for field in output_fields}
        )
    return transformed


def _transform_motivos(
    rows: Iterable[Row],
    period: str,
    id_field: str,
    output_fields: tuple[str, ...],
) -> list[TransformedRow]:
    closing_date = _closing_date(period)
    transformed: list[TransformedRow] = []
    for source in rows:
        ids = _split_list(source.get("ID_Motivos", ""))
        descriptions = _split_list(source.get("Motivo_Atencion", ""))
        if len(ids) != len(descriptions):
            raise ValueError(
                "ID_Motivos and Motivo_Atencion must contain the same number "
                "of ordinal entries"
            )
        for id_value, description_value in zip(ids, descriptions, strict=True):
            motivo_id, submotivo_id = _split_hierarchy(id_value)
            motivo_description, submotivo_description = _split_hierarchy(
                description_value
            )
            expanded = {
                "fechaCierre": closing_date,
                id_field: source.get(id_field, ""),
                "ID_Llamada": source.get("ID_Llamada", ""),
                "ID_Oficina": _optional_integer(
                    source.get("ID_Oficina", ""), "ID_Oficina"
                ),
                "ID_Serie": _optional_integer(
                    source.get("ID_Serie", ""), "ID_Serie"
                ),
                "IDMotivoAtencion": _optional_integer(
                    motivo_id, "IDMotivoAtencion"
                ),
                "DescMotivoAtencion": motivo_description,
                "IDSubMotivoAtencion": _optional_integer(
                    submotivo_id, "IDSubMotivoAtencion"
                ),
                "DescSubMotivoAtencion": submotivo_description,
            }
            transformed.append(
                {field: expanded.get(field, "") for field in output_fields}
            )
    return transformed


def _closing_date(period: str) -> str:
    if len(period) != 6 or not period.isdigit():
        raise ValueError("period must use YYYYMM")
    try:
        datetime.strptime(period, "%Y%m")
    except ValueError as exc:
        raise ValueError("period must be a valid YYYYMM calendar month") from exc
    return f"{period}01"


def _compact_date(value: Any, field: str) -> str:
    text = "" if value is None else str(value).strip()
    if not text:
        return ""
    for date_format in ("%Y-%m-%d", "%Y%m%d"):
        try:
            return datetime.strptime(text, date_format).strftime("%Y%m%d")
        except ValueError:
            continue
    raise ValueError(f"{field} must use YYYY-MM-DD: {text!r}")


def _split_list(value: Any) -> list[str]:
    text = "" if value is None else str(value)
    if not text:
        return []
    return [part.strip() for part in text.split(",")]


def _split_hierarchy(value: str) -> tuple[str, str]:
    parent, separator, child = value.partition("$")
    return parent.strip(), child.strip() if separator else ""


def _optional_integer(value: Any, field: str) -> int | None:
    text = "" if value is None else str(value).strip()
    if not text:
        return None
    try:
        return int(text)
    except ValueError as exc:
        raise ValueError(f"{field} must be an integer: {text!r}") from exc


def _validated_time(value: Any, field: str) -> str:
    text = "" if value is None else str(value).strip()
    if not text:
        return ""
    try:
        parsed = datetime.strptime(text, "%H:%M:%S")
    except ValueError as exc:
        raise ValueError(f"{field} must use HH:mm:ss: {text!r}") from exc
    if len(text) != 8:
        raise ValueError(f"{field} must use HH:mm:ss: {text!r}")
    return parsed.strftime("%H:%M:%S")
