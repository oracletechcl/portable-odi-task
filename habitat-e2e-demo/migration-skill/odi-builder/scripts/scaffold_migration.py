#!/usr/bin/env python3
"""Create an isolated Pentaho-to-OCI migration workspace from bundled templates."""

from __future__ import annotations

import argparse
import re
import shutil
import sys
from pathlib import Path


IDENTIFIER = re.compile(r"^[A-Z][A-Z0-9_]{1,127}$")
VERSION = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+(?:[-+][A-Za-z0-9.-]+)?$")


def required_path(value: str) -> Path:
    path = Path(value).expanduser().resolve()
    if not path.exists():
        raise argparse.ArgumentTypeError(f"path does not exist: {path}")
    return path


def identifier(value: str) -> str:
    if not IDENTIFIER.fullmatch(value):
        raise argparse.ArgumentTypeError(
            "identifier must start with A-Z and contain only A-Z, 0-9, or _"
        )
    return value


def version(value: str) -> str:
    if not VERSION.fullmatch(value):
        raise argparse.ArgumentTypeError("release version must be semantic X.Y.Z")
    return value


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--spec", type=required_path, required=True)
    parser.add_argument("--source-root", type=required_path, required=True)
    parser.add_argument("--canonical-project", type=required_path, required=True)
    parser.add_argument("--project-name", required=True)
    parser.add_argument("--project-identifier", type=identifier, required=True)
    parser.add_argument("--pipeline-name", required=True)
    parser.add_argument("--pipeline-identifier", type=identifier, required=True)
    parser.add_argument("--task-name", required=True)
    parser.add_argument("--task-identifier", type=identifier, required=True)
    parser.add_argument("--release-version", type=version, required=True)
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the planned paths without creating anything",
    )
    return parser.parse_args(argv)


def replacements(args: argparse.Namespace) -> dict[str, str]:
    return {
        "{{PROJECT_NAME}}": args.project_name,
        "{{PROJECT_IDENTIFIER}}": args.project_identifier,
        "{{PIPELINE_NAME}}": args.pipeline_name,
        "{{PIPELINE_IDENTIFIER}}": args.pipeline_identifier,
        "{{TASK_NAME}}": args.task_name,
        "{{TASK_IDENTIFIER}}": args.task_identifier,
        "{{RELEASE_VERSION}}": args.release_version,
    }


def render(template: Path, values: dict[str, str]) -> str:
    content = template.read_text(encoding="utf-8")
    for token, value in values.items():
        content = content.replace(token, value)
    return content


def planned_files(output_root: Path) -> list[Path]:
    return [
        output_root / "analysis" / "behavior-contract.md",
        output_root / "analysis" / "gap-register.md",
        output_root / "analysis" / "source-to-target-traceability.md",
        output_root / "spec" / "migration-spec.md",
        output_root / "implementation" / ".gitkeep",
        output_root / "implementation" / "tests" / ".gitkeep",
        output_root / "platforms" / "oci" / "scripts" / ".gitkeep",
        output_root / "platforms" / "oci" / "deployment.env.example",
        output_root / "target" / ".gitkeep",
        output_root / "expected-output" / ".gitkeep",
        output_root / "docs" / "tdd-evidence.md",
        output_root / "README.md",
        output_root / "source-evidence" / "approved-spec.md",
    ]


def write_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def scaffold(args: argparse.Namespace) -> list[Path]:
    output_root = args.output_root.expanduser().resolve()
    files = planned_files(output_root)
    if args.dry_run:
        return files

    if output_root.exists() and any(output_root.iterdir()):
        raise SystemExit(f"output root must be absent or empty: {output_root}")
    output_root.mkdir(parents=True, exist_ok=True)

    skill_root = Path(__file__).resolve().parent.parent
    assets = skill_root / "assets"
    values = replacements(args)

    write_file(
        output_root / "spec" / "migration-spec.md",
        render(assets / "migration-spec.template.md", values),
    )
    write_file(
        output_root / "analysis" / "source-to-target-traceability.md",
        render(assets / "traceability.template.md", values),
    )
    write_file(
        output_root / "platforms" / "oci" / "deployment.env.example",
        (assets / "deployment.env.example").read_text(encoding="utf-8"),
    )
    write_file(
        output_root / "README.md",
        render(assets / "operator-readme.template.md", values),
    )
    (output_root / "source-evidence").mkdir(parents=True, exist_ok=True)
    shutil.copyfile(args.spec, output_root / "source-evidence" / "approved-spec.md")

    starter_files = {
        output_root / "analysis" / "behavior-contract.md": (
            f"# {args.project_name} Behavior Contract\n\n"
        ),
        output_root / "analysis" / "gap-register.md": (
            f"# {args.project_name} Gap Register\n\n"
        ),
        output_root / "docs" / "tdd-evidence.md": (
            f"# {args.project_name} TDD Evidence\n\n"
        ),
    }
    for path, content in starter_files.items():
        write_file(path, content)

    for placeholder in (
        output_root / "implementation" / ".gitkeep",
        output_root / "implementation" / "tests" / ".gitkeep",
        output_root / "platforms" / "oci" / "scripts" / ".gitkeep",
        output_root / "target" / ".gitkeep",
        output_root / "expected-output" / ".gitkeep",
    ):
        write_file(placeholder, "")

    return files


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    output_root = args.output_root.expanduser().resolve()
    paths = scaffold(args)
    mode = "PLAN" if args.dry_run else "CREATED"
    print(f"{mode} {output_root}")
    for path in paths:
        print(path.relative_to(output_root).as_posix())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
