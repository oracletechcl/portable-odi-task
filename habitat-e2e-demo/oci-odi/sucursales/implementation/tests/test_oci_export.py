from __future__ import annotations

import hashlib
import json
import re
import sys
import zipfile
from pathlib import Path

import pytest


IMPLEMENTATION_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(IMPLEMENTATION_ROOT))

from habitat_sucursales.oci_export import (
    build_export_documents,
    package_export,
    sha256_file,
    write_export,
)
from habitat_sucursales.cli import main


EXPECTED_ROUTES = {
    "/v1/periods",
    "/v1/process/atenciones",
    "/v1/process/agendamientos",
    "/v1/validate",
    "/v1/notify-error",
}

EXPECTED_TASK_ORDER = [
    "TASK_PERIODS",
    "TASK_ATENCIONES_PREVIOUS",
    "TASK_ATENCIONES_CURRENT",
    "TASK_AGENDAMIENTOS_PREVIOUS",
    "TASK_AGENDAMIENTOS_CURRENT",
    "TASK_VALIDATE",
]


def _objects(documents: dict[str, dict[str, object]]) -> list[dict[str, object]]:
    return [
        document
        for path, document in documents.items()
        if path.startswith("Objects/")
    ]


def test_export_documents_match_import_bundle_contract() -> None:
    documents = build_export_documents()

    assert set(documents) == {
        "manifest.json",
        *(path.lstrip("/") for path in documents["manifest.json"]["objects"]),
    }
    assert all(path.startswith("/Objects/") for path in documents["manifest.json"]["objects"])
    assert documents["manifest.json"]["version"] == "V1"
    assert documents["manifest.json"]["exportedWorkspaceOcid"] == ""
    objects = _objects(documents)
    assert len(objects) == 13
    assert len({item["key"] for item in objects}) == len(objects)
    assert {item["modelType"] for item in objects} == {
        "USER_PROJECT",
        "REST_TASK",
        "PIPELINE",
        "PIPELINE_TASK",
    }
    assert all(item["objectStatus"] == 8 for item in objects)
    project = next(item for item in objects if item["modelType"] == "USER_PROJECT")
    assert documents["manifest.json"]["objectKeysProvidedForExport"] == [
        project["key"]
    ]
    assert project["metadata"] == {"registryVersion": 1}
    for item in objects:
        assert "registryMetadata" not in item
        assert "parentRef" not in item
        if item is project:
            continue
        assert item["metadata"]["registryVersion"] == 1
        assert item["metadata"]["aggregatorKey"] == project["key"]
        assert item["metadata"]["aggregator"] == {
            "description": project["description"],
            "identifier": project["identifier"],
            "key": project["key"],
            "name": project["name"],
            "type": "USER_PROJECT",
        }


def test_rest_tasks_use_publishable_parameter_free_mock_contract() -> None:
    documents = build_export_documents()
    rest_tasks = [
        item for item in _objects(documents) if item["modelType"] == "REST_TASK"
    ]

    assert len(rest_tasks) == 10
    routes: set[str] = set()
    for task in rest_tasks:
        assert task["apiCallMode"] == "SYNCHRONOUS"
        assert "authConfig" not in task
        call_config = task["executeRestCallConfig"]
        assert call_config["methodType"] == "POST"
        assert call_config["requestHeaders"] == {
            "Content-Type": "application/json"
        }
        request_config = call_config["configValues"]["configParamValues"]
        endpoint = request_config["requestURL"]["stringValue"]
        assert endpoint.startswith("http://mock-backend.invalid")
        assert "opConfigValues" not in task
        assert task["parameters"] == []
        assert task["isConcurrentAllowed"] is False
        routes.add(endpoint.removeprefix("http://mock-backend.invalid"))

    assert routes == EXPECTED_ROUTES


def test_pipeline_preserves_order_and_explicit_failure_notification() -> None:
    documents = build_export_documents()
    pipeline = next(
        item for item in _objects(documents) if item["modelType"] == "PIPELINE"
    )

    task_nodes = [
        node
        for node in pipeline["nodes"]
        if node["operator"]["modelType"] == "TASK_OPERATOR"
        and not node["name"].startswith("TASK_NOTIFY_")
    ]
    assert [node["name"] for node in task_nodes] == EXPECTED_TASK_ORDER

    notify_nodes = [
        node for node in pipeline["nodes"] if node["name"].startswith("TASK_NOTIFY_")
    ]
    assert [node["name"] for node in notify_nodes] == [
        "TASK_NOTIFY_ATENCIONES_PREVIOUS",
        "TASK_NOTIFY_ATENCIONES_CURRENT",
        "TASK_NOTIFY_AGENDAMIENTOS_PREVIOUS",
        "TASK_NOTIFY_AGENDAMIENTOS_CURRENT",
    ]
    assert all(node["operator"]["triggerRule"] == "ALL_FAILED" for node in notify_nodes)
    assert all(node["operator"]["taskType"] == "REST_TASK" for node in notify_nodes)
    assert len({node["operator"]["task"]["key"] for node in notify_nodes}) == 4
    assert {
        node["operator"]["task"]["identifier"] for node in notify_nodes
    } == {
        "REST_NOTIFY_ATENCIONES_PREVIOUS",
        "REST_NOTIFY_ATENCIONES_CURRENT",
        "REST_NOTIFY_AGENDAMIENTOS_PREVIOUS",
        "REST_NOTIFY_AGENDAMIENTOS_CURRENT",
    }

    input_owner = {
        link["key"]: node["name"]
        for node in pipeline["nodes"]
        for link in node["inputLinks"]
    }
    targets = {
        node["name"]: {
            input_owner[target]
            for link in node["outputLinks"]
            for target in link["toLinks"]
        }
        for node in pipeline["nodes"]
    }
    assert targets["TASK_PERIODS"] == {"TASK_ATENCIONES_PREVIOUS"}
    assert targets["TASK_ATENCIONES_PREVIOUS"] == {
        "TASK_ATENCIONES_CURRENT",
        "TASK_NOTIFY_ATENCIONES_PREVIOUS",
    }
    assert targets["TASK_ATENCIONES_CURRENT"] == {
        "TASK_AGENDAMIENTOS_PREVIOUS",
        "TASK_NOTIFY_ATENCIONES_CURRENT",
    }
    assert targets["TASK_AGENDAMIENTOS_PREVIOUS"] == {
        "TASK_AGENDAMIENTOS_CURRENT",
        "TASK_NOTIFY_AGENDAMIENTOS_PREVIOUS",
    }
    assert targets["TASK_AGENDAMIENTOS_CURRENT"] == {
        "TASK_VALIDATE",
        "TASK_NOTIFY_AGENDAMIENTOS_CURRENT",
    }
    for notify_node in notify_nodes:
        assert targets[notify_node["name"]] == {"END"}

    end_nodes = [
        node
        for node in pipeline["nodes"]
        if node["operator"]["modelType"] == "END_OPERATOR"
    ]
    assert len(end_nodes) == 1
    assert end_nodes[0]["operator"]["triggerRule"] == "ALL_SUCCESS"


def test_pipeline_task_is_ready_to_run_without_runtime_parameters() -> None:
    documents = build_export_documents()
    objects = _objects(documents)
    pipeline = next(item for item in objects if item["modelType"] == "PIPELINE")
    pipeline_task = next(
        item for item in objects if item["modelType"] == "PIPELINE_TASK"
    )
    assert pipeline["parameters"] == []
    assert pipeline_task["parameters"] == []
    assert pipeline_task["configProviderDelegate"] == {}
    assert pipeline_task["pipeline"]["nestedDepth"] == 0
    assert pipeline_task["pipeline"]["nodes"] == []
    assert pipeline_task["pipeline"]["parameters"] == []


def test_pipeline_links_are_bidirectional_and_tasks_need_no_bindings() -> None:
    documents = build_export_documents()
    pipeline = next(
        item for item in _objects(documents) if item["modelType"] == "PIPELINE"
    )

    output_links = {
        link["key"]: link
        for node in pipeline["nodes"]
        for link in node["outputLinks"]
    }
    input_links = {
        link["key"]: link
        for node in pipeline["nodes"]
        for link in node["inputLinks"]
    }
    for output_key, output in output_links.items():
        for input_key in output["toLinks"]:
            assert input_links[input_key]["fromLink"] == output_key
    for input in input_links.values():
        assert input["fromLink"] in output_links
        assert input["key"] in output_links[input["fromLink"]]["toLinks"]

    for node in pipeline["nodes"]:
        operator = node["operator"]
        if operator["modelType"] != "TASK_OPERATOR":
            continue
        assert operator["task"]["parameters"] == []
        assert operator["configProviderDelegate"] == {}


def test_processing_tasks_use_only_declared_request_parameters() -> None:
    documents = build_export_documents()
    rest_tasks = [
        item for item in _objects(documents) if item["modelType"] == "REST_TASK"
    ]
    processing = [
        task
        for task in rest_tasks
        if task["identifier"].startswith(("REST_ATENCIONES_", "REST_AGENDAMIENTOS_"))
    ]

    assert len(processing) == 4
    for task in processing:
        request_payload = task["executeRestCallConfig"]["configValues"][
            "configParamValues"
        ]["requestPayload"]["refValue"]["configValues"]["configParamValues"][
            "dataParam"
        ]["stringValue"]
        body = json.loads(request_payload)
        assert body == {
            "as_of_date": "${AS_OF_DATE}",
            "window": body["window"],
        }
        assert body["window"] in {"previous", "current"}


def test_every_rest_task_is_materialized_by_deploy_without_declared_parameters() -> None:
    documents = build_export_documents()
    rest_tasks = [
        item for item in _objects(documents) if item["modelType"] == "REST_TASK"
    ]
    placeholder = re.compile(r"\$\{([A-Z0-9_]+)\}")

    for task in rest_tasks:
        request_config = task["executeRestCallConfig"]["configValues"][
            "configParamValues"
        ]
        request_url = request_config["requestURL"]["stringValue"]
        request_body = request_config["requestPayload"]["refValue"][
            "configValues"
        ]["configParamValues"]["dataParam"]["stringValue"]
        referenced = set(placeholder.findall(request_url + request_body))
        assert task["parameters"] == []
        assert referenced.issubset({"AS_OF_DATE"})


def test_write_and_package_are_byte_deterministic(tmp_path: Path) -> None:
    project_name = "HABITAT_SUCURSALES.project"
    first_dir = write_export(tmp_path / "first" / project_name)
    second_dir = write_export(tmp_path / "second" / project_name)
    first_zip = package_export(
        first_dir, tmp_path / "first" / "HABITAT_SUCURSALES.project.zip"
    )
    second_zip = package_export(
        second_dir, tmp_path / "second" / "HABITAT_SUCURSALES.project.zip"
    )

    assert first_zip.read_bytes() == second_zip.read_bytes()
    assert sha256_file(first_zip) == hashlib.sha256(first_zip.read_bytes()).hexdigest()
    with zipfile.ZipFile(first_zip) as archive:
        assert archive.testzip() is None
        project_root = f"{project_name}/"
        assert archive.namelist()[:2] == [
            project_root,
            f"{project_root}Objects/",
        ]
        assert all(info.date_time == (1980, 1, 1, 0, 0, 0) for info in archive.infolist())
        manifest_path = f"{project_root}manifest.json"
        manifest = json.loads(archive.read(manifest_path))
        assert set(archive.namelist()) == {
            project_root,
            f"{project_root}Objects/",
            manifest_path,
            *(f"{project_root}{path.lstrip('/')}" for path in manifest["objects"]),
        }


def test_package_requires_project_zip_suffix(tmp_path: Path) -> None:
    export_dir = write_export(tmp_path / "bundle.project")

    with pytest.raises(ValueError, match=r"\.project\.zip"):
        package_export(export_dir, tmp_path / "bundle.pipeline.zip")


def test_package_cli_writes_import_asset_and_checksum(
    tmp_path: Path, capsys
) -> None:
    export_dir = tmp_path / "HABITAT_SUCURSALES.project"
    archive = tmp_path / "HABITAT_SUCURSALES.project.zip"

    status = main(
        [
            "package-oci",
            "--export-dir",
            str(export_dir),
            "--zip-path",
            str(archive),
        ]
    )

    result = json.loads(capsys.readouterr().out)
    checksum_path = Path(f"{archive}.sha256")
    assert status == 0
    assert archive.is_file()
    assert checksum_path.read_text().split()[0] == sha256_file(archive)
    assert result["sha256"] == sha256_file(archive)
