"""Command-line entrypoint for the portable mock service."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Sequence

from .mock_api import create_server
from .oci_export import (
    package_backend,
    package_export,
    sha256_file,
    write_export,
)


IMPLEMENTATION_ROOT = Path(__file__).resolve().parents[1]


def _environment_path(name: str, fallback: Path) -> Path:
    value = os.environ.get(name)
    return Path(value) if value else fallback


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="habitat-sucursales")
    subparsers = parser.add_subparsers(dest="command", required=True)
    serve = subparsers.add_parser("serve", help="start every mock endpoint")
    serve.add_argument("--host", default=os.environ.get("MOCK_HOST", "127.0.0.1"))
    serve.add_argument(
        "--port", type=int, default=int(os.environ.get("MOCK_PORT", "8080"))
    )
    serve.add_argument(
        "--fixtures-dir",
        type=Path,
        default=_environment_path(
            "MOCK_FIXTURES_DIR", IMPLEMENTATION_ROOT / "fixtures/raw"
        ),
    )
    serve.add_argument(
        "--output-dir",
        type=Path,
        default=_environment_path(
            "MOCK_OUTPUT_DIR", IMPLEMENTATION_ROOT.parent / "target/runtime-output"
        ),
    )
    run = subparsers.add_parser("run", help="run the complete local mock flow")
    run.add_argument("--as-of-date", required=True)
    run.add_argument(
        "--fixtures-dir",
        type=Path,
        default=_environment_path(
            "MOCK_FIXTURES_DIR", IMPLEMENTATION_ROOT / "fixtures/raw"
        ),
    )
    run.add_argument(
        "--output-dir",
        type=Path,
        default=_environment_path(
            "MOCK_OUTPUT_DIR", IMPLEMENTATION_ROOT.parent / "target/runtime-output"
        ),
    )
    run.add_argument("--fail-at")

    package = subparsers.add_parser(
        "package-oci", help="write and package the OCI project import asset"
    )
    package.add_argument("--export-dir", type=Path, required=True)
    package.add_argument("--zip-path", type=Path, required=True)

    backend_package = subparsers.add_parser(
        "package-backend", help="package the machine-ready mock backend"
    )
    backend_package.add_argument(
        "--implementation-dir", type=Path, required=True
    )
    backend_package.add_argument("--tar-path", type=Path, required=True)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "serve":
        try:
            server = create_server(
                args.host,
                args.port,
                fixtures_dir=args.fixtures_dir,
                output_dir=args.output_dir,
            )
        except OSError as exc:
            print(
                f"cannot start mock backend on {args.host}:{args.port}: {exc}",
                file=sys.stderr,
            )
            return 2
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass
        finally:
            server.server_close()
        return 0

    if args.command == "run":
        from habitat_sucursales import run_pipeline

        result = run_pipeline(
            args.as_of_date,
            args.fixtures_dir,
            args.output_dir,
            fail_at=args.fail_at,
        )
        print(json.dumps(result, ensure_ascii=False, sort_keys=True))
        return 0

    if args.command == "package-oci":
        export_dir = write_export(args.export_dir)
        archive = package_export(export_dir, args.zip_path)
        checksum = sha256_file(archive)
        checksum_path = Path(f"{archive}.sha256")
        checksum_path.write_text(
            f"{checksum}  {archive.name}\n", encoding="utf-8"
        )
        print(
            json.dumps(
                {
                    "export_dir": str(export_dir),
                    "sha256": checksum,
                    "sha256_file": str(checksum_path),
                    "zip": str(archive),
                },
                sort_keys=True,
            )
        )
        return 0

    if args.command == "package-backend":
        archive = package_backend(args.implementation_dir, args.tar_path)
        checksum = sha256_file(archive)
        checksum_path = Path(f"{archive}.sha256")
        checksum_path.write_text(
            f"{checksum}  {archive.name}\n", encoding="utf-8"
        )
        print(
            json.dumps(
                {
                    "sha256": checksum,
                    "sha256_file": str(checksum_path),
                    "tar": str(archive),
                },
                sort_keys=True,
            )
        )
        return 0

    raise AssertionError(f"unhandled command: {args.command}")
