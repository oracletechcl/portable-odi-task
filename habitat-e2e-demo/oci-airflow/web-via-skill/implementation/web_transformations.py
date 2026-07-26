"""Pure, source-traceable Web flat-file transformation contracts."""
from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from datetime import date, datetime


class ContractError(ValueError):
    pass


@dataclass(frozen=True)
class Field:
    name: str
    kind: str = "string"
    fmt: str | None = None
    null: str = ""


@dataclass(frozen=True)
class DatasetContract:
    fields: tuple[Field, ...]
    separator: str = "~|"
    encoding: str = "iso-8859-1"


def _fields(*items: Field) -> DatasetContract:
    return DatasetContract(items)


# Field order, delimiter, encoding, and null dates recover the seven KTR outputs.
DATASET_CONTRACTS = {
    "CONFIGURACION_EQUIPO_MESA": _fields(Field("ip_xls"), Field("equipo_xls"), Field("mesa_xls", "integer"), Field("codigoSucursal_xls", "integer"), Field("sucursal_xls"), Field("audpor_xls"), Field("audcreac_xls", "date", "%Y%m%d%H%M%S", "00000000000000"), Field("audmod_xls"), Field("audfecmod_xls", "date", "%Y%m%d%H%M%S", "00000000000000")),
    "CONFIGURACION_EQUIPO_USUARIO": _fields(Field("NombreTablet"), Field("Usuario"), Field("FEC_INI_RELOJ", "date", "%Y%m%d%H%M%S", "00000000000000"), Field("FechaHoraSesion", "date", "%Y%m%d%H%M%S", "00000000000000"), Field("FEC_FIN_RELOJ", "date", "%Y%m%d%H%M%S", "00000000000000"), Field("FEC_FIN_TABLET", "date", "%Y%m%d%H%M%S", "00000000000000"), Field("AUD_CREADO_POR"), Field("FechaCreacion", "date", "%Y%m%d%H%M%S", "00000000000000"), Field("AUD_MODIF_POR"), Field("AUD_FEC_MODIF", "date", "%Y%m%d%H%M%S", "00000000000000")),
    "OPC_OPCION": _fields(*[Field(name, "integer" if name in {"OPC_ID", "OPC_SUB_ID", "OPC_ORDEN"} else "string") for name in ("OPC_ID", "OPC_SUB_ID", "OPC_NOMBRE", "OPC_URL", "OPC_ORDEN", "OPC_ROLES", "OPC_DEFAULT", "OPC_EXPANDIDO", "OPC_ACTIVO", "OPC_VISIBLE", "OPC_ALIAS", "OPC_TIENE_INFO_CLI", "OPC_COD_SUPER")]),
    "SEC_SECCION": _fields(Field("SEC_ID", "integer"), Field("SEC_MEN_ID", "integer"), Field("SEC_NOMBRE"), Field("SEC_ORDEN", "integer"), Field("SEC_NOMBRE_EXTRA"), Field("SEC_DEFAULT", "integer")),
    "SUB_SUBSECCION": _fields(Field("SUB_ID", "integer"), Field("SUB_SEC_ID", "integer"), Field("SUB_NOMBRE"), Field("SUB_ORDEN", "integer"), Field("SUB_DEFAULT", "integer")),
    "TB_LOG_SISTEMA": _fields(Field("fechaCierre", "date", "%Y%m%d"), Field("ID_LOG", "number"), Field("CODIGO_SISTEMA", "integer"), Field("CODIGO_OPERACION", "integer"), Field("USUARIO"), Field("RUT", "integer"), Field("DV"), Field("FECHAHORA", "date", "%Y%m%d%H%M%S", "00000000000000"), Field("SUCURSAL", "integer"), Field("CANAL"), Field("MODULO"), Field("DATOS2"), Field("URL"), Field("EXITO", "integer"), Field("UUID")),
    "TB_SUB_SISTEMA_SERVICIO": _fields(Field("ID_SUB_SISTEMA", "integer"), Field("ID_SERVICIO", "integer"), Field("FECINI", "integer"), Field("ID_CLASE_SERVICIO", "integer"), Field("ID_TIPO_OPERACION"), Field("ID_NIVEL_SEGURIDAD"), Field("ID_TIPO_SERVICIO"), Field("DESCRIPCION"), Field("COD_OPER_TERMINAL", "integer"), Field("CODIGO_SERVICIO"), Field("OPC_COD_SUPER"), Field("COD_OPER_ERROR", "integer")),
}


def _format(field: Field, value: object) -> str:
    if value is None or (value == "" and field.kind != "string"):
        return field.null
    if field.kind == "date":
        if isinstance(value, str):
            for pattern in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
                try:
                    value = datetime.strptime(value, pattern)
                    break
                except ValueError:
                    pass
            else:
                raise ContractError(f"{field.name}: invalid date")
        if isinstance(value, date) and not isinstance(value, datetime):
            value = datetime.combine(value, datetime.min.time())
        if not isinstance(value, datetime):
            raise ContractError(f"{field.name}: expected date")
        return value.strftime(field.fmt or "%Y%m%d%H%M%S")
    if field.kind == "integer":
        if isinstance(value, bool):
            raise ContractError(f"{field.name}: expected integer")
        try:
            return str(int(value))
        except (TypeError, ValueError) as exc:
            raise ContractError(f"{field.name}: expected integer") from exc
    if field.kind == "number":
        try:
            number = float(value)
        except (TypeError, ValueError) as exc:
            raise ContractError(f"{field.name}: expected number") from exc
        return str(int(number)) if number.is_integer() else str(number)
    return str(value)


def render_dataset(dataset: str, rows: Iterable[Mapping[str, object]]) -> bytes:
    try:
        contract = DATASET_CONTRACTS[dataset]
    except KeyError as exc:
        raise ContractError(f"unknown dataset: {dataset}") from exc
    output = []
    for number, row in enumerate(rows, 1):
        missing = [field.name for field in contract.fields if field.name not in row]
        if missing:
            raise ContractError(f"{dataset} row {number} missing fields: {', '.join(missing)}")
        output.append(contract.separator.join(_format(field, row[field.name]) for field in contract.fields) + "\n")
    try:
        return "".join(output).encode(contract.encoding)
    except UnicodeEncodeError as exc:
        raise ContractError(f"{dataset}: non ISO-8859-1 value") from exc
