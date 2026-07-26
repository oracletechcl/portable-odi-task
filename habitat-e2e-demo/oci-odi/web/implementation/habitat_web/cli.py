from __future__ import annotations

import argparse
import json
from pathlib import Path

from .client import JsonHttpClient
from .pipeline import run_pipeline


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the portable Habitat Web flow")
    parser.add_argument("--base-url", required=True)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--run-date", required=True)
    parser.add_argument("--timeout-seconds", required=True, type=float)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    result = run_pipeline(
        client=JsonHttpClient(args.base_url, args.timeout_seconds),
        output_dir=args.output_dir,
        run_date=args.run_date,
    )
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

