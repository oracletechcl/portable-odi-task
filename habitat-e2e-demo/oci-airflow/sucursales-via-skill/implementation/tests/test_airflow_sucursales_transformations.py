from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parents[1]))
from airflow_sucursales_transformations import periods, transform_base, transform_motivos

def test_period_rollover_and_rut_cleanup():
    assert periods("2024-01-15") == {"previous": "202312", "current": "202401"}
    assert transform_base([{"DNI_Ejecutivo": "12.345.678-9"}], "202403")[0]["fechaCierre"] == "20240301"

def test_motivo_pairing():
    output = transform_motivos([{"ID_Ticket": "T1", "ID_Motivos": "1$2", "Motivo_Atencion": "A$B"}], "202403", "ID_Ticket")
    assert output == [{"fechaCierre": "20240301", "ID_Ticket": "T1", "IDMotivoAtencion": "1", "DescMotivoAtencion": "A", "IDSubMotivoAtencion": "2", "DescSubMotivoAtencion": "B"}]
