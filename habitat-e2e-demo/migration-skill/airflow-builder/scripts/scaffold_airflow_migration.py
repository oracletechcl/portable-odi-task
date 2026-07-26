#!/usr/bin/env python3
"""Create the isolated layout required for one Airflow migration."""
from __future__ import annotations
import argparse
import shutil
from pathlib import Path

def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("--output-root", type=Path, required=True); parser.add_argument("--spec", type=Path, required=True); args = parser.parse_args()
    root = args.output_root.resolve(); spec = args.spec.resolve()
    if not spec.is_file(): raise SystemExit(f"spec not found: {spec}")
    if root.exists() and any(root.iterdir()): raise SystemExit(f"output root must be empty: {root}")
    assets = Path(__file__).resolve().parent.parent / "assets"
    for relative in ("implementation", "implementation/tests", "dags", "analysis", "spec", "docs", "expected-output", "platforms/airflow/scripts"):
        (root / relative).mkdir(parents=True, exist_ok=True)
    for source, destination in (("deploy.sh.template", "deploy.sh"), ("deploy-internal.sh.template", "platforms/airflow/scripts/deploy-internal.sh"), ("deployment.env.example", ".deploy.env.example")):
        target = root / destination; target.write_text((assets / source).read_text(encoding="utf-8"), encoding="utf-8"); target.chmod(0o755 if target.suffix == ".sh" else 0o644)
    shutil.copyfile(spec, root / "spec" / "approved-spec.md")
    print(root)
    return 0
if __name__ == "__main__": raise SystemExit(main())
