#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_ROOT="$(cd "${SCRIPT_DIR}/../../.." && pwd)"
CONFIG_PATH=""; APP_NAME=""; DRY_RUN=no
usage() { echo 'usage: ./deploy.sh --config PATH --app-name NAME [--dry-run]'; }
while [[ $# -gt 0 ]]; do case "$1" in
  --config) CONFIG_PATH="${2:-}"; shift 2;; --app-name) APP_NAME="${2:-}"; shift 2;;
  --dry-run) DRY_RUN=yes; shift;; -h|--help) usage; exit 0;; *) echo "unknown argument: $1" >&2; usage >&2; exit 2;; esac; done
[[ -n "$CONFIG_PATH" && -n "$APP_NAME" && -f "$CONFIG_PATH" ]] || { usage >&2; exit 2; }
set -a; source "$CONFIG_PATH"; set +a

required=(OCI_CLI_PROFILE OCI_REGION OCI_WORKSPACE_ID OCI_BUCKET_NAME OCI_PROJECT_OBJECT_NAME OCI_APPLICATION_NAME OCI_TASK_IDENTIFIER RUN_AS_OF_DATE VM_PRIVATE_IP MOCK_PORT PROJECT_ARCHIVE PROJECT_CHECKSUM IMPORT_TIMEOUT_SECONDS PUBLISH_TIMEOUT_SECONDS)
for name in "${required[@]}"; do [[ -n "${!name:-}" && "${!name}" != "REPLACE_ME" ]] || { echo "missing config value: $name" >&2; exit 2; }; done
[[ "$MOCK_PORT" =~ ^[1-9][0-9]{0,4}$ ]] || { echo 'MOCK_PORT must be a valid TCP port' >&2; exit 2; }
python3 - "$RUN_AS_OF_DATE" <<'PY'
from datetime import date
import sys
date.fromisoformat(sys.argv[1])
PY
project_archive="$PROJECT_ARCHIVE"; [[ "$project_archive" = /* ]] || project_archive="$APP_ROOT/$project_archive"
project_checksum="$PROJECT_CHECKSUM"; [[ "$project_checksum" = /* ]] || project_checksum="$APP_ROOT/$project_checksum"
[[ -f "$project_archive" && -f "$project_checksum" ]] || { echo 'missing OCI project archive or checksum' >&2; exit 2; }
(cd "$(dirname "$project_archive")" && shasum -a 256 -c "$(basename "$project_checksum")")
mock_base_url="http://${VM_PRIVATE_IP}:${MOCK_PORT}"
echo "Dependency gates: project checksum valid; external mock=${mock_base_url}; application=${APP_NAME}"
if [[ "$DRY_RUN" == yes ]]; then echo 'DRY-RUN: no OCI or external mock mutation performed.'; exit 0; fi
command -v oci >/dev/null || { echo 'oci CLI is required' >&2; exit 2; }

# The mock is user-managed. Materialize its URL only; never probe, install,
# start, stop, replace, or otherwise mutate it from this deployment engine.
oci os object put --profile "$OCI_CLI_PROFILE" --region "$OCI_REGION" --bucket-name "$OCI_BUCKET_NAME" --name "$OCI_PROJECT_OBJECT_NAME" --file "$project_archive" --force >/dev/null
import_key="$(oci data-integration import-request create --profile "$OCI_CLI_PROFILE" --region "$OCI_REGION" --workspace-id "$OCI_WORKSPACE_ID" --bucket-name "$OCI_BUCKET_NAME" --file-name "$OCI_PROJECT_OBJECT_NAME" --object-storage-region "$OCI_REGION" --are-data-asset-references-included false --import-conflict-resolution '{"importConflictResolutionType":"REPLACE"}' --query 'data.key' --raw-output)"
[[ -n "$import_key" && "$import_key" != null ]] || { echo 'import request key missing' >&2; exit 1; }
deadline=$((SECONDS + IMPORT_TIMEOUT_SECONDS)); import_status=""
while (( SECONDS < deadline )); do
  import_status="$(oci data-integration import-request get --profile "$OCI_CLI_PROFILE" --region "$OCI_REGION" --workspace-id "$OCI_WORKSPACE_ID" --import-request-key "$import_key" --query 'data.status' --raw-output)"
  [[ "$import_status" == SUCCESSFUL ]] && break
  if [[ "$import_status" == FAILED ]]; then oci data-integration import-request get --profile "$OCI_CLI_PROFILE" --region "$OCI_REGION" --workspace-id "$OCI_WORKSPACE_ID" --import-request-key "$import_key" >&2; exit 1; fi
  sleep 5
done
[[ "$import_status" == SUCCESSFUL ]] || { echo 'import timed out' >&2; exit 1; }

rest_key="$(oci data-integration task list --profile "$OCI_CLI_PROFILE" --region "$OCI_REGION" --workspace-id "$OCI_WORKSPACE_ID" --identifier RUN_SUCURSALES --all --query 'data.items[0].key' --raw-output)"
[[ -n "$rest_key" && "$rest_key" != null ]] || { echo 'imported REST task RUN_SUCURSALES not found' >&2; exit 1; }
rest_version="$(oci data-integration task get --profile "$OCI_CLI_PROFILE" --region "$OCI_REGION" --workspace-id "$OCI_WORKSPACE_ID" --task-key "$rest_key" --query 'data."object-version"' --raw-output)"
rest_config="$(python3 "$APP_ROOT/implementation/oci_rest_config.py" "$rest_key" "$mock_base_url" "$RUN_AS_OF_DATE")"
oci data-integration task update-task-from-rest-task --profile "$OCI_CLI_PROFILE" --region "$OCI_REGION" --workspace-id "$OCI_WORKSPACE_ID" --task-key "$rest_key" --key "$rest_key" --object-version "$rest_version" --parameters '[]' --execute-rest-config "$rest_config" --force >/dev/null

app_identifier="$(printf '%s' "$APP_NAME" | tr '[:lower:]' '[:upper:]' | tr -cs 'A-Z0-9_' '_')"
app_key="$(oci data-integration application list --profile "$OCI_CLI_PROFILE" --region "$OCI_REGION" --workspace-id "$OCI_WORKSPACE_ID" --identifier "$app_identifier" --all --query 'data.items[0].key' --raw-output)"
if [[ -z "$app_key" || "$app_key" == null ]]; then
  oci data-integration application create --profile "$OCI_CLI_PROFILE" --region "$OCI_REGION" --workspace-id "$OCI_WORKSPACE_ID" --name "$APP_NAME" --identifier "$app_identifier" --model-type INTEGRATION_APPLICATION --display-name "$APP_NAME" --description 'Sucursales via skill migration' >/dev/null
  deadline=$((SECONDS + PUBLISH_TIMEOUT_SECONDS)); app_key=""
  while (( SECONDS < deadline )); do app_key="$(oci data-integration application list --profile "$OCI_CLI_PROFILE" --region "$OCI_REGION" --workspace-id "$OCI_WORKSPACE_ID" --identifier "$app_identifier" --all --query 'data.items[0].key' --raw-output)"; [[ -n "$app_key" && "$app_key" != null ]] && break; sleep 5; done
fi
[[ -n "$app_key" && "$app_key" != null ]] || { echo 'application was not created' >&2; exit 1; }
task_key="$(oci data-integration task list --profile "$OCI_CLI_PROFILE" --region "$OCI_REGION" --workspace-id "$OCI_WORKSPACE_ID" --identifier "$OCI_TASK_IDENTIFIER" --all --query 'data.items[0].key' --raw-output)"
[[ -n "$task_key" && "$task_key" != null ]] || { echo 'imported pipeline task not found' >&2; exit 1; }
patch_id="PUBLISH_$(date -u +%Y%m%d%H%M%S)"
patch_key="$(oci data-integration application create-patch --profile "$OCI_CLI_PROFILE" --region "$OCI_REGION" --workspace-id "$OCI_WORKSPACE_ID" --application-key "$app_key" --name "$patch_id" --identifier "$patch_id" --patch-type PUBLISH --object-keys "[\"$task_key\"]" --query 'data.key' --raw-output)"
deadline=$((SECONDS + PUBLISH_TIMEOUT_SECONDS)); patch_status=""
while (( SECONDS < deadline )); do
  patch_status="$(oci data-integration application get-patch --profile "$OCI_CLI_PROFILE" --region "$OCI_REGION" --workspace-id "$OCI_WORKSPACE_ID" --application-key "$app_key" --patch-key "$patch_key" --query 'data."patch-status"' --raw-output)"
  [[ "$patch_status" == SUCCESSFUL ]] && break
  if [[ "$patch_status" == FAILED ]]; then oci data-integration application get-patch --profile "$OCI_CLI_PROFILE" --region "$OCI_REGION" --workspace-id "$OCI_WORKSPACE_ID" --application-key "$app_key" --patch-key "$patch_key" >&2; exit 1; fi
  sleep 5
done
[[ "$patch_status" == SUCCESSFUL ]] || { echo 'publication timed out' >&2; exit 1; }
published="$(oci data-integration application list-published-objects --profile "$OCI_CLI_PROFILE" --region "$OCI_REGION" --workspace-id "$OCI_WORKSPACE_ID" --application-key "$app_key" --identifier "$OCI_TASK_IDENTIFIER" --all --query 'data.items[0].key' --raw-output)"
[[ -n "$published" && "$published" != null ]] || { echo 'published root task is absent' >&2; exit 1; }
echo 'READY: imported, materialized, published, external mock preserved.'
