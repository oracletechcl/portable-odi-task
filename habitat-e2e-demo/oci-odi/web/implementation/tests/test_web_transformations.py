from __future__ import annotations

from datetime import datetime

import pytest

from habitat_web.transformations import (
    DATASET_CONTRACTS,
    ContractError,
    render_dataset,
    transform_configuracion_equipo_usuario,
)


def test_contracts_cover_all_seven_source_transformations() -> None:
    assert tuple(DATASET_CONTRACTS) == (
        "CONFIGURACION_EQUIPO_MESA",
        "CONFIGURACION_EQUIPO_USUARIO",
        "OPC_OPCION",
        "SEC_SECCION",
        "SUB_SUBSECCION",
        "TB_LOG_SISTEMA",
        "TB_SUB_SISTEMA_SERVICIO",
    )


def test_render_dataset_preserves_order_delimiter_encoding_and_lf() -> None:
    row = {
        "SEC_DEFAULT": 0,
        "SEC_NOMBRE_EXTRA": "Configuración",
        "SEC_ORDEN": 2,
        "SEC_NOMBRE": "Atención",
        "SEC_MEN_ID": 10,
        "SEC_ID": 7,
    }

    rendered = render_dataset("SEC_SECCION", [row])

    assert rendered == (
        "7~|10~|Atención~|2~|Configuración~|0\n".encode("iso-8859-1")
    )
    assert not rendered.startswith(b"SEC_ID")


def test_render_dataset_preserves_zero_rows() -> None:
    assert render_dataset("OPC_OPCION", []) == b""


def test_render_dataset_rejects_missing_contract_fields() -> None:
    with pytest.raises(ContractError, match="missing fields"):
        render_dataset("SUB_SUBSECCION", [{"SUB_ID": 1}])


def test_usuario_transformation_recovers_period_and_session_timestamp() -> None:
    source = {
        "NombreTablet": "TAB-01",
        "Usuario": "user-01",
        "InicioSesion": "25-07-2026",
        "HoraSesion1Str": "08:09:10,123",
        "HoraSesion2Str": "",
    }

    actual = transform_configuracion_equipo_usuario(
        source,
        source_filename="bi_TAMAB_01-07-2026.txt",
        now=datetime(2026, 7, 25, 12, 30, 0),
        audit_user="migration",
    )

    assert actual["fechaCierre"] == datetime(2026, 7, 1)
    assert actual["FechaHoraSesion"] == datetime(2026, 7, 25, 8, 9, 10)
    assert actual["FechaCreacion"] == datetime(2026, 7, 25, 12, 30, 0)
    assert actual["AUD_CREADO_POR"] == "migration"
    assert actual["FEC_INI_RELOJ"] is None
    assert actual["FEC_FIN_RELOJ"] is None
    assert actual["FEC_FIN_TABLET"] is None


def test_usuario_transformation_falls_back_to_second_session_time() -> None:
    actual = transform_configuracion_equipo_usuario(
        {
            "NombreTablet": "TAB-02",
            "Usuario": "user-02",
            "InicioSesion": "25-07-2026",
            "HoraSesion1Str": "",
            "HoraSesion2Str": "18:19:20,456",
        },
        source_filename="bi_TAMXY_31-07-2026.txt",
        now=datetime(2026, 7, 25, 12, 30, 0),
        audit_user="migration",
    )

    assert actual["FechaHoraSesion"] == datetime(2026, 7, 25, 18, 19, 20)


@pytest.mark.parametrize(
    "filename",
    ("unexpected.txt", "bi_TAMAB_2026-07-01.txt", "../bi_TAMAB_01-07-2026.txt"),
)
def test_usuario_transformation_rejects_malformed_or_unsafe_filename(
    filename: str,
) -> None:
    with pytest.raises(ContractError, match="source filename"):
        transform_configuracion_equipo_usuario(
            {
                "NombreTablet": "TAB-01",
                "Usuario": "user-01",
                "InicioSesion": "25-07-2026",
                "HoraSesion1Str": "08:09:10,123",
                "HoraSesion2Str": "",
            },
            source_filename=filename,
            now=datetime(2026, 7, 25, 12, 30, 0),
            audit_user="migration",
        )
