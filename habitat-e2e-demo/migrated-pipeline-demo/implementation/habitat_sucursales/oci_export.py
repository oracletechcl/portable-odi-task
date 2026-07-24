"""Deterministic OCI Data Integration export construction.

The object envelope follows the supplied OCI Data Integration pipeline export.
REST task request configuration follows the current OCI SDK model:
``REST_TASK`` + ``SYNCHRONOUS`` + ``executeRestCallConfig``.
"""

from __future__ import annotations

import hashlib
import gzip
import json
import re
import tarfile
import uuid
import zipfile
from pathlib import Path


NAMESPACE = uuid.UUID("cddc8a21-5a9b-45e9-a20a-a8a9ca69bdac")
REST_MODEL_VERSION = "20230421"
PIPELINE_MODEL_VERSION = "20220124"
FLOW_MODEL_VERSION = "20211031"
OPERATOR_MODEL_VERSION = "20220523"

PROCESSING_NODE_NAMES = (
    "TASK_ATENCIONES_PREVIOUS",
    "TASK_ATENCIONES_CURRENT",
    "TASK_AGENDAMIENTOS_PREVIOUS",
    "TASK_AGENDAMIENTOS_CURRENT",
)


def _processing_body(window: str) -> dict[str, object]:
    return {
        "as_of_date": "${AS_OF_DATE}",
        "window": window,
    }


TASK_DEFINITIONS = (
    ("REST_PERIODS", "/v1/periods", {"as_of_date": "${AS_OF_DATE}"}),
    (
        "REST_ATENCIONES_PREVIOUS",
        "/v1/process/atenciones",
        _processing_body("previous"),
    ),
    (
        "REST_ATENCIONES_CURRENT",
        "/v1/process/atenciones",
        _processing_body("current"),
    ),
    (
        "REST_AGENDAMIENTOS_PREVIOUS",
        "/v1/process/agendamientos",
        _processing_body("previous"),
    ),
    (
        "REST_AGENDAMIENTOS_CURRENT",
        "/v1/process/agendamientos",
        _processing_body("current"),
    ),
    ("REST_VALIDATE", "/v1/validate", {"as_of_date": "${AS_OF_DATE}"}),
    (
        "REST_NOTIFY_ERROR",
        "/v1/notify-error",
        {
            "message": "OCI Data Integration processing task failed",
            "status": "error",
            "step": "${FAILED_STEP}",
        },
    ),
)


def _key(label: str) -> str:
    return str(uuid.uuid5(NAMESPACE, label))


def _identifier(value: str) -> str:
    normalized = re.sub(r"[^A-Z0-9_]", "_", value.upper())
    if not normalized[0].isalpha() and normalized[0] != "_":
        normalized = f"_{normalized}"
    return normalized


def _parameter(parent_key: str, name: str) -> dict[str, object]:
    return {
        "defaultValue": (
            "http://mock-backend.invalid"
            if name == "MOCK_BASE_URL"
            else None
        ),
        "isInput": True,
        "isOutput": False,
        "key": _key(f"{parent_key}:parameter:{name}"),
        "modelType": "PARAMETER",
        "modelVersion": "20200129",
        "name": name,
        "objectStatus": 1,
        "parentRef": {"parent": parent_key},
        "type": "Seeded:/typeSystems/PLATFORM/dataTypes/STRING",
        "typeName": "VARCHAR",
    }


def _child_metadata(project: dict[str, object]) -> dict[str, object]:
    return {
        "aggregator": {
            "description": project["description"],
            "identifier": project["identifier"],
            "key": project["key"],
            "name": project["name"],
            "type": "USER_PROJECT",
        },
        "aggregatorKey": project["key"],
        "registryVersion": 1,
    }


def _project_object(project_key: str) -> dict[str, object]:
    return {
        "description": "Portable mock-backed Habitat Sucursales migration",
        "identifier": "HABITAT_SUCURSALES",
        "key": project_key,
        "modelType": "USER_PROJECT",
        "modelVersion": "20200901",
        "name": "HABITAT_SUCURSALES",
        "objectStatus": 8,
        "objectVersion": 1,
        "metadata": {"registryVersion": 1},
    }


def _request_payload(body: dict[str, object]) -> dict[str, object]:
    return {
        "refValue": {
            "configValues": {
                "configParamValues": {
                    "dataParam": {
                        "stringValue": json.dumps(
                            body,
                            ensure_ascii=False,
                            separators=(",", ":"),
                            sort_keys=True,
                        )
                    }
                }
            },
            "modelType": "JSON_TEXT",
        }
    }


def _rest_task_object(
    project: dict[str, object],
    identifier: str,
    route: str,
    body: dict[str, object],
) -> dict[str, object]:
    project_key = str(project["key"])
    task_key = _key(f"rest-task:{identifier}")
    body_text = json.dumps(body, ensure_ascii=False, sort_keys=True)
    referenced_parameters = set(
        re.findall(
            r"\$\{([A-Z0-9_]+)\}",
            f"${{MOCK_BASE_URL}}{route}{body_text}",
        )
    )
    parameter_names = [
        "MOCK_BASE_URL",
        *sorted(referenced_parameters - {"MOCK_BASE_URL"}),
    ]
    parameters = [
        _parameter(task_key, name) for name in parameter_names
    ]
    return {
        "apiCallMode": "SYNCHRONOUS",
        "configProviderDelegate": {},
        "description": f"Calls the portable mock endpoint {route}",
        "executeRestCallConfig": {
            "configValues": {
                "configParamValues": {
                    "requestPayload": _request_payload(body),
                    "requestURL": {
                        "stringValue": f"${{MOCK_BASE_URL}}{route}"
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
        "jsonData": json.dumps(
            body,
            ensure_ascii=False,
            separators=(",", ":"),
            sort_keys=True,
        ),
        "key": task_key,
        "modelType": "REST_TASK",
        "modelVersion": REST_MODEL_VERSION,
        "name": identifier,
        "objectStatus": 8,
        "objectVersion": 1,
        "opConfigValues": {
            "configParamValues": {
                "successCondition": {
                    "refValue": {
                        "exprString": (
                            "SYS.RESPONSE_STATUS >= 200 "
                            "AND SYS.RESPONSE_STATUS < 300"
                        ),
                        "modelType": "EXPRESSION",
                    }
                }
            },
            "parentRef": {"parent": task_key},
        },
        "outputPorts": [],
        "parameters": parameters,
        "metadata": _child_metadata(project),
        "typedExpressions": [],
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
    trigger_rule: str = "ALL_SUCCESS",
    bindings: dict[str, str] | None = None,
    coordinate_x: float = 0,
    coordinate_y: float = 0,
) -> dict[str, object]:
    node_key = _key(f"pipeline-node:{name}")
    input_link = {
        "key": _key(f"pipeline-node:{name}:input"),
        "modelType": "INPUT_LINK",
        "modelVersion": FLOW_MODEL_VERSION,
        "parentRef": {"parent": node_key},
    }
    if name == "START":
        operator_type = "START_OPERATOR"
    elif name == "END":
        operator_type = "END_OPERATOR"
    else:
        operator_type = "TASK_OPERATOR"
    operator: dict[str, object] = {
        "identifier": _identifier(name),
        "inputPorts": [],
        "key": _key(f"pipeline-node:{name}:operator"),
        "modelType": operator_type,
        "modelVersion": OPERATOR_MODEL_VERSION
        if operator_type != "TASK_OPERATOR"
        else "20210408",
        "name": name,
        "objectVersion": 0,
        "outputPorts": [],
        "parentRef": {"parent": node_key},
        "triggerRule": trigger_rule,
    }
    if task is not None:
        parameter_keys = {
            parameter["name"]: parameter["key"]
            for parameter in task["parameters"]
        }
        operator.update(
            {
                "configProviderDelegate": {
                    "bindings": {
                        parameter_keys[parameter]: {"simpleValue": value}
                        for parameter, value in sorted((bindings or {}).items())
                    }
                },
                "retryAttempts": 0,
                "retryDelay": 0,
                "retryDelayUnit": "SECONDS",
                "task": _task_stub(task),
                "taskType": task["modelType"],
            }
        )
    return {
        "inputLinks": [] if name == "START" else [input_link],
        "key": node_key,
        "modelType": "FLOW_NODE",
        "modelVersion": FLOW_MODEL_VERSION,
        "name": name,
        "operator": operator,
        "outputLinks": [],
        "parentRef": {"parent": pipeline_key},
        "uiProperties": {
            "coordinateX": coordinate_x,
            "coordinateY": coordinate_y,
            "isExpanded": False,
            "isInputPortsExpandable": False,
            "isOutputPortsExpandable": False,
        },
    }


def _connect(source: dict[str, object], targets: list[dict[str, object]]) -> None:
    output_key = _key(f"pipeline-node:{source['name']}:output")
    target_input_links = []
    for target in targets:
        input_link = next(
            (
                link
                for link in target["inputLinks"]
                if "fromLink" not in link
            ),
            None,
        )
        if input_link is None:
            input_link = {
                "key": _key(
                    f"pipeline-node:{target['name']}:input:{source['name']}"
                ),
                "modelType": "INPUT_LINK",
                "modelVersion": FLOW_MODEL_VERSION,
                "parentRef": {"parent": target["key"]},
            }
            target["inputLinks"].append(input_link)
        input_link["fromLink"] = output_key
        target_input_links.append(input_link["key"])
    source["outputLinks"].append(
        {
            "key": output_key,
            "modelType": "OUTPUT_LINK",
            "modelVersion": FLOW_MODEL_VERSION,
            "parentRef": {"parent": source["key"]},
            "toLinks": target_input_links,
        }
    )


def _pipeline_object(
    project: dict[str, object], rest_tasks: dict[str, dict[str, object]]
) -> dict[str, object]:
    pipeline_key = _key("pipeline:PL_HABITAT_SUCURSALES")
    task_map = {
        "TASK_PERIODS": rest_tasks["REST_PERIODS"],
        "TASK_ATENCIONES_PREVIOUS": rest_tasks["REST_ATENCIONES_PREVIOUS"],
        "TASK_ATENCIONES_CURRENT": rest_tasks["REST_ATENCIONES_CURRENT"],
        "TASK_AGENDAMIENTOS_PREVIOUS": rest_tasks[
            "REST_AGENDAMIENTOS_PREVIOUS"
        ],
        "TASK_AGENDAMIENTOS_CURRENT": rest_tasks[
            "REST_AGENDAMIENTOS_CURRENT"
        ],
        "TASK_VALIDATE": rest_tasks["REST_VALIDATE"],
    }
    start = _flow_node(
        pipeline_key, "START", coordinate_x=0, coordinate_y=100
    )
    main_nodes = {
        name: _flow_node(
            pipeline_key,
            name,
            task=task,
            bindings={
                "AS_OF_DATE": "${AS_OF_DATE}",
                "MOCK_BASE_URL": "${MOCK_BASE_URL}",
            },
            coordinate_x=float((index + 1) * 200),
            coordinate_y=100,
        )
        for index, (name, task) in enumerate(task_map.items())
    }
    notify_nodes = {
        processing_name: _flow_node(
            pipeline_key,
            processing_name.replace("TASK_", "TASK_NOTIFY_", 1),
            task=rest_tasks["REST_NOTIFY_ERROR"],
            trigger_rule="ALL_FAILED",
            bindings={
                "FAILED_STEP": processing_name,
                "MOCK_BASE_URL": "${MOCK_BASE_URL}",
            },
            coordinate_x=float((index + 2) * 200),
            coordinate_y=300,
        )
        for index, processing_name in enumerate(PROCESSING_NODE_NAMES)
    }
    end = _flow_node(
        pipeline_key,
        "END",
        trigger_rule="ALL_SUCCESS",
        coordinate_x=1400,
        coordinate_y=100,
    )

    _connect(start, [main_nodes["TASK_PERIODS"]])
    _connect(
        main_nodes["TASK_PERIODS"],
        [main_nodes["TASK_ATENCIONES_PREVIOUS"]],
    )
    _connect(
        main_nodes["TASK_ATENCIONES_PREVIOUS"],
        [
            main_nodes["TASK_ATENCIONES_CURRENT"],
            notify_nodes["TASK_ATENCIONES_PREVIOUS"],
        ],
    )
    _connect(
        main_nodes["TASK_ATENCIONES_CURRENT"],
        [
            main_nodes["TASK_AGENDAMIENTOS_PREVIOUS"],
            notify_nodes["TASK_ATENCIONES_CURRENT"],
        ],
    )
    _connect(
        main_nodes["TASK_AGENDAMIENTOS_PREVIOUS"],
        [
            main_nodes["TASK_AGENDAMIENTOS_CURRENT"],
            notify_nodes["TASK_AGENDAMIENTOS_PREVIOUS"],
        ],
    )
    _connect(
        main_nodes["TASK_AGENDAMIENTOS_CURRENT"],
        [
            main_nodes["TASK_VALIDATE"],
            notify_nodes["TASK_AGENDAMIENTOS_CURRENT"],
        ],
    )
    _connect(main_nodes["TASK_VALIDATE"], [end])
    # A processing failure remains a failed task outcome. The notification
    # operator records the error, then converges on the sole terminal node.
    for notify_node in notify_nodes.values():
        _connect(notify_node, [end])

    nodes = [
        start,
        *main_nodes.values(),
        *notify_nodes.values(),
        end,
    ]
    return {
        "description": (
            "Pentaho Sucursales topology with mock REST boundaries and "
            "processing-stage notification branches"
        ),
        "identifier": "PL_HABITAT_SUCURSALES",
        "key": pipeline_key,
        "modelType": "PIPELINE",
        "modelVersion": PIPELINE_MODEL_VERSION,
        "name": "PL_HABITAT_SUCURSALES",
        "nestedDepth": 0,
        "nodes": nodes,
        "objectStatus": 8,
        "objectVersion": 1,
        "parameters": [
            _parameter(pipeline_key, "MOCK_BASE_URL"),
            _parameter(pipeline_key, "AS_OF_DATE"),
        ],
        "metadata": _child_metadata(project),
    }


def _pipeline_task_object(
    project: dict[str, object], pipeline: dict[str, object]
) -> dict[str, object]:
    task_key = _key("pipeline-task:TASK_RUN_HABITAT_SUCURSALES")
    task_parameters = [
        _parameter(task_key, "MOCK_BASE_URL"),
        _parameter(task_key, "AS_OF_DATE"),
    ]
    return {
        "configProviderDelegate": {
            "bindings": {
                parameter["key"]: {
                    "simpleValue": f"${{{parameter['name']}}}"
                }
                for parameter in pipeline["parameters"]
            }
        },
        "description": "Runnable task for the Habitat Sucursales pipeline",
        "identifier": "TASK_RUN_HABITAT_SUCURSALES",
        "inputPorts": [],
        "isConcurrentAllowed": False,
        "key": task_key,
        "modelType": "PIPELINE_TASK",
        "modelVersion": REST_MODEL_VERSION,
        "name": "TASK_RUN_HABITAT_SUCURSALES",
        "objectStatus": 8,
        "objectVersion": 1,
        "outputPorts": [],
        "parameters": task_parameters,
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
        "metadata": _child_metadata(project),
    }


def _object_path(item: dict[str, object]) -> str:
    return (
        f"Objects/{item['modelType']}_{_identifier(str(item['identifier']))}_"
        f"{item['key']}.json"
    )


def build_export_documents() -> dict[str, dict[str, object]]:
    """Build all import-oriented documents without touching the filesystem."""

    project_key = _key("project:HABITAT_SUCURSALES")
    project = _project_object(project_key)
    rest_tasks = {
        identifier: _rest_task_object(project, identifier, route, body)
        for identifier, route, body in TASK_DEFINITIONS
    }
    pipeline = _pipeline_object(project, rest_tasks)
    pipeline_task = _pipeline_task_object(project, pipeline)
    objects = [project, *rest_tasks.values(), pipeline, pipeline_task]
    object_documents = {
        _object_path(item): item for item in objects
    }
    manifest = {
        "exportedWorkspaceOcid": "",
        "modelVersionMap": {
            "257": "20200901",
            "788": PIPELINE_MODEL_VERSION,
            "17230268181": REST_MODEL_VERSION,
        },
        "objectKeysProvidedForExport": [project["key"]],
        "objects": [f"/{path}" for path in object_documents],
        "referencedObjectsList": [],
        "version": "V1",
    }
    return {"manifest.json": manifest, **object_documents}


def write_export(export_dir: Path | str) -> Path:
    """Write the deterministic OCI object directory."""

    export_path = Path(export_dir)
    if export_path.suffix != ".project":
        raise ValueError("export directory must use the .project suffix")
    documents = build_export_documents()
    for relative_path, document in documents.items():
        destination = export_path / relative_path
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(
            json.dumps(
                document,
                ensure_ascii=False,
                indent=2,
                sort_keys=True,
            )
            + "\n",
            encoding="utf-8",
        )
    return export_path


def package_export(
    export_dir: Path | str, zip_path: Path | str
) -> Path:
    """Create a deterministic ``.project.zip`` from a written export."""

    export_path = Path(export_dir)
    archive_path = Path(zip_path)
    if not archive_path.name.endswith(".project.zip"):
        raise ValueError("OCI project import asset must use the .project.zip suffix")
    manifest_path = export_path / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    relative_paths = [
        "manifest.json",
        *(path.lstrip("/") for path in manifest["objects"]),
    ]
    archive_path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(
        archive_path,
        "w",
        compression=zipfile.ZIP_DEFLATED,
        compresslevel=9,
    ) as archive:
        for relative_path in relative_paths:
            source = export_path / relative_path
            info = zipfile.ZipInfo(relative_path, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            archive.writestr(info, source.read_bytes(), compresslevel=9)
    return archive_path


def sha256_file(path: Path | str) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def package_backend(
    implementation_dir: Path | str, tar_path: Path | str
) -> Path:
    """Create a deterministic, machine-ready mock backend archive."""

    source_root = Path(implementation_dir)
    archive_path = Path(tar_path)
    if not archive_path.name.endswith(".tar.gz"):
        raise ValueError("backend bundle must use the .tar.gz suffix")
    candidates = [
        source_root / "start-mock-backend.sh",
        source_root / "config/pipeline.yaml",
        *source_root.joinpath("habitat_sucursales").glob("*.py"),
        *source_root.joinpath("fixtures/raw").rglob("*"),
    ]
    files = sorted(
        {
            path
            for path in candidates
            if path.is_file()
            and "__pycache__" not in path.parts
            and path.suffix not in {".pyc", ".pyo"}
        },
        key=lambda path: path.relative_to(source_root).as_posix(),
    )
    archive_path.parent.mkdir(parents=True, exist_ok=True)
    with archive_path.open("wb") as raw_stream:
        with gzip.GzipFile(
            filename="", mode="wb", fileobj=raw_stream, mtime=0
        ) as compressed:
            with tarfile.open(fileobj=compressed, mode="w") as archive:
                directory_names = {"implementation"}
                for path in files:
                    relative = Path("implementation") / path.relative_to(
                        source_root
                    )
                    directory_names.update(
                        parent.as_posix()
                        for parent in relative.parents
                        if parent.as_posix() != "."
                    )
                for name in sorted(directory_names):
                    info = tarfile.TarInfo(name)
                    info.type = tarfile.DIRTYPE
                    info.mode = 0o755
                    info.mtime = 0
                    info.uid = 0
                    info.gid = 0
                    info.uname = ""
                    info.gname = ""
                    archive.addfile(info)
                for path in files:
                    relative = (
                        Path("implementation") / path.relative_to(source_root)
                    ).as_posix()
                    info = tarfile.TarInfo(relative)
                    info.size = path.stat().st_size
                    info.mode = (
                        0o755
                        if path.name == "start-mock-backend.sh"
                        else 0o644
                    )
                    info.mtime = 0
                    info.uid = 0
                    info.gid = 0
                    info.uname = ""
                    info.gname = ""
                    with path.open("rb") as stream:
                        archive.addfile(info, stream)
    return archive_path
