#!/usr/bin/env bash
set -euo pipefail

ODI_MOCK_IMPLEMENTATION_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export PYTHONPATH="${ODI_MOCK_IMPLEMENTATION_DIR}${PYTHONPATH:+:${PYTHONPATH}}"

exec "${MOCK_PYTHON_BIN:-python3}" -m habitat_sucursales serve \
  --host "${MOCK_HOST:-127.0.0.1}" \
  --port "${MOCK_PORT:-8080}" \
  --fixtures-dir "${MOCK_FIXTURES_DIR:-${ODI_MOCK_IMPLEMENTATION_DIR}/fixtures/raw}" \
  --output-dir "${MOCK_OUTPUT_DIR:-${ODI_MOCK_IMPLEMENTATION_DIR}/../target/runtime-output}"
