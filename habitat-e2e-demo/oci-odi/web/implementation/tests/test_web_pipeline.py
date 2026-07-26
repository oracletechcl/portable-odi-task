from __future__ import annotations

import json
from pathlib import Path

import pytest

from habitat_web.pipeline import PipelineError, ROUTES, run_pipeline
from habitat_web.transformations import DATASET_CONTRACTS


class FakeClient:
    def __init__(self, *, fail_at: str | None = None) -> None:
        self.calls: list[tuple[str, dict[str, str]]] = []
        self.fail_at = fail_at

    def post_json(self, route: str, payload: dict[str, str]) -> object:
        self.calls.append((route, payload))
        if route == self.fail_at:
            raise PipelineError("synthetic boundary failure")
        dataset = next(name for name, expected in ROUTES.items() if expected == route)
        fields = DATASET_CONTRACTS[dataset].fields
        return {"records": [{field: "" for field in fields}]}


def test_pipeline_calls_source_derived_stages_in_order_and_writes_outputs(
    tmp_path: Path,
) -> None:
    client = FakeClient()

    manifest = run_pipeline(
        client=client,
        output_dir=tmp_path,
        run_date="2026-07-25",
    )

    assert [route for route, _ in client.calls] == list(ROUTES.values())
    assert [item["name"] for item in manifest["outputs"]] == [
        f"{dataset}.csv" for dataset in DATASET_CONTRACTS
    ]
    for dataset in DATASET_CONTRACTS:
        assert (tmp_path / f"{dataset}.csv").is_file()
    saved = json.loads((tmp_path / "run-manifest.json").read_text())
    assert saved == manifest


def test_pipeline_stops_after_failed_stage_and_records_no_false_success(
    tmp_path: Path,
) -> None:
    failed_route = ROUTES["SEC_SECCION"]
    client = FakeClient(fail_at=failed_route)

    with pytest.raises(PipelineError, match="SEC_SECCION"):
        run_pipeline(client=client, output_dir=tmp_path, run_date="2026-07-25")

    assert [route for route, _ in client.calls][-1] == failed_route
    assert not (tmp_path / "run-manifest.json").exists()


def test_pipeline_rejects_path_traversal_output_directory(tmp_path: Path) -> None:
    with pytest.raises(PipelineError, match="output directory"):
        run_pipeline(
            client=FakeClient(),
            output_dir=tmp_path / ".." / "escaped",
            run_date="2026-07-25",
        )
