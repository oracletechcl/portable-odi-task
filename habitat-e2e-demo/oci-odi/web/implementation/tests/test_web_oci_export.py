from __future__ import annotations

import hashlib
import json
import zipfile
from pathlib import Path

from habitat_web.oci_export import build_project


def _load_object(project_dir: Path, model_type: str) -> dict[str, object]:
    objects = [
        json.loads(path.read_text())
        for path in (project_dir / "Objects").glob("*.json")
    ]
    matches = [obj for obj in objects if obj["modelType"] == model_type]
    assert len(matches) == 1
    return matches[0]


def test_oci_export_is_deterministic_and_has_explicit_archive_envelope(
    tmp_path: Path,
) -> None:
    first = build_project(tmp_path / "first")
    second = build_project(tmp_path / "second")

    assert first.zip_path.read_bytes() == second.zip_path.read_bytes()
    assert first.sha256 == hashlib.sha256(first.zip_path.read_bytes()).hexdigest()
    with zipfile.ZipFile(first.zip_path) as archive:
        names = archive.namelist()
    assert "HABITAT_WEB.project/" in names
    assert "HABITAT_WEB.project/Objects/" in names
    assert "HABITAT_WEB.project/manifest.json" in names


def test_oci_export_uses_parameter_free_mock_template_urls(tmp_path: Path) -> None:
    result = build_project(tmp_path)

    rest_objects = list(
        (result.project_dir / "Objects").glob("REST_TASK_*.json")
    )
    assert len(rest_objects) == 7
    for path in rest_objects:
        text = path.read_text()
        assert '"parameters":[]' in text
        assert "http://mock-backend.invalid/" in text
        assert '"modelType":"JSON_TEXT"' in text


def test_pipeline_uses_importable_flow_nodes_and_reciprocal_links(
    tmp_path: Path,
) -> None:
    result = build_project(tmp_path)
    pipeline = _load_object(result.project_dir, "PIPELINE")
    nodes = pipeline["nodes"]

    assert pipeline["nestedDepth"] == 0
    assert pipeline["objectVersion"] == 1
    assert pipeline["parameters"] == []
    assert "variables" not in pipeline
    assert len(nodes) == 9
    assert all(node["modelType"] == "FLOW_NODE" for node in nodes)
    assert [node["operator"]["modelType"] for node in nodes] == [
        "START_OPERATOR",
        *(["TASK_OPERATOR"] * 7),
        "END_OPERATOR",
    ]

    for node in nodes:
        assert node["parentRef"] == {"parent": pipeline["key"]}
        assert node["operator"]["parentRef"] == {"parent": node["key"]}

    for source, target in zip(nodes, nodes[1:]):
        assert len(source["outputLinks"]) == 1
        assert len(target["inputLinks"]) == 1
        output_link = source["outputLinks"][0]
        input_link = target["inputLinks"][0]
        assert output_link["toLinks"] == [input_link["key"]]
        assert input_link["fromLink"] == output_link["key"]
        assert output_link["parentRef"] == {"parent": source["key"]}
        assert input_link["parentRef"] == {"parent": target["key"]}

    for node in nodes[1:-1]:
        task = node["operator"]["task"]
        assert task["objectStatus"] == 1
        assert task["objectVersion"] == 1
        assert task["inputPorts"] == []
        assert task["outputPorts"] == []
        assert task["parameters"] == []


def test_rest_and_pipeline_tasks_use_complete_oci_envelopes(
    tmp_path: Path,
) -> None:
    result = build_project(tmp_path)
    rest_path = next(
        (result.project_dir / "Objects").glob("REST_TASK_*.json")
    )
    rest_task = json.loads(rest_path.read_text())
    execute_config = rest_task["executeRestCallConfig"]

    assert rest_task["apiCallMode"] == "SYNCHRONOUS"
    assert rest_task["objectVersion"] == 1
    assert rest_task["inputPorts"] == []
    assert rest_task["outputPorts"] == []
    assert execute_config["methodType"] == "POST"
    assert execute_config["requestHeaders"] == {
        "Content-Type": "application/json"
    }
    assert execute_config["configValues"]["parentRef"] == {
        "parent": rest_task["key"]
    }
    assert set(execute_config["configValues"]["configParamValues"]) == {
        "requestPayload",
        "requestURL",
    }

    pipeline = _load_object(result.project_dir, "PIPELINE")
    pipeline_task = _load_object(result.project_dir, "PIPELINE_TASK")
    pipeline_stub = pipeline_task["pipeline"]
    assert pipeline_task["objectVersion"] == 1
    assert pipeline_task["inputPorts"] == []
    assert pipeline_task["outputPorts"] == []
    assert pipeline_stub == {
        "identifier": pipeline["identifier"],
        "key": pipeline["key"],
        "modelType": "PIPELINE",
        "modelVersion": pipeline["modelVersion"],
        "name": pipeline["name"],
        "nestedDepth": 0,
        "nodes": [],
        "objectStatus": 1,
        "objectVersion": 1,
        "parameters": [],
    }
