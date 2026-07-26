from __future__ import annotations

import hashlib
import json
import uuid
import zipfile
from dataclasses import dataclass
from pathlib import Path

from .pipeline import ROUTES


PROJECT_NAME = "HABITAT_WEB"
PROJECT_IDENTIFIER = "HABITAT_WEB"
PIPELINE_IDENTIFIER = "PL_HABITAT_WEB"
PIPELINE_TASK_IDENTIFIER = "TASK_RUN_HABITAT_WEB"
REST_MODEL_VERSION = "20230421"
PIPELINE_MODEL_VERSION = "20220124"
FLOW_MODEL_VERSION = "20211031"
OPERATOR_MODEL_VERSION = "20220523"
_NAMESPACE = uuid.UUID("82027ea8-16f1-5db7-930c-56c48bd692f2")
_ZIP_TIME = (1980, 1, 1, 0, 0, 0)


@dataclass(frozen=True)
class ExportResult:
    project_dir: Path
    zip_path: Path
    checksum_path: Path
    sha256: str


def _key(identifier: str) -> str:
    return str(uuid.uuid5(_NAMESPACE, identifier))


def _metadata(project_key: str) -> dict[str, object]:
    return {
        "aggregator": {
            "type": "USER_PROJECT",
            "key": project_key,
            "identifier": PROJECT_IDENTIFIER,
        },
        "aggregatorKey": project_key,
        "registryVersion": 1,
    }


def _compact(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _rest_object(
    dataset: str,
    route: str,
    *,
    project_key: str,
) -> dict[str, object]:
    identifier = f"REST_{dataset}"
    task_key = _key(identifier)
    body = {"runDate": "2026-07-25"}
    return {
        "apiCallMode": "SYNCHRONOUS",
        "configProviderDelegate": {},
        "description": f"Calls the portable mock endpoint {route}",
        "executeRestCallConfig": {
            "configValues": {
                "configParamValues": {
                    "requestURL": {
                        "stringValue": f"http://mock-backend.invalid{route}"
                    },
                    "requestPayload": {
                        "refValue": {
                            "modelType": "JSON_TEXT",
                            "configValues": {
                                "configParamValues": {
                                    "dataParam": {
                                        "stringValue": _compact(body)
                                    }
                                }
                            },
                        }
                    },
                },
                "parentRef": {"parent": task_key},
            },
            "methodType": "POST",
            "requestHeaders": {"Content-Type": "application/json"},
        },
        "identifier": identifier,
        "inputPorts": [],
        "isConcurrentAllowed": False,
        "jsonData": _compact(body),
        "key": task_key,
        "modelType": "REST_TASK",
        "modelVersion": REST_MODEL_VERSION,
        "name": identifier,
        "objectStatus": 8,
        "objectVersion": 1,
        "outputPorts": [],
        "parameters": [],
        "typedExpressions": [],
        "metadata": _metadata(project_key),
    }


def _task_stub(task: dict[str, object]) -> dict[str, object]:
    return {
        "identifier": task["identifier"],
        "inputPorts": [],
        "key": task["key"],
        "modelType": task["modelType"],
        "modelVersion": task["modelVersion"],
        "name": task["name"],
        "objectStatus": 1,
        "objectVersion": 1,
        "outputPorts": [],
        "parameters": task["parameters"],
    }


def _flow_node(
    pipeline_key: str,
    name: str,
    *,
    task: dict[str, object] | None = None,
    coordinate_x: float = 0,
) -> dict[str, object]:
    node_key = _key(f"pipeline-node:{name}")
    operator_type = (
        "START_OPERATOR"
        if name == "START"
        else "END_OPERATOR"
        if name == "END"
        else "TASK_OPERATOR"
    )
    operator: dict[str, object] = {
        "identifier": f"OP_{name}",
        "inputPorts": [],
        "key": _key(f"pipeline-node:{name}:operator"),
        "modelType": operator_type,
        "modelVersion": (
            "20210408"
            if operator_type == "TASK_OPERATOR"
            else OPERATOR_MODEL_VERSION
        ),
        "name": name,
        "objectVersion": 0,
        "outputPorts": [],
        "parentRef": {"parent": node_key},
        "triggerRule": "ALL_SUCCESS",
    }
    if task is not None:
        operator.update(
            {
                "configProviderDelegate": {},
                "retryAttempts": 0,
                "retryDelay": 0,
                "retryDelayUnit": "SECONDS",
                "task": _task_stub(task),
                "taskType": task["modelType"],
            }
        )
    input_links = []
    if name != "START":
        input_links.append(
            {
                "key": _key(f"pipeline-node:{name}:input"),
                "modelType": "INPUT_LINK",
                "modelVersion": FLOW_MODEL_VERSION,
                "parentRef": {"parent": node_key},
            }
        )
    return {
        "inputLinks": input_links,
        "key": node_key,
        "modelType": "FLOW_NODE",
        "modelVersion": FLOW_MODEL_VERSION,
        "name": name,
        "operator": operator,
        "outputLinks": [],
        "parentRef": {"parent": pipeline_key},
        "uiProperties": {
            "coordinateX": coordinate_x,
            "coordinateY": 100.0,
            "isExpanded": False,
            "isInputPortsExpandable": False,
            "isOutputPortsExpandable": False,
        },
    }


def _connect(
    source: dict[str, object], target: dict[str, object]
) -> None:
    output_key = _key(f"pipeline-node:{source['name']}:output")
    input_link = target["inputLinks"][0]
    input_link["fromLink"] = output_key
    source["outputLinks"].append(
        {
            "key": output_key,
            "modelType": "OUTPUT_LINK",
            "modelVersion": FLOW_MODEL_VERSION,
            "parentRef": {"parent": source["key"]},
            "toLinks": [input_link["key"]],
        }
    )


def _pipeline_object(
    rest_objects: list[dict[str, object]],
    *,
    project_key: str,
) -> dict[str, object]:
    pipeline_key = _key(PIPELINE_IDENTIFIER)
    nodes = [
        _flow_node(pipeline_key, "START", coordinate_x=0.0),
        *[
            _flow_node(
                pipeline_key,
                f"TASK_{rest['identifier']}",
                task=rest,
                coordinate_x=float((position + 1) * 200),
            )
            for position, rest in enumerate(rest_objects)
        ],
        _flow_node(
            pipeline_key,
            "END",
            coordinate_x=float((len(rest_objects) + 1) * 200),
        )
    ]
    for source, target in zip(nodes, nodes[1:]):
        _connect(source, target)
    return {
        "modelType": "PIPELINE",
        "modelVersion": PIPELINE_MODEL_VERSION,
        "key": pipeline_key,
        "name": "HABITAT WEB PIPELINE",
        "identifier": PIPELINE_IDENTIFIER,
        "nestedDepth": 0,
        "objectStatus": 8,
        "objectVersion": 1,
        "parameters": [],
        "nodes": nodes,
        "metadata": _metadata(project_key),
    }


def _pipeline_task_object(
    pipeline: dict[str, object],
    *,
    project_key: str,
) -> dict[str, object]:
    return {
        "configProviderDelegate": {},
        "description": "Runnable task for the Habitat Web pipeline",
        "identifier": PIPELINE_TASK_IDENTIFIER,
        "inputPorts": [],
        "isConcurrentAllowed": False,
        "key": _key(PIPELINE_TASK_IDENTIFIER),
        "modelType": "PIPELINE_TASK",
        "modelVersion": REST_MODEL_VERSION,
        "name": "RUN HABITAT WEB",
        "objectStatus": 8,
        "objectVersion": 1,
        "outputPorts": [],
        "parameters": [],
        "metadata": _metadata(project_key),
        "pipeline": {
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
        },
    }


def _filename(obj: dict[str, object]) -> str:
    return f"{obj['modelType']}_{obj['identifier']}_{obj['key']}.json"


def _zip(project_dir: Path, destination: Path) -> None:
    root = project_dir.name
    entries: list[tuple[str, bytes, int]] = [
        (f"{root}/", b"", 0o755),
        (f"{root}/Objects/", b"", 0o755),
    ]
    for path in sorted(item for item in project_dir.rglob("*") if item.is_file()):
        entries.append(
            (f"{root}/{path.relative_to(project_dir).as_posix()}", path.read_bytes(), 0o644)
        )
    with zipfile.ZipFile(
        destination, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9
    ) as archive:
        for name, content, mode in entries:
            info = zipfile.ZipInfo(name, _ZIP_TIME)
            info.create_system = 3
            info.external_attr = (mode & 0xFFFF) << 16
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, content)


def build_project(output_root: Path) -> ExportResult:
    project_dir = output_root / f"{PROJECT_NAME}.project"
    objects_dir = project_dir / "Objects"
    objects_dir.mkdir(parents=True, exist_ok=True)

    project_key = _key(PROJECT_IDENTIFIER)
    project = {
        "modelType": "USER_PROJECT",
        "modelVersion": "20200901",
        "key": project_key,
        "name": PROJECT_NAME,
        "identifier": PROJECT_IDENTIFIER,
        "objectStatus": 8,
        "metadata": {"registryVersion": 1},
    }
    rest_objects = [
        _rest_object(dataset, route, project_key=project_key)
        for dataset, route in ROUTES.items()
    ]
    pipeline = _pipeline_object(rest_objects, project_key=project_key)
    pipeline_task = _pipeline_task_object(pipeline, project_key=project_key)
    objects = [project, *rest_objects, pipeline, pipeline_task]

    paths: list[str] = []
    for obj in objects:
        filename = _filename(obj)
        (objects_dir / filename).write_text(_compact(obj) + "\n", encoding="utf-8")
        paths.append(f"/Objects/{filename}")

    manifest = {
        "version": "V1",
        "exportedWorkspaceOcid": "",
        "objects": paths,
        "objectKeysProvidedForExport": [project_key],
        "referencedObjectsList": [],
        "modelVersionMap": {
            "257": "20200901",
            "788": "20220124",
            "67176213": "20230421",
            "17230268181": "20230421",
        },
    }
    (project_dir / "manifest.json").write_text(
        _compact(manifest) + "\n", encoding="utf-8"
    )

    zip_path = output_root / f"{PROJECT_NAME}.project.zip"
    _zip(project_dir, zip_path)
    digest = hashlib.sha256(zip_path.read_bytes()).hexdigest()
    checksum_path = zip_path.with_suffix(zip_path.suffix + ".sha256")
    checksum_path.write_text(f"{digest}  {zip_path.name}\n", encoding="ascii")
    return ExportResult(project_dir, zip_path, checksum_path, digest)
