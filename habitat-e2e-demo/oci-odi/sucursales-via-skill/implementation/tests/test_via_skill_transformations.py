from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parents[1]))
from transformations import calculate_periods, transform_base, transform_motivos

def test_period_boundary_and_rut_normalization():
    assert calculate_periods("2024-01-15") == {"previous": "202312", "current": "202401"}
    assert transform_base([{"DNI_Ejecutivo": "12.345.678-9"}], "202403")[0] == {"DNI_Ejecutivo": "12345678-9", "fechaCierre": "20240301"}

def test_motivo_pairs_and_rejects_unpaired_values():
    row = {"ID_Ticket": "T1", "ID_Motivos": "1$2", "Motivo_Atencion": "A$B"}
    assert transform_motivos([row], "202403", "ID_Ticket")[0]["IDSubMotivoAtencion"] == "2"
