#!/usr/bin/env bash
set -euo pipefail

PORT="${1:?usage: start-mock-backend.sh PORT [OUTPUT_DIR]}"
OUTPUT_DIR="${2:-output}"
HOST="${MOCK_BIND_HOST:-0.0.0.0}"
PYTHON_BIN="${MOCK_PYTHON_BIN:?set MOCK_PYTHON_BIN to an executable Python path}"

[[ "${PORT}" =~ ^[0-9]+$ ]] || {
  echo "PORT must be numeric" >&2
  exit 2
}
[[ -d fixtures ]] || {
  echo "fixtures directory is missing" >&2
  exit 2
}
mkdir -p "${OUTPUT_DIR}"

exec "${PYTHON_BIN}" -m habitat_web.mock_server \
  --host "${HOST}" \
  --port "${PORT}" \
  --fixtures fixtures \
  --output "${OUTPUT_DIR}"
