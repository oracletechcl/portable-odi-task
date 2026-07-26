from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parents[1]))
import web_pipeline
from web_transformations import ContractError, DATASET_CONTRACTS, render_dataset


def test_seven_source_contracts_and_output_format():
    assert len(DATASET_CONTRACTS) == 7
    assert render_dataset("SEC_SECCION", [{"SEC_ID": 7, "SEC_MEN_ID": 10, "SEC_NOMBRE": "Atención", "SEC_ORDEN": 2, "SEC_NOMBRE_EXTRA": "Configuración", "SEC_DEFAULT": 0}]) == "7~|10~|Atención~|2~|Configuración~|0\n".encode("iso-8859-1")


def test_missing_fields_are_rejected():
    with pytest.raises(ContractError, match="missing fields"):
        render_dataset("SUB_SUBSECCION", [{"SUB_ID": 1}])


def test_pipeline_preserves_route_order_and_stops_on_failure(tmp_path, monkeypatch):
    calls = []
    def fake_post(base, route, payload):
        calls.append(route)
        if route == web_pipeline.ROUTES["SEC_SECCION"]:
            raise OSError("failure")
        dataset = next(key for key, value in web_pipeline.ROUTES.items() if value == route)
        return {"records": [{field.name: "" for field in DATASET_CONTRACTS[dataset].fields}]}
    monkeypatch.setattr(web_pipeline, "post_json", fake_post)
    with pytest.raises(web_pipeline.PipelineError, match="SEC_SECCION"):
        web_pipeline.run_pipeline(base_url="http://mock.invalid:8002", output_dir=tmp_path, run_date="2026-07-25")
    assert calls[-1] == web_pipeline.ROUTES["SEC_SECCION"]
    assert not (tmp_path / "run-manifest.json").exists()
