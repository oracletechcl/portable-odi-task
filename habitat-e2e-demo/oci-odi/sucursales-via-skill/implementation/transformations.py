"""Pure Python equivalents of the evidenced Pentaho field operations."""
from __future__ import annotations

from collections.abc import Iterable, Mapping
from datetime import datetime


def calculate_periods(as_of_date: str) -> dict[str, str]:
    current = datetime.strptime(as_of_date, "%Y-%m-%d").date().replace(day=1)
    previous = current.replace(day=1).fromordinal(current.toordinal() - 1).replace(day=1)
    return {"previous": previous.strftime("%Y%m"), "current": current.strftime("%Y%m")}


def transform_base(rows: Iterable[Mapping[str, object]], period: str) -> list[dict[str, object]]:
    """Implements Replace puntos en rutEjecutivo and Obtiene Fecha Cierre."""
    datetime.strptime(period, "%Y%m")
    output = []
    for row in rows:
        transformed = dict(row)
        transformed["fechaCierre"] = period + "01"
        transformed["DNI_Ejecutivo"] = str(transformed.get("DNI_Ejecutivo", "")).replace(".", "")
        output.append(transformed)
    return output


def transform_motivos(rows: Iterable[Mapping[str, object]], period: str, record_field: str) -> list[dict[str, object]]:
    """Implements paired SplitFieldToRows3, FieldSplitter and StreamLookup steps."""
    datetime.strptime(period, "%Y%m")
    output = []
    for row in rows:
        ids = [] if not row.get("ID_Motivos") else [v.strip() for v in str(row["ID_Motivos"]).split(",")]
        descriptions = [] if not row.get("Motivo_Atencion") else [v.strip() for v in str(row["Motivo_Atencion"]).split(",")]
        if len(ids) != len(descriptions):
            raise ValueError("ID_Motivos and Motivo_Atencion ordinal counts differ")
        for motive_id, description in zip(ids, descriptions, strict=True):
            parent_id, _, child_id = motive_id.partition("$")
            parent_text, _, child_text = description.partition("$")
            output.append({"fechaCierre": period + "01", record_field: row.get(record_field, ""), "ID_Llamada": row.get("ID_Llamada", ""), "ID_Oficina": row.get("ID_Oficina", ""), "ID_Serie": row.get("ID_Serie", ""), "IDMotivoAtencion": parent_id, "DescMotivoAtencion": parent_text, "IDSubMotivoAtencion": child_id, "DescSubMotivoAtencion": child_text})
    return output
