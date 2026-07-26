#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_ROOT="$(cd "${SCRIPT_DIR}/../../.." && pwd)"
CONFIG_PATH=""
APP_NAME=""
DRY_RUN="no"

usage() {
  echo "usage: ./deploy.sh --config PATH --app-name NAME [--dry-run]"
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --config)
      CONFIG_PATH="${2:-}"
      shift 2
      ;;
    --app-name)
      APP_NAME="${2:-}"
      shift 2
      ;;
    --dry-run)
      DRY_RUN="yes"
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "unknown argument: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

[[ -n "${CONFIG_PATH}" ]] || { echo "--config is required" >&2; exit 2; }
[[ -n "${APP_NAME}" ]] || { echo "--app-name is required" >&2; exit 2; }
[[ -f "${CONFIG_PATH}" ]] || { echo "config not found: ${CONFIG_PATH}" >&2; exit 2; }

set -a
# shellcheck disable=SC1090
source "${CONFIG_PATH}"
set +a

required=(
  OCI_CLI_PROFILE OCI_REGION OCI_WORKSPACE_ID OCI_BUCKET_NAME OCI_OBJECT_NAME
  OCI_APPLICATION_IDENTIFIER MOCK_BASE_URL PROJECT_ZIP PROJECT_SHA256
  PIPELINE_TASK_IDENTIFIER RUN_DATE IMPORT_TIMEOUT_SECONDS PATCH_TIMEOUT_SECONDS
)
for name in "${required[@]}"; do
  [[ -n "${!name:-}" ]] || { echo "missing config value: ${name}" >&2; exit 2; }
  [[ "${!name}" != "REPLACE_ME" ]] || { echo "unresolved config value: ${name}" >&2; exit 2; }
done

resolve_app_path() {
  local value="$1"
  if [[ "${value}" = /* ]]; then
    printf '%s\n' "${value}"
  else
    printf '%s\n' "${APP_ROOT}/${value}"
  fi
}

PROJECT_ZIP_PATH="$(resolve_app_path "${PROJECT_ZIP}")"
PROJECT_SHA256_PATH="$(resolve_app_path "${PROJECT_SHA256}")"
[[ -f "${PROJECT_ZIP_PATH}" ]] || { echo "project ZIP not found" >&2; exit 2; }
[[ -f "${PROJECT_SHA256_PATH}" ]] || { echo "project checksum not found" >&2; exit 2; }
(cd "$(dirname "${PROJECT_ZIP_PATH}")" && shasum -a 256 -c "$(basename "${PROJECT_SHA256_PATH}")")

case "${MOCK_BASE_URL}" in
  http://*|https://*) ;;
  *) echo "MOCK_BASE_URL must be HTTP(S)" >&2; exit 2 ;;
esac
[[ "${RUN_DATE}" =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}$ ]] || {
  echo "RUN_DATE must use YYYY-MM-DD" >&2
  exit 2
}

echo "Application: ${APP_NAME}"
echo "Workspace: configured"
echo "Project: ${PROJECT_ZIP_PATH}"
echo "Mock: trusted external service supplied by operator"

if [[ "${DRY_RUN}" == "yes" ]]; then
  echo "DRY-RUN: checksum and configuration valid; no OCI mutation performed."
  exit 0
fi

command -v oci >/dev/null || { echo "oci CLI is required" >&2; exit 2; }

oci os object put \
  --profile "${OCI_CLI_PROFILE}" \
  --region "${OCI_REGION}" \
  --bucket-name "${OCI_BUCKET_NAME}" \
  --name "${OCI_OBJECT_NAME}" \
  --file "${PROJECT_ZIP_PATH}" \
  --force >/dev/null

IMPORT_JSON="$(oci data-integration import-request create \
  --profile "${OCI_CLI_PROFILE}" \
  --region "${OCI_REGION}" \
  --workspace-id "${OCI_WORKSPACE_ID}" \
  --bucket-name "${OCI_BUCKET_NAME}" \
  --file-name "${OCI_OBJECT_NAME}" \
  --object-storage-region "${OCI_REGION}" \
  --are-data-asset-references-included false \
  --import-conflict-resolution '{"importConflictResolutionType":"REPLACE"}' \
  --query 'data.key' \
  --raw-output)"
[[ -n "${IMPORT_JSON}" ]] || { echo "import request key missing" >&2; exit 1; }

deadline=$((SECONDS + IMPORT_TIMEOUT_SECONDS))
while (( SECONDS < deadline )); do
  status="$(oci data-integration import-request get \
    --profile "${OCI_CLI_PROFILE}" \
    --region "${OCI_REGION}" \
    --workspace-id "${OCI_WORKSPACE_ID}" \
    --import-request-key "${IMPORT_JSON}" \
    --query 'data.status' \
    --raw-output)"
  case "${status}" in
    SUCCESSFUL) break ;;
    FAILED)
      oci data-integration import-request get \
        --profile "${OCI_CLI_PROFILE}" \
        --region "${OCI_REGION}" \
        --workspace-id "${OCI_WORKSPACE_ID}" \
        --import-request-key "${IMPORT_JSON}"
      exit 1
      ;;
  esac
  sleep 5
done
[[ "${status:-}" == "SUCCESSFUL" ]] || { echo "import timed out" >&2; exit 1; }

rest_identifiers=(
  REST_CONFIGURACION_EQUIPO_MESA
  REST_CONFIGURACION_EQUIPO_USUARIO
  REST_OPC_OPCION
  REST_SEC_SECCION
  REST_SUB_SUBSECCION
  REST_TB_LOG_SISTEMA
  REST_TB_SUB_SISTEMA_SERVICIO
)

for rest_identifier in "${rest_identifiers[@]}"; do
  rest_key="$(oci data-integration task list \
    --profile "${OCI_CLI_PROFILE}" \
    --region "${OCI_REGION}" \
    --workspace-id "${OCI_WORKSPACE_ID}" \
    --identifier "${rest_identifier}" \
    --all \
    --query 'data.items[0].key' \
    --raw-output)"
  [[ -n "${rest_key}" && "${rest_key}" != "null" ]] || {
    echo "imported REST task not found: ${rest_identifier}" >&2
    exit 1
  }
  rest_version="$(oci data-integration task get \
    --profile "${OCI_CLI_PROFILE}" \
    --region "${OCI_REGION}" \
    --workspace-id "${OCI_WORKSPACE_ID}" \
    --task-key "${rest_key}" \
    --query 'data."object-version"' \
    --raw-output)"
  template_url="$(oci data-integration task get \
    --profile "${OCI_CLI_PROFILE}" \
    --region "${OCI_REGION}" \
    --workspace-id "${OCI_WORKSPACE_ID}" \
    --task-key "${rest_key}" \
    --query 'data."execute-rest-call-config"."config-values"."config-param-values".requestURL."string-value"' \
    --raw-output)"
  execute_config="$(python3 - "${rest_key}" "${template_url}" "${MOCK_BASE_URL}" "${RUN_DATE}" <<'PY'
import json
import sys

task_key, template_url, base_url, run_date = sys.argv[1:]
prefix = "http://mock-backend.invalid"
if not template_url.startswith(prefix):
    raise SystemExit(f"unexpected REST URL template: {template_url}")
request_url = base_url.rstrip("/") + template_url[len(prefix):]
payload = json.dumps({"runDate": run_date}, separators=(",", ":"), sort_keys=True)
print(
    json.dumps(
        {
            "configValues": {
                "configParamValues": {
                    "requestPayload": {
                        "refValue": {
                            "configValues": {
                                "configParamValues": {
                                    "dataParam": {"stringValue": payload}
                                }
                            },
                            "modelType": "JSON_TEXT",
                        }
                    },
                    "requestURL": {"stringValue": request_url},
                },
                "parentRef": {"parent": task_key},
            },
            "methodType": "POST",
            "requestHeaders": {"Content-Type": "application/json"},
        },
        separators=(",", ":"),
        sort_keys=True,
    )
)
PY
)"
  oci data-integration task update-task-from-rest-task \
    --profile "${OCI_CLI_PROFILE}" \
    --region "${OCI_REGION}" \
    --workspace-id "${OCI_WORKSPACE_ID}" \
    --task-key "${rest_key}" \
    --key "${rest_key}" \
    --object-version "${rest_version}" \
    --parameters '[]' \
    --execute-rest-config "${execute_config}" \
    --force >/dev/null
done

application_key="$(oci data-integration application list \
  --profile "${OCI_CLI_PROFILE}" \
  --region "${OCI_REGION}" \
  --workspace-id "${OCI_WORKSPACE_ID}" \
  --identifier "${OCI_APPLICATION_IDENTIFIER}" \
  --all \
  --query 'data.items[0].key' \
  --raw-output)"
if [[ -z "${application_key}" || "${application_key}" == "null" ]]; then
  oci data-integration application create \
    --profile "${OCI_CLI_PROFILE}" \
    --region "${OCI_REGION}" \
    --workspace-id "${OCI_WORKSPACE_ID}" \
    --name "${APP_NAME}" \
    --identifier "${OCI_APPLICATION_IDENTIFIER}" \
    --model-type INTEGRATION_APPLICATION \
    --display-name "${APP_NAME}" \
    --description "Habitat Web migrated demo" >/dev/null
fi

application_state=""
deadline=$((SECONDS + PATCH_TIMEOUT_SECONDS))
while (( SECONDS < deadline )); do
  if [[ -z "${application_key}" || "${application_key}" == "null" ]]; then
    application_key="$(oci data-integration application list \
      --profile "${OCI_CLI_PROFILE}" \
      --region "${OCI_REGION}" \
      --workspace-id "${OCI_WORKSPACE_ID}" \
      --identifier "${OCI_APPLICATION_IDENTIFIER}" \
      --all \
      --query 'data.items[0].key' \
      --raw-output)"
  fi
  if [[ -n "${application_key}" && "${application_key}" != "null" ]]; then
    application_state="$(oci data-integration application get \
      --profile "${OCI_CLI_PROFILE}" \
      --region "${OCI_REGION}" \
      --workspace-id "${OCI_WORKSPACE_ID}" \
      --application-key "${application_key}" \
      --query 'data."lifecycle-state"' \
      --raw-output)"
    [[ "${application_state}" == "ACTIVE" ]] && break
    [[ "${application_state}" != "FAILED" ]] || {
      echo "application entered FAILED state" >&2
      exit 1
    }
  fi
  sleep 5
done
[[ "${application_state}" == "ACTIVE" ]] || {
  echo "application did not become ACTIVE" >&2
  exit 1
}

task_key="$(oci data-integration task list \
  --profile "${OCI_CLI_PROFILE}" \
  --region "${OCI_REGION}" \
  --workspace-id "${OCI_WORKSPACE_ID}" \
  --identifier "${PIPELINE_TASK_IDENTIFIER}" \
  --all \
  --query 'data.items[0].key' \
  --raw-output)"
[[ -n "${task_key}" && "${task_key}" != "null" ]] || {
  echo "imported pipeline task not found" >&2
  exit 1
}

patch_identifier="PUBLISH_$(date -u +%Y%m%d%H%M%S)"
patch_key="$(oci data-integration application create-patch \
  --profile "${OCI_CLI_PROFILE}" \
  --region "${OCI_REGION}" \
  --workspace-id "${OCI_WORKSPACE_ID}" \
  --application-key "${application_key}" \
  --name "${patch_identifier}" \
  --identifier "${patch_identifier}" \
  --patch-type PUBLISH \
  --object-keys "[\"${task_key}\"]" \
  --query 'data.key' \
  --raw-output)"

patch_status=""
deadline=$((SECONDS + PATCH_TIMEOUT_SECONDS))
while (( SECONDS < deadline )); do
  patch_status="$(oci data-integration application get-patch \
    --profile "${OCI_CLI_PROFILE}" \
    --region "${OCI_REGION}" \
    --workspace-id "${OCI_WORKSPACE_ID}" \
    --application-key "${application_key}" \
    --patch-key "${patch_key}" \
    --query 'data."patch-status"' \
    --raw-output)"
  [[ "${patch_status}" == "SUCCESSFUL" ]] && break
  if [[ "${patch_status}" == "FAILED" ]]; then
    oci data-integration application get-patch \
      --profile "${OCI_CLI_PROFILE}" \
      --region "${OCI_REGION}" \
      --workspace-id "${OCI_WORKSPACE_ID}" \
      --application-key "${application_key}" \
      --patch-key "${patch_key}" >&2
    exit 1
  fi
  sleep 5
done
[[ "${patch_status}" == "SUCCESSFUL" ]] || { echo "publish timed out" >&2; exit 1; }

published_key="$(oci data-integration application list-published-objects \
  --profile "${OCI_CLI_PROFILE}" \
  --region "${OCI_REGION}" \
  --workspace-id "${OCI_WORKSPACE_ID}" \
  --application-key "${application_key}" \
  --identifier "${PIPELINE_TASK_IDENTIFIER}" \
  --all \
  --query 'data.items[0].key' \
  --raw-output)"
[[ -n "${published_key}" && "${published_key}" != "null" ]] || {
  echo "publish succeeded but pipeline task is absent" >&2
  exit 1
}

echo "READY_WITH_TRUSTED_MOCK: import, materialization, application, and publication passed."
