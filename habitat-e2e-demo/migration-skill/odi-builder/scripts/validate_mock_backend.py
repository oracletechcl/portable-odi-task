#!/usr/bin/env python3
"""Validate whether a migration has the mock assets required to run."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

RUNTIME_SUFFIXES = {
    ".go",
    ".java",
    ".js",
    ".php",
    ".py",
    ".rb",
    ".sh",
    ".ts",
}


def existing_directory(value: str) -> Path:
    path = Path(value).expanduser().resolve()
    if not path.is_dir():
        raise argparse.ArgumentTypeError(f"directory does not exist: {path}")
    return path


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--migration-root",
        type=existing_directory,
        required=True,
    )
    parser.add_argument(
        "--required",
        choices=("yes", "no"),
        required=True,
        help="Explicit mock decision derived from source and environment evidence",
    )
    parser.add_argument(
        "--compute-vm",
        action="store_true",
        help="Require Compute VM deployment and systemd assets",
    )
    parser.add_argument(
        "--release",
        action="store_true",
        help="Require a checksummed immutable mock release archive",
    )
    return parser.parse_args(argv)


def useful_files(root: Path) -> list[Path]:
    if not root.is_dir():
        return []
    return sorted(
        path
        for path in root.rglob("*")
        if path.is_file()
        and path.name != ".gitkeep"
        and "__pycache__" not in path.parts
    )


def readable_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return ""


def valid_release_checksum(archive: Path) -> bool:
    checksum = archive.with_name(f"{archive.name}.sha256")
    if not checksum.is_file():
        return False
    fields = checksum.read_text(encoding="utf-8").split()
    if not fields:
        return False
    return hashlib.sha256(archive.read_bytes()).hexdigest() == fields[0]


def assess(args: argparse.Namespace) -> dict[str, object]:
    required = args.required == "yes"
    result: dict[str, object] = {
        "compute_vm": args.compute_vm,
        "migration_root": str(args.migration_root),
        "missing": [],
        "release": args.release,
        "required": required,
        "status": "NOT_REQUIRED",
    }
    if not required:
        return result

    root: Path = args.migration_root
    missing: list[str] = []
    contract = root / "analysis" / "mock-contract.md"
    implementation = root / "implementation"
    wrapper = implementation / "start-mock-backend.sh"
    fixtures = useful_files(implementation / "fixtures")
    tests = [
        path
        for path in useful_files(implementation / "tests")
        if path.name.startswith("test")
    ]
    runtime_sources = [
        path
        for path in useful_files(implementation)
        if path.suffix in RUNTIME_SUFFIXES
        and "tests" not in path.parts
        and "fixtures" not in path.parts
        and path != wrapper
    ]
    runtime_corpus = "\n".join(readable_text(path) for path in runtime_sources)
    readme = root / "README.md"
    readme_text = readable_text(readme).lower()

    if not contract.is_file():
        missing.append("analysis/mock-contract.md")
    if not wrapper.is_file():
        missing.append("implementation/start-mock-backend.sh")
    elif "set -euo pipefail" not in readable_text(wrapper):
        missing.append("start wrapper strict mode")
    if not fixtures:
        missing.append("implementation fixture data")
    if not tests:
        missing.append("mock route tests")
    if not runtime_sources:
        missing.append("mock runtime implementation")
    if "/health" not in runtime_corpus:
        missing.append("GET /health contract")
    if not (
        readme.is_file()
        and "mock" in readme_text
        and "start-mock-backend.sh" in readme_text
        and "/health" in readme_text
    ):
        missing.append("operator README mock runbook")

    if args.compute_vm:
        root_deployer = root / "deploy.sh"
        deploy_scripts = sorted(
            (root / "platforms" / "oci" / "scripts").glob("*.sh")
        )
        service_units = sorted(
            (root / "platforms" / "oci" / "systemd").glob("*.service*")
        )
        if not root_deployer.is_file():
            missing.append("app-root one-stop deploy.sh")
        elif "set -euo pipefail" not in readable_text(root_deployer):
            missing.append("app-root one-stop deploy.sh strict mode")
        if not deploy_scripts:
            missing.append("Compute VM deployment script")
        elif not all(
            "set -euo pipefail" in readable_text(path)
            for path in deploy_scripts
        ):
            missing.append("Compute VM deployment script strict mode")
        if not service_units:
            missing.append("Compute VM systemd unit")

    if args.release:
        archives = sorted((root / "target").glob("*-mock-backend-*.tar.gz"))
        if not archives:
            missing.append("mock release archive")
        if not archives or not any(
            valid_release_checksum(archive) for archive in archives
        ):
            missing.append("mock release SHA-256")

    result["missing"] = missing
    result["status"] = "MISSING" if missing else "READY"
    return result


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    result = assess(args)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 1 if result["status"] == "MISSING" else 0


if __name__ == "__main__":
    raise SystemExit(main())
