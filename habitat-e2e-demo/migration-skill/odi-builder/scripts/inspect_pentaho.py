#!/usr/bin/env python3
"""Create a deterministic, secret-safe inventory of Pentaho KJB/KTR XML."""

from __future__ import annotations

import argparse
import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any


SECRET_NAME = re.compile(
    r"(?:pass(?:word|wd)?|secret|token|credential|private.?key|access.?key|"
    r"user(?:name)?|server|host|database|jndi)",
    re.IGNORECASE,
)
SENSITIVE_VALUE = re.compile(
    r"(?:ocid1\.|https?://|BEGIN [A-Z ]*PRIVATE KEY|"
    r"(?:^|[^0-9])(?:[0-9]{1,3}\.){3}[0-9]{1,3}(?:$|[^0-9])|"
    r"[^@\s]+@[^@\s]+)",
    re.IGNORECASE,
)
VARIABLE_TOKEN = re.compile(r"\$\{[^}]+\}")


def text(element: ET.Element | None, name: str) -> str:
    if element is None:
        return ""
    value = element.findtext(name)
    return value.strip() if value else ""


def safe_value(name: str, value: str) -> str:
    if value and (SECRET_NAME.search(name) or SENSITIVE_VALUE.search(value)):
        return "<redacted>"
    return value


def named_values(parent: ET.Element, path: str) -> list[dict[str, str]]:
    values: list[dict[str, str]] = []
    for element in parent.findall(path):
        name = text(element, "name") or element.tag
        value = text(element, "value") or (element.text or "").strip()
        values.append({"name": name, "value": safe_value(name, value)})
    return sorted(values, key=lambda item: (item["name"], item["value"]))


def connection_inventory(root: ET.Element) -> list[dict[str, str]]:
    result: list[dict[str, str]] = []
    for connection in root.findall(".//connection"):
        name = text(connection, "name")
        if not name:
            continue
        result.append(
            {
                "name": name,
                "type": text(connection, "type"),
                "access": text(connection, "access"),
                "server": safe_value("server", text(connection, "server")),
                "database": safe_value("database", text(connection, "database")),
                "username": safe_value("username", text(connection, "username")),
                "password": safe_value("password", text(connection, "password")),
            }
        )
    return sorted(result, key=lambda item: item["name"])


def variable_tokens(root: ET.Element) -> list[str]:
    tokens: set[str] = set()
    for element in root.iter():
        value = (element.text or "").strip()
        tokens.update(VARIABLE_TOKEN.findall(value))
    return sorted(tokens)


def referenced_files(root: ET.Element) -> list[str]:
    references: set[str] = set()
    tags = {
        "filename",
        "file_name",
        "jobfilename",
        "transfilename",
        "script",
        "sql",
    }
    for element in root.iter():
        tag = element.tag.rsplit("}", 1)[-1].lower()
        value = (element.text or "").strip()
        if tag not in tags or not value or SECRET_NAME.search(tag):
            continue
        if tag in {"script", "sql"} and "\n" in value:
            continue
        references.add(
            f"<absolute>/{Path(value).name}" if Path(value).is_absolute() else value
        )
    return sorted(references)


def hop_inventory(root: ET.Element) -> list[dict[str, str]]:
    hops: list[dict[str, str]] = []
    for hop in root.findall(".//hops/hop"):
        hops.append(
            {
                "from": text(hop, "from"),
                "to": text(hop, "to"),
                "enabled": text(hop, "enabled"),
                "evaluation": text(hop, "evaluation"),
                "unconditional": text(hop, "unconditional"),
            }
        )
    return sorted(
        hops,
        key=lambda item: (
            item["from"],
            item["to"],
            item["evaluation"],
            item["unconditional"],
        ),
    )


def job_inventory(root: ET.Element) -> dict[str, Any]:
    entries: list[dict[str, str]] = []
    for entry in root.findall(".//entries/entry"):
        entries.append(
            {
                "name": text(entry, "name"),
                "type": text(entry, "type"),
                "filename": text(entry, "filename")
                or text(entry, "jobfilename")
                or text(entry, "transfilename"),
            }
        )
    return {
        "name": text(root, "name"),
        "entries": sorted(entries, key=lambda item: (item["name"], item["type"])),
        "hops": hop_inventory(root),
    }


def transformation_inventory(root: ET.Element) -> dict[str, Any]:
    steps: list[dict[str, str]] = []
    for step in root.findall(".//step"):
        steps.append(
            {
                "name": text(step, "name"),
                "type": text(step, "type"),
                "description": text(step, "description"),
            }
        )
    order = root.find(".//order")
    hops: list[dict[str, str]] = []
    if order is not None:
        for hop in order.findall("hop"):
            hops.append(
                {
                    "from": text(hop, "from"),
                    "to": text(hop, "to"),
                    "enabled": text(hop, "enabled"),
                }
            )
    return {
        "name": text(root, "name"),
        "steps": sorted(steps, key=lambda item: (item["name"], item["type"])),
        "hops": sorted(hops, key=lambda item: (item["from"], item["to"])),
    }


def inspect_file(path: Path, source_root: Path) -> dict[str, Any]:
    try:
        root = ET.parse(path).getroot()
    except ET.ParseError as exc:
        return {
            "path": path.relative_to(source_root).as_posix(),
            "kind": path.suffix.lower().lstrip("."),
            "parse_error": str(exc),
        }

    kind = path.suffix.lower()
    document = job_inventory(root) if kind == ".kjb" else transformation_inventory(root)
    document.update(
        {
            "path": path.relative_to(source_root).as_posix(),
            "kind": kind.lstrip("."),
            "parameters": named_values(root, ".//parameters/parameter"),
            "variables": variable_tokens(root),
            "connections": connection_inventory(root),
            "referenced_files": referenced_files(root),
        }
    )
    return document


def inspect(source_root: Path) -> dict[str, Any]:
    paths = sorted(
        path
        for path in source_root.rglob("*")
        if path.is_file() and path.suffix.lower() in {".kjb", ".ktr"}
    )
    documents = [inspect_file(path, source_root) for path in paths]
    referenced = {
        item
        for document in documents
        for item in document.get("referenced_files", [])
        if item
    }
    return {
        "source_root": ".",
        "document_count": len(documents),
        "jobs": sum(document.get("kind") == "kjb" for document in documents),
        "transformations": sum(
            document.get("kind") == "ktr" for document in documents
        ),
        "referenced_files": sorted(referenced),
        "documents": documents,
    }


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source_root", type=Path, help="Read-only Pentaho source root")
    parser.add_argument(
        "--output",
        type=Path,
        help="Write deterministic JSON here; stdout when omitted",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    source_root = args.source_root.resolve()
    if not source_root.is_dir():
        raise SystemExit(f"source root is not a directory: {source_root}")

    payload = json.dumps(inspect(source_root), indent=2, sort_keys=True) + "\n"
    if args.output:
        output = args.output.resolve()
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(payload, encoding="utf-8")
    else:
        sys.stdout.write(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
