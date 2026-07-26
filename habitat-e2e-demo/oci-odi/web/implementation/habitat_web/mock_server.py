from __future__ import annotations

import argparse
from pathlib import Path

from .mock_api import serve


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the Habitat Web mock")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", required=True, type=int)
    parser.add_argument("--fixtures", required=True, type=Path)
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    serve(args.host, args.port, args.fixtures)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
