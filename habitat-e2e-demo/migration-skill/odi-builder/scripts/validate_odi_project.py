#!/usr/bin/env python3
"""Validate a canonical OCI Data Integration .project directory or ZIP."""

from __future__ import annotations

import argparse
import json
import re
import sys
import zipfile
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any, Callable
from urllib.parse import urlparse


SECRET_PATTERN = re.compile(
    r"(BEGIN [A-Z ]*PRIVATE KEY|ocid1\.|password\s*[:=]|client_secret\s*[:=])",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class ProjectData:
    root_name: str
    names: set[str]
    read_text: Callable[[str], str]
    is_zip: bool
    archive_names: frozenset[str]


def open_directory(path: Path) -> ProjectData:
    root = path.resolve()
    names = {
        child.relative_to(root).as_posix() + ("/" if child.is_dir() else "")
        for child in root.rglob("*")
    }

    def read_text(name: str) -> str:
        return (root / name).read_text(encoding="utf-8")

    return ProjectData(root.name, names, read_text, False, frozenset())


def safe_zip_names(archive: zipfile.ZipFile) -> list[str]:
    names = archive.namelist()
    for name in names:
        pure = PurePosixPath(name)
        if pure.is_absolute() or ".." in pure.parts:
            raise ValueError(f"unsafe ZIP member: {name}")
    return names


def open_zip(path: Path) -> tuple[ProjectData, zipfile.ZipFile]:
    archive = zipfile.ZipFile(path)
    names = safe_zip_names(archive)
    roots = {PurePosixPath(name).parts[0] for name in names if name}
    if len(roots) != 1:
        archive.close()
        raise ValueError("ZIP must contain exactly one top-level project directory")
    root_name = roots.pop()
    prefix = f"{root_name}/"
    relative_names = {
        name[len(prefix) :]
        for name in names
        if name.startswith(prefix) and name != prefix
    }

    def read_text(name: str) -> str:
        return archive.read(prefix + name).decode("utf-8")

    return (
        ProjectData(root_name, relative_names, read_text, True, frozenset(names)),
        archive,
    )


def load_project(path: Path) -> tuple[ProjectData, zipfile.ZipFile | None]:
    if path.is_dir():
        return open_directory(path), None
    if not path.is_file() or not zipfile.is_zipfile(path):
        raise ValueError("input must be a .project directory or readable ZIP")
    return open_zip(path)


def json_object(data: ProjectData, name: str, errors: list[str]) -> dict[str, Any]:
    try:
        value = json.loads(data.read_text(name))
    except (KeyError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        errors.append(f"{name}: invalid JSON: {exc}")
        return {}
    if not isinstance(value, dict):
        errors.append(f"{name}: root JSON value must be an object")
        return {}
    return value


def validate_rest_task(obj: dict[str, Any], filename: str, errors: list[str]) -> None:
    if obj.get("apiCallMode") != "SYNCHRONOUS":
        errors.append(f"{filename}: apiCallMode must be SYNCHRONOUS")
    for field in ("inputPorts", "outputPorts"):
        if obj.get(field) != []:
            errors.append(f"{filename}: {field} must be an empty list")
    if obj.get("objectVersion") != 1:
        errors.append(f"{filename}: objectVersion must be 1")
    config = obj.get("executeRestCallConfig")
    if not isinstance(config, dict):
        errors.append(f"{filename}: missing executeRestCallConfig")
        return
    if config.get("methodType") != "POST":
        errors.append(f"{filename}: executeRestCallConfig.methodType must be POST")
    if config.get("requestHeaders") != {"Content-Type": "application/json"}:
        errors.append(
            f"{filename}: executeRestCallConfig.requestHeaders must declare JSON"
        )
    config_values = config.get("configValues")
    if not isinstance(config_values, dict):
        errors.append(f"{filename}: missing executeRestCallConfig.configValues")
        return
    if config_values.get("parentRef") != {"parent": obj.get("key")}:
        errors.append(
            f"{filename}: executeRestCallConfig parentRef must reference the task"
        )
    values = config_values.get("configParamValues")
    if not isinstance(values, dict):
        errors.append(f"{filename}: missing REST configParamValues")
        return
    if set(values) != {"requestPayload", "requestURL"}:
        errors.append(
            f"{filename}: REST configParamValues must contain only "
            "requestPayload and requestURL"
        )
    payload = values.get("requestPayload", {}).get("refValue", {})
    if payload.get("modelType") != "JSON_TEXT":
        errors.append(f"{filename}: requestPayload must use JSON_TEXT refValue")

    url = values.get("requestURL", {}).get("stringValue", "")
    parsed = urlparse(url)
    if not url or parsed.scheme not in {"http", "https"}:
        errors.append(f"{filename}: requestURL must be an HTTP template URL")
    elif not (parsed.hostname or "").endswith(".invalid"):
        errors.append(f"{filename}: tracked requestURL must use a .invalid host")


def validate_pipeline(
    obj: dict[str, Any], filename: str, errors: list[str]
) -> None:
    if obj.get("nestedDepth") != 0:
        errors.append(f"{filename}: PIPELINE nestedDepth must be 0")
    if obj.get("objectVersion") != 1:
        errors.append(f"{filename}: PIPELINE objectVersion must be 1")
    if "variables" in obj:
        errors.append(f"{filename}: PIPELINE must not contain variables")
    nodes = obj.get("nodes")
    if not isinstance(nodes, list) or len(nodes) < 2:
        errors.append(f"{filename}: PIPELINE must contain START and END flow nodes")
        return

    input_links: dict[str, dict[str, Any]] = {}
    output_links: dict[str, dict[str, Any]] = {}
    for index, node in enumerate(nodes):
        location = f"{filename}: node[{index}]"
        if not isinstance(node, dict):
            errors.append(f"{location} must be an object")
            continue
        if node.get("modelType") != "FLOW_NODE":
            errors.append(
                f"{location} must use a FLOW_NODE wrapper; flat operators are invalid"
            )
            continue
        node_key = node.get("key")
        if node.get("parentRef") != {"parent": obj.get("key")}:
            errors.append(f"{location} parentRef must reference the PIPELINE")
        operator = node.get("operator")
        if not isinstance(operator, dict):
            errors.append(f"{location} is missing its operator")
            continue
        expected_type = (
            "START_OPERATOR"
            if index == 0
            else "END_OPERATOR"
            if index == len(nodes) - 1
            else "TASK_OPERATOR"
        )
        if operator.get("modelType") != expected_type:
            errors.append(f"{location} operator must be {expected_type}")
        if operator.get("parentRef") != {"parent": node_key}:
            errors.append(f"{location} operator parentRef must reference its node")
        if expected_type == "TASK_OPERATOR":
            task = operator.get("task")
            if not isinstance(task, dict):
                errors.append(f"{location} TASK_OPERATOR is missing its task stub")
            else:
                for field, expected in (
                    ("inputPorts", []),
                    ("outputPorts", []),
                    ("parameters", []),
                    ("objectStatus", 1),
                    ("objectVersion", 1),
                ):
                    if task.get(field) != expected:
                        errors.append(
                            f"{location} task stub {field} must be {expected!r}"
                        )

        node_inputs = node.get("inputLinks")
        node_outputs = node.get("outputLinks")
        if not isinstance(node_inputs, list) or not isinstance(node_outputs, list):
            errors.append(f"{location} inputLinks and outputLinks must be lists")
            continue
        if index == 0 and node_inputs:
            errors.append(f"{location} START must not have input links")
        if index > 0 and not node_inputs:
            errors.append(f"{location} must have an input link")
        if index == len(nodes) - 1 and node_outputs:
            errors.append(f"{location} END must not have output links")
        if index < len(nodes) - 1 and not node_outputs:
            errors.append(f"{location} must have an output link")
        for link in node_inputs:
            if not isinstance(link, dict):
                errors.append(f"{location} contains an invalid input link")
                continue
            if (
                link.get("modelType") != "INPUT_LINK"
                or link.get("parentRef") != {"parent": node_key}
            ):
                errors.append(f"{location} contains a malformed INPUT_LINK")
            if isinstance(link.get("key"), str):
                input_links[link["key"]] = link
        for link in node_outputs:
            if not isinstance(link, dict):
                errors.append(f"{location} contains an invalid output link")
                continue
            if (
                link.get("modelType") != "OUTPUT_LINK"
                or link.get("parentRef") != {"parent": node_key}
                or not isinstance(link.get("toLinks"), list)
            ):
                errors.append(f"{location} contains a malformed OUTPUT_LINK")
            if isinstance(link.get("key"), str):
                output_links[link["key"]] = link

    for input_key, input_link in input_links.items():
        output_key = input_link.get("fromLink")
        output_link = output_links.get(output_key)
        if output_link is None or input_key not in output_link.get("toLinks", []):
            errors.append(
                f"{filename}: INPUT_LINK {input_key} lacks a reciprocal OUTPUT_LINK"
            )
    for output_key, output_link in output_links.items():
        for input_key in output_link.get("toLinks", []):
            input_link = input_links.get(input_key)
            if input_link is None or input_link.get("fromLink") != output_key:
                errors.append(
                    f"{filename}: OUTPUT_LINK {output_key} lacks a reciprocal INPUT_LINK"
                )


def validate_pipeline_task(
    obj: dict[str, Any], filename: str, errors: list[str]
) -> None:
    for field, expected in (
        ("inputPorts", []),
        ("outputPorts", []),
        ("objectVersion", 1),
    ):
        if obj.get(field) != expected:
            errors.append(f"{filename}: PIPELINE_TASK {field} must be {expected!r}")
    pipeline = obj.get("pipeline")
    if not isinstance(pipeline, dict):
        errors.append(f"{filename}: PIPELINE_TASK is missing its pipeline stub")
        return
    for field, expected in (
        ("modelType", "PIPELINE"),
        ("nestedDepth", 0),
        ("nodes", []),
        ("objectStatus", 1),
        ("objectVersion", 1),
        ("parameters", []),
    ):
        if pipeline.get(field) != expected:
            errors.append(
                f"{filename}: pipeline stub {field} must be {expected!r}"
            )


def validate(data: ProjectData) -> list[str]:
    errors: list[str] = []
    if not data.root_name.endswith(".project"):
        errors.append("top-level directory must end with .project")
    if data.is_zip:
        archive_root = f"{data.root_name}/"
        archive_objects = f"{data.root_name}/Objects/"
        if archive_root not in data.archive_names:
            errors.append("ZIP is missing explicit top-level .project directory entry")
        if archive_objects not in data.archive_names:
            errors.append("ZIP is missing explicit Objects/ directory entry")
    if "manifest.json" not in data.names:
        return errors + ["manifest.json is missing"]
    if "Objects/" not in data.names and not any(
        name.startswith("Objects/") for name in data.names
    ):
        errors.append("Objects/ directory is missing")

    manifest = json_object(data, "manifest.json", errors)
    if manifest.get("version") != "V1":
        errors.append("manifest.version must be V1")
    if manifest.get("exportedWorkspaceOcid") != "":
        errors.append("manifest.exportedWorkspaceOcid must be empty")
    exported_keys = manifest.get("objectKeysProvidedForExport")
    if not isinstance(exported_keys, list) or len(exported_keys) != 1:
        errors.append("objectKeysProvidedForExport must contain one USER_PROJECT key")
        exported_keys = []
    if not isinstance(manifest.get("referencedObjectsList"), list):
        errors.append("referencedObjectsList must be a list")
    if not isinstance(manifest.get("modelVersionMap"), dict):
        errors.append("modelVersionMap must be an object")

    manifest_paths = manifest.get("objects")
    if not isinstance(manifest_paths, list):
        errors.append("manifest.objects must be a list")
        manifest_paths = []

    if manifest_paths:
        first_path = manifest_paths[0]
        if not isinstance(first_path, str) or "/USER_PROJECT_" not in first_path:
            errors.append("manifest.objects must list USER_PROJECT first")

    objects: list[tuple[str, dict[str, Any]]] = []
    for manifest_path in manifest_paths:
        if not isinstance(manifest_path, str) or not manifest_path.startswith(
            "/Objects/"
        ):
            errors.append(f"invalid manifest object path: {manifest_path!r}")
            continue
        relative = manifest_path.lstrip("/")
        if relative not in data.names:
            errors.append(f"manifest object is missing: {relative}")
            continue
        objects.append((relative, json_object(data, relative, errors)))

    keys: dict[str, str] = {}
    projects: list[tuple[str, dict[str, Any]]] = []
    for filename, obj in objects:
        key = obj.get("key")
        if not isinstance(key, str) or not key:
            errors.append(f"{filename}: missing key")
        elif key in keys:
            errors.append(f"{filename}: duplicate object key also used by {keys[key]}")
        else:
            keys[key] = filename
        if isinstance(key, str) and not filename.endswith(f"_{key}.json"):
            errors.append(f"{filename}: filename must end with exact object key")
        identifier = obj.get("identifier")
        if isinstance(identifier, str) and f"_{identifier}_{key}.json" not in filename:
            errors.append(f"{filename}: filename must include exact object identifier")
        if obj.get("objectStatus") != 8:
            errors.append(f"{filename}: first-class objectStatus must be 8")
        if obj.get("modelType") == "USER_PROJECT":
            projects.append((filename, obj))

    if len(projects) != 1:
        errors.append("archive must export exactly one USER_PROJECT")
        return errors
    project_filename, project = projects[0]
    project_key = project.get("key")
    if exported_keys and exported_keys[0] != project_key:
        errors.append("objectKeysProvidedForExport must contain the USER_PROJECT key")
    if project.get("metadata") != {"registryVersion": 1}:
        errors.append(f"{project_filename}: invalid USER_PROJECT metadata")

    for filename, obj in objects:
        if obj.get("modelType") == "USER_PROJECT":
            continue
        metadata = obj.get("metadata")
        if not isinstance(metadata, dict):
            errors.append(f"{filename}: missing child metadata")
            continue
        if metadata.get("aggregatorKey") != project_key:
            errors.append(f"{filename}: aggregatorKey does not match USER_PROJECT")
        aggregator = metadata.get("aggregator")
        if not isinstance(aggregator, dict) or aggregator.get("key") != project_key:
            errors.append(f"{filename}: aggregator does not match USER_PROJECT")
        if metadata.get("registryVersion") != 1:
            errors.append(f"{filename}: registryVersion must be 1")
        if "parentRef" in obj or "registryMetadata" in obj:
            errors.append(f"{filename}: first-class child has invalid top-level registry data")

        model_type = obj.get("modelType")
        if model_type in {"REST_TASK", "PIPELINE", "PIPELINE_TASK"}:
            if obj.get("parameters") != []:
                errors.append(f"{filename}: {model_type} must be parameter-free")
        if model_type == "REST_TASK":
            validate_rest_task(obj, filename, errors)
        elif model_type == "PIPELINE":
            validate_pipeline(obj, filename, errors)
        elif model_type == "PIPELINE_TASK":
            validate_pipeline_task(obj, filename, errors)

    serialized = "\n".join(data.read_text(name) for name in sorted(data.names) if name.endswith(".json"))
    if SECRET_PATTERN.search(serialized):
        errors.append("project contains a secret, credential assignment, or OCID")
    return errors


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project", type=Path)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    archive: zipfile.ZipFile | None = None
    try:
        data, archive = load_project(args.project.resolve())
        errors = validate(data)
    except (OSError, ValueError, zipfile.BadZipFile) as exc:
        errors = [str(exc)]
    finally:
        if archive is not None:
            archive.close()

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(f"VALID {args.project}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
