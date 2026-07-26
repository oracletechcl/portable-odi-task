#!/usr/bin/env bash
set -euo pipefail

APP_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEPLOY_ENGINE="${APP_ROOT}/platforms/oci/scripts/deploy-internal.sh"

if [[ ! -x "${DEPLOY_ENGINE}" ]]; then
  echo "Missing executable OCI deployment engine: ${DEPLOY_ENGINE}" >&2
  echo "Complete this migration's --config and --app-name one-stop deployer." >&2
  exit 2
fi

exec "${DEPLOY_ENGINE}" "$@"
