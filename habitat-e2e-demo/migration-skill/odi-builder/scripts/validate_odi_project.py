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
    config = obj.get("executeRestCallConfig")
    if not isinstance(config, dict):
        errors.append(f"{filename}: missing executeRestCallConfig")
        return
    values = config.get("configValues", {}).get("configParamValues", {})
    payload = values.get("requestPayload", {}).get("refValue", {})
    if payload.get("modelType") != "JSON_TEXT":
        errors.append(f"{filename}: requestPayload must use JSON_TEXT refValue")

    url = values.get("requestURL", {}).get("stringValue", "")
    parsed = urlparse(url)
    if not url or parsed.scheme not in {"http", "https"}:
        errors.append(f"{filename}: requestURL must be an HTTP template URL")
    elif not (parsed.hostname or "").endswith(".invalid"):
        errors.append(f"{filename}: tracked requestURL must use a .invalid host")


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
