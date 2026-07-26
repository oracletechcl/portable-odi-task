import pytest

from habitat_sucursales.transformations import (
    transform_agendamientos_base,
    transform_agendamientos_motivos,
    transform_atenciones_base,
    transform_atenciones_motivos,
)


def test_atenciones_base_preserves_contract_and_normalizes_rut() -> None:
    row = {
        "ID_Ticket": "T-100",
        "ID_Llamada": "CALL-100",
        "ID_Oficina": "10",
        "Codigo_de_Oficina": "101",
        "Oficina": "Providencia",
        "ID_Serie": "20",
        "Serie": "Atencion",
        "ID_Linea": "30",
        "Fila": "A",
        "Modulo": "4",
        "DNI_Ejecutivo": "12.345.678-9",
        "Nombre_Ejecutivo": "Ada",
        "Fecha": "2026-06-18",
        "Prefijo_Ticket": "A",
        "Nro._Ticket": "42",
        "DNI_Cliente": "9.876.543-2",
        "ID_Tipo_Cliente": "1",
        "Tipo_Cliente": "Afiliado",
        "Nombre_Cliente": "Cliente Uno",
        "Email_Cliente": "cliente@example.test",
        "Hora_Emision_Ticket": "09:00:00",
        "Hora_Inicio_Atencion": "09:02:00",
        "Hora_Termino_Atencion": "09:12:00",
        "Tiempo_Espera": "00:02:00",
        "Tiempo_Atencion": "00:10:00",
        "ID_Motivos": "101$1001,202$2002",
        "Motivo_Atencion": "Consulta$Cartola,Pago$Cheque",
        "Perdido": "N",
        "Saltado": "N",
        "Formulario": "Sucursal",
        "Modo_de_Atencion": "Presencial",
    }

    transformed = transform_atenciones_base([row], "202606")

    assert transformed[0]["fechaCierre"] == "20260601"
    assert transformed[0]["DNI_Ejecutivo"] == "12345678-9"
    assert transformed[0]["Fecha"] == "20260618"
    assert "ID_Motivos" not in transformed[0]
    assert "Motivo_Atencion" not in transformed[0]
    assert list(transformed[0])[:3] == ["fechaCierre", "ID_Ticket", "ID_Llamada"]


def test_atenciones_motivos_expands_paired_hierarchy_by_ordinal() -> None:
    row = {
        "ID_Ticket": "T-100",
        "ID_Llamada": "CALL-100",
        "ID_Oficina": "10",
        "ID_Serie": "20",
        "ID_Motivos": "101$1001,202$2002",
        "Motivo_Atencion": "Consulta$Cartola,Pago$Cheque",
    }

    transformed = transform_atenciones_motivos([row], "202606")

    assert transformed == [
        {
            "fechaCierre": "20260601",
            "ID_Ticket": "T-100",
            "ID_Llamada": "CALL-100",
            "ID_Oficina": 10,
            "ID_Serie": 20,
            "IDMotivoAtencion": 101,
            "DescMotivoAtencion": "Consulta",
            "IDSubMotivoAtencion": 1001,
            "DescSubMotivoAtencion": "Cartola",
        },
        {
            "fechaCierre": "20260601",
            "ID_Ticket": "T-100",
            "ID_Llamada": "CALL-100",
            "ID_Oficina": 10,
            "ID_Serie": 20,
            "IDMotivoAtencion": 202,
            "DescMotivoAtencion": "Pago",
            "IDSubMotivoAtencion": 2002,
            "DescSubMotivoAtencion": "Cheque",
        },
    ]


def test_agendamientos_base_and_motivos_follow_same_contract() -> None:
    row = {
        "ID_Reserva": "R-200",
        "ID_Llamada": "CALL-200",
        "ID_Oficina": "11",
        "Codigo_de_Oficina": "102",
        "Oficina": "Centro",
        "ID_Serie": "21",
        "Serie": "Reserva",
        "ID_Linea": "31",
        "Fila": "B",
        "Modulo": "5",
        "DNI_Ejecutivo": "11.222.333-4",
        "Nombre_Ejecutivo": "Grace",
        "Fecha_Reserva": "2026-07-02",
        "Hora_Reserva": "10:00:00",
        "Prefijo_Fila": "B",
        "Terminal_Reserva": "T1",
        "DNI_Cliente": "8.765.432-1",
        "ID_Tipo_Cliente": "2",
        "Tipo_Cliente": "Pensionado",
        "Nombre_Cliente": "Cliente Dos",
        "Email_Cliente": "cliente2@example.test",
        "Fecha_Creacion_Reserva": "2026-07-01",
        "Hora_Creacion_Reserva": "08:00:00",
        "Fecha_Atencion": "2026-07-02",
        "Hora_Atencion": "10:02:00",
        "Hora_Termino_Atencion": "10:15:00",
        "Tiempo_Espera": "00:02:00",
        "Tiempo_Atencion": "00:13:00",
        "Cancelado": "N",
        "Fecha_Cancelacion": "",
        "Usuario_que_Cancelo": "",
        "Motivo_de_Cancelacion": "",
        "ID_Motivos": "303$3003",
        "Motivo_Atencion": "Solicitud$Certificado",
        "Formulario": "Sucursal",
        "Perdido": "N",
        "Saltado": "N",
        "Origen_de_Creacion": "Web",
        "Nombre_Agente": "Agente Mock",
        "Email_Agente": "agente@example.test",
        "DNI_Agente": "7.654.321-0",
        "Modo_de_Atencion": "Presencial",
    }

    base = transform_agendamientos_base([row], "202607")
    motivos = transform_agendamientos_motivos([row], "202607")

    assert base[0]["fechaCierre"] == "20260701"
    assert base[0]["DNI_Ejecutivo"] == "11222333-4"
    assert base[0]["Fecha_Reserva"] == "20260702"
    assert "ID_Motivos" not in base[0]
    assert "Motivo_Atencion" not in base[0]
    assert motivos == [
        {
            "fechaCierre": "20260701",
            "ID_Reserva": "R-200",
            "ID_Llamada": "CALL-200",
            "ID_Oficina": 11,
            "ID_Serie": 21,
            "IDMotivoAtencion": 303,
            "DescMotivoAtencion": "Solicitud",
            "IDSubMotivoAtencion": 3003,
            "DescSubMotivoAtencion": "Certificado",
        }
    ]


def test_motivo_expansion_keeps_missing_submotivo_explicit() -> None:
    row = {
        "ID_Ticket": "T-101",
        "ID_Llamada": "CALL-101",
        "ID_Oficina": "10",
        "ID_Serie": "20",
        "ID_Motivos": "404",
        "Motivo_Atencion": "Orientacion",
    }

    transformed = transform_atenciones_motivos([row], "202607")

    assert transformed[0]["IDSubMotivoAtencion"] is None
    assert transformed[0]["DescSubMotivoAtencion"] == ""


def test_motivo_expansion_rejects_unpaired_lists() -> None:
    row = {
        "ID_Ticket": "T-102",
        "ID_Llamada": "CALL-102",
        "ID_Oficina": "10",
        "ID_Serie": "20",
        "ID_Motivos": "101$1001,202$2002",
        "Motivo_Atencion": "Solo una descripcion",
    }

    try:
        transform_atenciones_motivos([row], "202607")
    except ValueError as exc:
        assert "same number" in str(exc)
    else:
        raise AssertionError("unpaired motivo lists must be rejected")


def test_motivo_expansion_preserves_duplicates_and_normalizes_whitespace() -> None:
    row = {
        "ID_Ticket": "T-103",
        "ID_Llamada": "CALL-103",
        "ID_Oficina": "10",
        "ID_Serie": "20",
        "ID_Motivos": " 101 $ 1001 , 101 $ 1001 ",
        "Motivo_Atencion": " Consulta $ Cartola , Consulta $ Cartola ",
    }

    transformed = transform_atenciones_motivos([row], "202607")

    assert len(transformed) == 2
    assert transformed[0] == transformed[1]
    assert transformed[0]["IDMotivoAtencion"] == 101
    assert transformed[0]["IDSubMotivoAtencion"] == 1001
    assert transformed[0]["DescMotivoAtencion"] == "Consulta"
    assert transformed[0]["DescSubMotivoAtencion"] == "Cartola"


def test_motivo_expansion_handles_empty_values_deterministically() -> None:
    empty_row = {
        "ID_Ticket": "T-104",
        "ID_Llamada": "CALL-104",
        "ID_Oficina": "10",
        "ID_Serie": "20",
        "ID_Motivos": "",
        "Motivo_Atencion": "",
    }
    trailing_empty_row = {
        **empty_row,
        "ID_Motivos": "101$1001,",
        "Motivo_Atencion": "Consulta$Cartola,",
    }

    assert transform_atenciones_motivos([empty_row], "202607") == []
    transformed = transform_atenciones_motivos([trailing_empty_row], "202607")
    assert len(transformed) == 2
    assert transformed[1]["IDMotivoAtencion"] is None
    assert transformed[1]["IDSubMotivoAtencion"] is None
    assert transformed[1]["DescMotivoAtencion"] == ""
    assert transformed[1]["DescSubMotivoAtencion"] == ""


@pytest.mark.parametrize(
    ("field", "invalid_value", "message"),
    [
        ("ID_Oficina", "not-an-integer", "ID_Oficina"),
        ("Hora_Emision_Ticket", "25:00:00", "Hora_Emision_Ticket"),
        ("Fecha", "2026-02-30", "Fecha"),
    ],
)
def test_atenciones_rejects_invalid_typed_values(
    field: str, invalid_value: str, message: str
) -> None:
    row = {
        "ID_Ticket": "T-105",
        "ID_Oficina": "10",
        "Fecha": "2026-07-01",
        "Hora_Emision_Ticket": "09:00:00",
        field: invalid_value,
    }

    with pytest.raises(ValueError, match=message):
        transform_atenciones_base([row], "202607")


def test_agendamientos_allows_empty_nullable_dates() -> None:
    row = {
        "ID_Reserva": "R-201",
        "ID_Oficina": "11",
        "Fecha_Reserva": "2026-07-02",
        "Hora_Reserva": "10:00:00",
        "Fecha_Cancelacion": "",
    }

    transformed = transform_agendamientos_base([row], "202607")

    assert transformed[0]["ID_Oficina"] == 11
    assert transformed[0]["Fecha_Cancelacion"] == ""
