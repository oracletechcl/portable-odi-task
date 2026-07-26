#!/usr/bin/env python3
"""Reject common unsafe or non-portable Airflow DAG source patterns."""
from __future__ import annotations
import argparse
import ast
import re
from pathlib import Path

FORBIDDEN = re.compile(r"(ocid1\.|BEGIN [A-Z ]*PRIVATE KEY|password\s*[:=])", re.I)

def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("dag", type=Path); parser.add_argument("--dag-id", required=True); args = parser.parse_args()
    source = args.dag.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(args.dag))
    errors = []
    if FORBIDDEN.search(source): errors.append("DAG contains secret-like tracked content")
    if args.dag_id not in source: errors.append("expected DAG ID is absent")
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr in {"get", "post", "request", "urlopen"}:
            if isinstance(node.parent if hasattr(node, "parent") else None, ast.Module): errors.append("network call at DAG parse time")
    if errors:
        for error in errors: print(f"ERROR: {error}")
        return 1
    print(f"VALID {args.dag}"); return 0
if __name__ == "__main__": raise SystemExit(main())
