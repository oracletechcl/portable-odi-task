"""Pure equivalents of the evidenced Sucursales Pentaho transformations."""
from __future__ import annotations
from datetime import datetime, timedelta
from collections.abc import Iterable, Mapping

def periods(as_of_date: str) -> dict[str, str]:
    current = datetime.strptime(as_of_date, "%Y-%m-%d").date().replace(day=1)
    previous = (current - timedelta(days=1)).replace(day=1)
    return {"previous": previous.strftime("%Y%m"), "current": current.strftime("%Y%m")}

def transform_base(rows: Iterable[Mapping[str, object]], period: str) -> list[dict[str, object]]:
    datetime.strptime(period, "%Y%m")
    return [{**row, "DNI_Ejecutivo": str(row.get("DNI_Ejecutivo", "")).replace(".", ""), "fechaCierre": period + "01"} for row in rows]

def transform_motivos(rows: Iterable[Mapping[str, object]], period: str, key: str) -> list[dict[str, object]]:
    datetime.strptime(period, "%Y%m"); result = []
    for row in rows:
        ids = [] if not row.get("ID_Motivos") else [x.strip() for x in str(row["ID_Motivos"]).split(",")]
        texts = [] if not row.get("Motivo_Atencion") else [x.strip() for x in str(row["Motivo_Atencion"]).split(",")]
        if len(ids) != len(texts): raise ValueError("motivo ID and description ordinal counts differ")
        for identifier, description in zip(ids, texts, strict=True):
            motive, _, submotive = identifier.partition("$"); label, _, sublabel = description.partition("$")
            result.append({"fechaCierre": period + "01", key: row.get(key, ""), "IDMotivoAtencion": motive, "DescMotivoAtencion": label, "IDSubMotivoAtencion": submotive, "DescSubMotivoAtencion": sublabel})
    return result
