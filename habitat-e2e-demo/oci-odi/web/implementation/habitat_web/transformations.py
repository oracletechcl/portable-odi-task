from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date, datetime
from typing import Iterable, Mapping


class ContractError(ValueError):
    """Raised when source or boundary data violates the recovered Pentaho contract."""


@dataclass(frozen=True)
class Field:
    name: str
    kind: str = "string"
    format: str | None = None
    null_value: str = ""


@dataclass(frozen=True)
class DatasetContract:
    fields: tuple[str, ...]
    definitions: tuple[Field, ...]
    separator: str = "~|"
    encoding: str = "iso-8859-1"
    newline: str = "\n"


def _contract(*fields: Field) -> DatasetContract:
    return DatasetContract(
        fields=tuple(field.name for field in fields),
        definitions=tuple(fields),
    )


DATASET_CONTRACTS: dict[str, DatasetContract] = {
    "CONFIGURACION_EQUIPO_MESA": _contract(
        Field("ip_xls"),
        Field("equipo_xls"),
        Field("mesa_xls", "integer"),
        Field("codigoSucursal_xls", "integer"),
        Field("sucursal_xls"),
        Field("audpor_xls"),
        Field("audcreac_xls", "date", "%Y%m%d%H%M%S", "00000000000000"),
        Field("audmod_xls"),
        Field("audfecmod_xls", "date", "%Y%m%d%H%M%S", "00000000000000"),
    ),
    "CONFIGURACION_EQUIPO_USUARIO": _contract(
        Field("NombreTablet"),
        Field("Usuario"),
        Field("FEC_INI_RELOJ", "date", "%Y%m%d%H%M%S", "00000000000000"),
        Field("FechaHoraSesion", "date", "%Y%m%d%H%M%S", "00000000000000"),
        Field("FEC_FIN_RELOJ", "date", "%Y%m%d%H%M%S", "00000000000000"),
        Field("FEC_FIN_TABLET", "date", "%Y%m%d%H%M%S", "00000000000000"),
        Field("AUD_CREADO_POR"),
        Field("FechaCreacion", "date", "%Y%m%d%H%M%S", "00000000000000"),
        Field("AUD_MODIF_POR"),
        Field("AUD_FEC_MODIF", "date", "%Y%m%d%H%M%S", "00000000000000"),
    ),
    "OPC_OPCION": _contract(
        Field("OPC_ID", "integer"),
        Field("OPC_SUB_ID", "integer"),
        Field("OPC_NOMBRE"),
        Field("OPC_URL"),
        Field("OPC_ORDEN", "integer"),
        Field("OPC_ROLES"),
        Field("OPC_DEFAULT"),
        Field("OPC_EXPANDIDO"),
        Field("OPC_ACTIVO"),
        Field("OPC_VISIBLE"),
        Field("OPC_ALIAS"),
        Field("OPC_TIENE_INFO_CLI"),
        Field("OPC_COD_SUPER"),
    ),
    "SEC_SECCION": _contract(
        Field("SEC_ID", "integer"),
        Field("SEC_MEN_ID", "integer"),
        Field("SEC_NOMBRE"),
        Field("SEC_ORDEN", "integer"),
        Field("SEC_NOMBRE_EXTRA"),
        Field("SEC_DEFAULT", "integer"),
    ),
    "SUB_SUBSECCION": _contract(
        Field("SUB_ID", "integer"),
        Field("SUB_SEC_ID", "integer"),
        Field("SUB_NOMBRE"),
        Field("SUB_ORDEN", "integer"),
        Field("SUB_DEFAULT", "integer"),
    ),
    "TB_LOG_SISTEMA": _contract(
        Field("fechaCierre", "date", "%Y%m%d"),
        Field("ID_LOG", "number"),
        Field("CODIGO_SISTEMA", "integer"),
        Field("CODIGO_OPERACION", "integer"),
        Field("USUARIO"),
        Field("RUT", "integer"),
        Field("DV"),
        Field("FECHAHORA", "date", "%Y%m%d%H%M%S", "00000000000000"),
        Field("SUCURSAL", "integer"),
        Field("CANAL"),
        Field("MODULO"),
        Field("DATOS2"),
        Field("URL"),
        Field("EXITO", "integer"),
        Field("UUID"),
    ),
    "TB_SUB_SISTEMA_SERVICIO": _contract(
        Field("ID_SUB_SISTEMA", "integer"),
        Field("ID_SERVICIO", "integer"),
        Field("FECINI", "integer"),
        Field("ID_CLASE_SERVICIO", "integer"),
        Field("ID_TIPO_OPERACION"),
        Field("ID_NIVEL_SEGURIDAD"),
        Field("ID_TIPO_SERVICIO"),
        Field("DESCRIPCION"),
        Field("COD_OPER_TERMINAL", "integer"),
        Field("CODIGO_SERVICIO"),
        Field("OPC_COD_SUPER"),
        Field("COD_OPER_ERROR", "integer"),
    ),
}


def _format_value(field: Field, value: object) -> str:
    if value is None or (value == "" and field.kind != "string"):
        return field.null_value
    if field.kind == "date":
        if isinstance(value, str):
            accepted = ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d")
            parsed: datetime | None = None
            for pattern in accepted:
                try:
                    parsed = datetime.strptime(value, pattern)
                    break
                except ValueError:
                    continue
            if parsed is None:
                raise ContractError(f"{field.name}: invalid date value")
            value = parsed
        if isinstance(value, date) and not isinstance(value, datetime):
            value = datetime.combine(value, datetime.min.time())
        if not isinstance(value, datetime):
            raise ContractError(f"{field.name}: expected date")
        return value.strftime(field.format or "%Y%m%d%H%M%S")
    if field.kind == "integer":
        if isinstance(value, bool):
            raise ContractError(f"{field.name}: expected integer")
        try:
            return str(int(value))
        except (TypeError, ValueError) as exc:
            raise ContractError(f"{field.name}: expected integer") from exc
    if field.kind == "number":
        if isinstance(value, bool):
            raise ContractError(f"{field.name}: expected number")
        try:
            number = float(value)
        except (TypeError, ValueError) as exc:
            raise ContractError(f"{field.name}: expected number") from exc
        return str(int(number)) if number.is_integer() else format(number, "f").rstrip("0").rstrip(".")
    return str(value)


def render_dataset(
    dataset: str,
    rows: Iterable[Mapping[str, object]],
) -> bytes:
    try:
        contract = DATASET_CONTRACTS[dataset]
    except KeyError as exc:
        raise ContractError(f"unknown dataset: {dataset}") from exc

    output: list[str] = []
    for row_number, row in enumerate(rows, start=1):
        missing = [field for field in contract.fields if field not in row]
        if missing:
            raise ContractError(
                f"{dataset} row {row_number} missing fields: {', '.join(missing)}"
            )
        values = [
            _format_value(field, row[field.name]) for field in contract.definitions
        ]
        output.append(contract.separator.join(values) + contract.newline)
    try:
        return "".join(output).encode(contract.encoding)
    except UnicodeEncodeError as exc:
        raise ContractError(f"{dataset}: value is not ISO-8859-1 encodable") from exc


_SOURCE_FILENAME = re.compile(
    r"^bi_[A-Z]{5}_(?P<day>[0-9]{2})-(?P<month>[0-9]{2})-"
    r"(?P<year>[0-9]{4})\.txt$"
)


def _parse_session_time(value: object) -> tuple[int, int, int] | None:
    text = str(value or "").strip()
    if not text:
        return None
    match = re.fullmatch(r"([0-9]{2}):([0-9]{2}):([0-9]{2})(?:,[0-9]+)?", text)
    if not match:
        raise ContractError("invalid session time")
    hour, minute, second = (int(part) for part in match.groups())
    try:
        datetime(2000, 1, 1, hour, minute, second)
    except ValueError as exc:
        raise ContractError("invalid session time") from exc
    return hour, minute, second


def transform_configuracion_equipo_usuario(
    row: Mapping[str, object],
    *,
    source_filename: str,
    now: datetime,
    audit_user: str,
) -> dict[str, object]:
    if "/" in source_filename or "\\" in source_filename:
        raise ContractError("invalid source filename")
    filename_match = _SOURCE_FILENAME.fullmatch(source_filename)
    if filename_match is None:
        raise ContractError("invalid source filename")

    try:
        fecha_cierre = datetime(
            int(filename_match.group("year")),
            int(filename_match.group("month")),
            1,
        )
        session_date = datetime.strptime(str(row["InicioSesion"]), "%d-%m-%Y")
    except (KeyError, ValueError) as exc:
        raise ContractError("invalid source filename or session date") from exc

    time_parts = _parse_session_time(row.get("HoraSesion1Str"))
    if time_parts is None:
        time_parts = _parse_session_time(row.get("HoraSesion2Str"))
    if time_parts is None:
        raise ContractError("both session times are empty")
    session = session_date.replace(
        hour=time_parts[0], minute=time_parts[1], second=time_parts[2]
    )

    return {
        "NombreTablet": row.get("NombreTablet", ""),
        "Usuario": row.get("Usuario", ""),
        "FEC_INI_RELOJ": None,
        "FechaHoraSesion": session,
        "FEC_FIN_RELOJ": None,
        "FEC_FIN_TABLET": None,
        "AUD_CREADO_POR": audit_user,
        "FechaCreacion": now,
        "AUD_MODIF_POR": "",
        "AUD_FEC_MODIF": None,
        "fechaCierre": fecha_cierre,
    }
