"""Airflow equivalent of the Web Pentaho extracted-file workflow."""
from __future__ import annotations

import os
import sys
from datetime import datetime
from pathlib import Path

from airflow.decorators import dag, task
from airflow.models import Variable
from airflow.utils.trigger_rule import TriggerRule

IMPLEMENTATION = Path(__file__).resolve().parent / "habitat_web"
if str(IMPLEMENTATION) not in sys.path:
    sys.path.insert(0, str(IMPLEMENTATION))
from web_pipeline import run_pipeline  # noqa: E402

DAG_ID = "habitat_web_carga_archivo_externo"


@dag(dag_id=DAG_ID, schedule=None, start_date=datetime(2024, 1, 1), catchup=False, tags=["habitat", "web"])
def carga_archivo_externo():
    @task(retries=2)
    def archivo_sesion(logical_date=None):
        run_date = (logical_date or datetime.now()).date().isoformat()
        base_url = Variable.get("habitat_web_mock_base_url")
        output_root = Path(os.environ.get("HABITAT_WEB_OUTPUT_ROOT", "/tmp/habitat-web"))
        return run_pipeline(base_url=base_url, output_dir=output_root / run_date, run_date=run_date)

    @task
    def exito_carga_archivo_externo(manifest):
        return {"status": "success", "outputs": len(manifest["outputs"])}

    @task(trigger_rule=TriggerRule.ONE_FAILED)
    def error_carga_archivo_externo():
        raise RuntimeError("Archivo Sesion failed; Pentaho Error cargaArchivoExterno branch selected")

    archived = archivo_sesion()
    archived >> exito_carga_archivo_externo(archived)
    archived >> error_carga_archivo_externo()


carga_archivo_externo()
