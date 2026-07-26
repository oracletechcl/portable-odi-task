"""Airflow orchestration for Pentaho cargaArchivoExterno."""
from __future__ import annotations
import json
from datetime import datetime
from urllib.request import Request, urlopen
from airflow.decorators import dag, task
from airflow.models import Variable
from airflow.utils.trigger_rule import TriggerRule

DAG_ID = "habitat_sucursales_carga_archivo_externo"

def _post(route: str, payload: dict[str, object]) -> dict[str, object]:
    base_url = Variable.get("sucursales_mock_base_url")
    request = Request(base_url.rstrip("/") + route, data=json.dumps(payload).encode(), headers={"Content-Type": "application/json"}, method="POST")
    with urlopen(request, timeout=60) as response: return json.load(response)

@dag(dag_id=DAG_ID, schedule=None, start_date=datetime(2024, 1, 1), catchup=False, tags=["habitat", "sucursales"])
def carga_archivo_externo():
    @task
    def obtener_periodos(logical_date=None):
        date_value = (logical_date or datetime.now()).date().isoformat()
        return _post("/v1/periods", {"as_of_date": date_value})["periods"]
    @task
    def atenciones(periods_value, window: str): return _post("/v1/process/atenciones", {"as_of_date": periods_value["as_of_date"], "window": window})
    @task
    def agendamientos(periods_value, window: str): return _post("/v1/process/agendamientos", {"as_of_date": periods_value["as_of_date"], "window": window})
    @task(trigger_rule=TriggerRule.ALL_FAILED)
    def notificar_error(step: str): return _post("/v1/notify-error", {"status": "error", "step": step, "message": "Pentaho-equivalent task failed"})
    windows = obtener_periodos(); at_prev = atenciones(windows, "previous"); at_cur = atenciones(windows, "current"); ag_prev = agendamientos(windows, "previous"); ag_cur = agendamientos(windows, "current")
    at_prev >> at_cur >> ag_prev >> ag_cur
    for upstream, name in ((at_prev, "Atenciones ZeroQ - Mes Anterior"), (at_cur, "Atenciones ZeroQ - Mes Actual"), (ag_prev, "Agendamiento ZeroQ - Mes Anterior"), (ag_cur, "Agendamiento ZeroQ - Mes Actual")):
        upstream >> notificar_error.override(task_id="notificar_" + name.lower().replace(" ", "_").replace("-", "_"))(name)
carga_archivo_externo()
