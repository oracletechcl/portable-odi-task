#!/usr/bin/env bash
set -euo pipefail

OCI_DEPLOY_SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OCI_DEPLOY_REPO_ROOT="$(cd "${OCI_DEPLOY_SCRIPT_DIR}/../../.." && pwd)"
OCI_DEPLOY_DEMO_ROOT="${OCI_DEPLOY_REPO_ROOT}/habitat-e2e-demo/migrated-pipeline-demo"
OCI_DEPLOY_CONFIG_FILE="${DEMO_CONFIG_FILE:-${OCI_DEPLOY_DEMO_ROOT}/.demo-deploy.env}"
OCI_DEPLOY_ARCHIVE="${OCI_DEPLOY_DEMO_ROOT}/target/habitat-sucursales-mock-backend-1.0.0.tar.gz"
OCI_DEPLOY_CHECKSUM="${OCI_DEPLOY_ARCHIVE}.sha256"
OCI_DEPLOY_PROJECT_ARCHIVE="${OCI_DEPLOY_DEMO_ROOT}/target/HABITAT_SUCURSALES.project.zip"
OCI_DEPLOY_PROJECT_CHECKSUM="${OCI_DEPLOY_PROJECT_ARCHIVE}.sha256"
OCI_DEPLOY_UNIT="${OCI_DEPLOY_REPO_ROOT}/platforms/oci/systemd/habitat-sucursales-mock.service"

usage() {
  cat <<'EOF'
Usage:
  platforms/oci/scripts/deploy-habitat-sucursales-demo.sh \
    --app-name NAME \
    --as-of-date YYYY-MM-DD

The script loads:
  habitat-e2e-demo/migrated-pipeline-demo/.demo-deploy.env

Required argument:
  --app-name NAME
  --as-of-date YYYY-MM-DD

Required values:
  VM_PUBLIC_IP
  VM_PRIVATE_IP
  VM_SSH_USER
  VM_SSH_KEY
  OCI_WORKSPACE_ID
  OCI_REGION
  OCI_BUCKET_NAME
EOF
}

OCI_DEPLOY_APPLICATION_NAME=""
OCI_DEPLOY_AS_OF_DATE=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --app-name)
      if [[ $# -lt 2 || -z "$2" ]]; then
        echo "--app-name requires a value" >&2
        exit 2
      fi
      OCI_DEPLOY_APPLICATION_NAME="$2"
      shift 2
      ;;
    --as-of-date)
      if [[ $# -lt 2 || -z "$2" ]]; then
        echo "--as-of-date requires a value" >&2
        exit 2
      fi
      OCI_DEPLOY_AS_OF_DATE="$2"
      shift 2
      ;;
    --help|-h)
      usage
      exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

if [[ -z "${OCI_DEPLOY_APPLICATION_NAME}" ]]; then
  echo "--app-name is required" >&2
  usage >&2
  exit 2
fi
if [[ -z "${OCI_DEPLOY_AS_OF_DATE}" ]]; then
  echo "--as-of-date is required" >&2
  usage >&2
  exit 2
fi

OCI_APPLICATION_IDENTIFIER="$(
  printf '%s' "${OCI_DEPLOY_APPLICATION_NAME}" \
    | tr '[:lower:]' '[:upper:]' \
    | tr -cs 'A-Z0-9_' '_'
)"
if [[ ! "${OCI_APPLICATION_IDENTIFIER}" =~ ^[A-Z_] ]]; then
  OCI_APPLICATION_IDENTIFIER="_${OCI_APPLICATION_IDENTIFIER}"
fi

if [[ -f "${OCI_DEPLOY_CONFIG_FILE}" ]]; then
  # shellcheck disable=SC1090
  source "${OCI_DEPLOY_CONFIG_FILE}"
fi

: "${VM_PUBLIC_IP:?Set VM_PUBLIC_IP in ${OCI_DEPLOY_CONFIG_FILE}}"
: "${VM_PRIVATE_IP:?Set VM_PRIVATE_IP in ${OCI_DEPLOY_CONFIG_FILE}}"
: "${VM_SSH_USER:?Set VM_SSH_USER in ${OCI_DEPLOY_CONFIG_FILE}}"
: "${VM_SSH_KEY:?Set VM_SSH_KEY in ${OCI_DEPLOY_CONFIG_FILE}}"
: "${OCI_WORKSPACE_ID:?Set OCI_WORKSPACE_ID in ${OCI_DEPLOY_CONFIG_FILE}}"
: "${OCI_REGION:?Set OCI_REGION in ${OCI_DEPLOY_CONFIG_FILE}}"
: "${OCI_BUCKET_NAME:?Set OCI_BUCKET_NAME in ${OCI_DEPLOY_CONFIG_FILE}}"

OCI_TASK_IDENTIFIER="TASK_RUN_HABITAT_SUCURSALES"

if [[ "${VM_SSH_KEY}" != /* ]]; then
  VM_SSH_KEY="${OCI_DEPLOY_REPO_ROOT}/${VM_SSH_KEY}"
fi

for command_name in oci ssh scp curl python3; do
  if ! command -v "${command_name}" >/dev/null 2>&1; then
    echo "Missing required command: ${command_name}" >&2
    exit 1
  fi
done

if ! python3 - "${OCI_DEPLOY_AS_OF_DATE}" <<'PY'
from datetime import date
import sys

date.fromisoformat(sys.argv[1])
PY
then
  echo "--as-of-date must be a valid ISO date (YYYY-MM-DD)" >&2
  exit 2
fi

for required_file in \
  "${VM_SSH_KEY}" \
  "${OCI_DEPLOY_ARCHIVE}" \
  "${OCI_DEPLOY_CHECKSUM}" \
  "${OCI_DEPLOY_PROJECT_ARCHIVE}" \
  "${OCI_DEPLOY_PROJECT_CHECKSUM}" \
  "${OCI_DEPLOY_UNIT}"; do
  if [[ ! -f "${required_file}" ]]; then
    echo "Required file not found: ${required_file}" >&2
    exit 1
  fi
done

echo "[1/7] Verifying the immutable release assets"
if command -v sha256sum >/dev/null 2>&1; then
  (
    cd "$(dirname "${OCI_DEPLOY_ARCHIVE}")"
    sha256sum -c "$(basename "${OCI_DEPLOY_CHECKSUM}")"
    sha256sum -c "$(basename "${OCI_DEPLOY_PROJECT_CHECKSUM}")"
  )
else
  (
    cd "$(dirname "${OCI_DEPLOY_ARCHIVE}")"
    shasum -a 256 -c "$(basename "${OCI_DEPLOY_CHECKSUM}")"
    shasum -a 256 -c "$(basename "${OCI_DEPLOY_PROJECT_CHECKSUM}")"
  )
fi

chmod 600 "${VM_SSH_KEY}"
OCI_DEPLOY_SSH_OPTIONS=(
  -i "${VM_SSH_KEY}"
  -o BatchMode=yes
  -o ConnectTimeout=15
  -o StrictHostKeyChecking=accept-new
)

echo "[2/7] Resolving the workspace subnet"
OCI_DEPLOY_WORKSPACE_SUBNET_ID="$(
  oci data-integration workspace get \
    --region "${OCI_REGION}" \
    --workspace-id "${OCI_WORKSPACE_ID}" \
    --query 'data."subnet-id"' \
    --raw-output
)"
if [[ -z "${OCI_DEPLOY_WORKSPACE_SUBNET_ID}" || "${OCI_DEPLOY_WORKSPACE_SUBNET_ID}" == "null" ]]; then
  echo "The OCI Data Integration workspace has no subnet attachment." >&2
  exit 1
fi

OCI_DEPLOY_WORKSPACE_CIDR="$(
  oci network subnet get \
    --region "${OCI_REGION}" \
    --subnet-id "${OCI_DEPLOY_WORKSPACE_SUBNET_ID}" \
    --query 'data."cidr-block"' \
    --raw-output
)"

echo "[3/7] Installing and starting the VM mock"
scp "${OCI_DEPLOY_SSH_OPTIONS[@]}" \
  "${OCI_DEPLOY_ARCHIVE}" \
  "${OCI_DEPLOY_CHECKSUM}" \
  "${OCI_DEPLOY_UNIT}" \
  "${VM_SSH_USER}@${VM_PUBLIC_IP}:/tmp/"

OCI_DEPLOY_RELEASE_SHA="$(
  awk 'NR == 1 {print $1}' "${OCI_DEPLOY_CHECKSUM}"
)"
OCI_DEPLOY_RELEASE_ID="1.0.0-${OCI_DEPLOY_RELEASE_SHA:0:8}"

ssh "${OCI_DEPLOY_SSH_OPTIONS[@]}" \
  "${VM_SSH_USER}@${VM_PUBLIC_IP}" \
  bash -s -- "${OCI_DEPLOY_WORKSPACE_CIDR}" "${OCI_DEPLOY_RELEASE_ID}" <<'REMOTE'
set -euo pipefail

workspace_cidr="$1"
release_id="$2"
archive="/tmp/habitat-sucursales-mock-backend-1.0.0.tar.gz"
checksum="${archive}.sha256"
unit="/tmp/habitat-sucursales-mock.service"
release_dir="/opt/habitat-sucursales/releases/${release_id}"

cd /tmp
sha256sum -c "$(basename "${checksum}")"

if ! command -v python3.11 >/dev/null 2>&1; then
  sudo dnf -y -q install python3.11
fi

sudo install -d -o root -g root -m 0755 "${release_dir}"
sudo tar -xzf "${archive}" -C "${release_dir}" --no-same-owner
sudo chown -R root:root "${release_dir}"
sudo chmod 0755 "${release_dir}/implementation/start-mock-backend.sh"
sudo ln -sfn "releases/${release_id}" /opt/habitat-sucursales/current
sudo install -d -o opc -g opc -m 0750 /var/lib/habitat-sucursales/output
sudo install -o root -g root -m 0644 \
  "${unit}" \
  /etc/systemd/system/habitat-sucursales-mock.service

if sudo firewall-cmd --state >/dev/null 2>&1; then
  sudo firewall-cmd --permanent --zone=public \
    --add-rich-rule="rule family=ipv4 source address=${workspace_cidr} port port=8080 protocol=tcp accept"
  sudo firewall-cmd --reload
fi

sudo systemctl daemon-reload
sudo systemctl enable --now habitat-sucursales-mock.service

mock_ready=false
for _attempt in $(seq 1 30); do
  if curl --fail --silent --show-error http://127.0.0.1:8080/health; then
    mock_ready=true
    printf '\n'
    break
  fi
  sleep 1
done

if [[ "${mock_ready}" != "true" ]]; then
  sudo journalctl -u habitat-sucursales-mock.service -n 100 --no-pager
  exit 1
fi
REMOTE

echo "[4/7] Importing the OCI Data Integration project"
OCI_DEPLOY_PROJECT_DIGEST="$(awk '{print $1}' "${OCI_DEPLOY_PROJECT_CHECKSUM}")"
OCI_DEPLOY_OBJECT_NAME="$(
  printf 'releases/%s/%s' \
    "${OCI_DEPLOY_PROJECT_DIGEST}" \
    "$(basename "${OCI_DEPLOY_PROJECT_ARCHIVE}")"
)"
oci os object put \
  --region "${OCI_REGION}" \
  --bucket-name "${OCI_BUCKET_NAME}" \
  --name "${OCI_DEPLOY_OBJECT_NAME}" \
  --file "${OCI_DEPLOY_PROJECT_ARCHIVE}" \
  --force >/dev/null

OCI_DEPLOY_IMPORT_KEY="$(
  oci data-integration import-request create \
    --region "${OCI_REGION}" \
    --workspace-id "${OCI_WORKSPACE_ID}" \
    --bucket-name "${OCI_BUCKET_NAME}" \
    --file-name "${OCI_DEPLOY_OBJECT_NAME}" \
    --object-storage-region "${OCI_REGION}" \
    --are-data-asset-references-included false \
    --import-conflict-resolution \
      '{"importConflictResolutionType":"REPLACE"}' \
    --query 'data.key' \
    --raw-output
)"

OCI_DEPLOY_IMPORT_STATUS=""
for _attempt in $(seq 1 60); do
  OCI_DEPLOY_IMPORT_STATUS="$(
    oci data-integration import-request get \
      --region "${OCI_REGION}" \
      --workspace-id "${OCI_WORKSPACE_ID}" \
      --import-request-key "${OCI_DEPLOY_IMPORT_KEY}" \
      --query 'data.status' \
      --raw-output
  )"
  if [[ "${OCI_DEPLOY_IMPORT_STATUS}" == "SUCCESSFUL" ]]; then
    break
  fi
  if [[ "${OCI_DEPLOY_IMPORT_STATUS}" == "FAILED" ]]; then
    echo "Project import failed:" >&2
    oci data-integration import-request get \
      --region "${OCI_REGION}" \
      --workspace-id "${OCI_WORKSPACE_ID}" \
      --import-request-key "${OCI_DEPLOY_IMPORT_KEY}" >&2
    exit 1
  fi
  sleep 5
done
if [[ "${OCI_DEPLOY_IMPORT_STATUS}" != "SUCCESSFUL" ]]; then
  echo "Project import did not complete within five minutes." >&2
  exit 1
fi

echo "[5/7] Materializing the mock endpoint and run date"
OCI_DEPLOY_REST_TASK_IDENTIFIERS=(
  REST_PERIODS
  REST_ATENCIONES_PREVIOUS
  REST_ATENCIONES_CURRENT
  REST_AGENDAMIENTOS_PREVIOUS
  REST_AGENDAMIENTOS_CURRENT
  REST_VALIDATE
  REST_NOTIFY_ATENCIONES_PREVIOUS
  REST_NOTIFY_ATENCIONES_CURRENT
  REST_NOTIFY_AGENDAMIENTOS_PREVIOUS
  REST_NOTIFY_AGENDAMIENTOS_CURRENT
)

for OCI_DEPLOY_REST_IDENTIFIER in "${OCI_DEPLOY_REST_TASK_IDENTIFIERS[@]}"; do
  OCI_DEPLOY_REST_KEY="$(
    oci data-integration task list \
      --region "${OCI_REGION}" \
      --workspace-id "${OCI_WORKSPACE_ID}" \
      --identifier "${OCI_DEPLOY_REST_IDENTIFIER}" \
      --all \
      --query 'data.items[0].key' \
      --raw-output
  )"
  if [[ -z "${OCI_DEPLOY_REST_KEY}" || "${OCI_DEPLOY_REST_KEY}" == "null" ]]; then
    echo "Imported REST task not found: ${OCI_DEPLOY_REST_IDENTIFIER}" >&2
    exit 1
  fi

  OCI_DEPLOY_REST_VERSION="$(
    oci data-integration task get \
      --region "${OCI_REGION}" \
      --workspace-id "${OCI_WORKSPACE_ID}" \
      --task-key "${OCI_DEPLOY_REST_KEY}" \
      --query 'data."object-version"' \
      --raw-output
  )"
  OCI_DEPLOY_TEMPLATE_URL="$(
    oci data-integration task get \
      --region "${OCI_REGION}" \
      --workspace-id "${OCI_WORKSPACE_ID}" \
      --task-key "${OCI_DEPLOY_REST_KEY}" \
      --query \
        'data."execute-rest-call-config"."config-values"."config-param-values".requestURL."string-value"' \
      --raw-output
  )"
  OCI_DEPLOY_TEMPLATE_PAYLOAD="$(
    oci data-integration task get \
      --region "${OCI_REGION}" \
      --workspace-id "${OCI_WORKSPACE_ID}" \
      --task-key "${OCI_DEPLOY_REST_KEY}" \
      --query \
        'data."execute-rest-call-config"."config-values"."config-param-values".requestPayload."ref-value".configValues.configParamValues.dataParam.stringValue' \
      --raw-output
  )"

  OCI_DEPLOY_EXECUTE_CONFIG="$(
    python3 - \
      "${OCI_DEPLOY_REST_KEY}" \
      "${OCI_DEPLOY_TEMPLATE_URL}" \
      "${OCI_DEPLOY_TEMPLATE_PAYLOAD}" \
      "${VM_PRIVATE_IP}" \
      "${OCI_DEPLOY_AS_OF_DATE}" <<'PY'
import json
import sys

task_key, template_url, template_payload, private_ip, as_of_date = sys.argv[1:]
expected_prefix = "http://mock-backend.invalid"
if not template_url.startswith(expected_prefix):
    raise SystemExit(f"Unexpected REST URL template: {template_url}")
request_url = template_url.replace(
    expected_prefix, f"http://{private_ip}:8080", 1
)
placeholder_prefix = "$" + "{"
request_payload = template_payload.replace(
    placeholder_prefix + "AS_OF_DATE}", as_of_date
)
if placeholder_prefix in request_url or placeholder_prefix in request_payload:
    raise SystemExit("Unresolved placeholder in materialized REST task")
print(
    json.dumps(
        {
            "configValues": {
                "configParamValues": {
                    "requestPayload": {
                        "refValue": {
                            "configValues": {
                                "configParamValues": {
                                    "dataParam": {
                                        "stringValue": request_payload
                                    }
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
    --region "${OCI_REGION}" \
    --workspace-id "${OCI_WORKSPACE_ID}" \
    --task-key "${OCI_DEPLOY_REST_KEY}" \
    --key "${OCI_DEPLOY_REST_KEY}" \
    --object-version "${OCI_DEPLOY_REST_VERSION}" \
    --parameters '[]' \
    --execute-rest-config "${OCI_DEPLOY_EXECUTE_CONFIG}" \
    --force >/dev/null
done

echo "[6/7] Creating or finding the OCI application"
OCI_DEPLOY_APPLICATION_KEY="$(
  oci data-integration application list \
    --region "${OCI_REGION}" \
    --workspace-id "${OCI_WORKSPACE_ID}" \
    --identifier "${OCI_APPLICATION_IDENTIFIER}" \
    --all \
    --query 'data.items[0].key' \
    --raw-output
)"

if [[ -z "${OCI_DEPLOY_APPLICATION_KEY}" || "${OCI_DEPLOY_APPLICATION_KEY}" == "null" ]]; then
  oci data-integration application create \
    --region "${OCI_REGION}" \
    --workspace-id "${OCI_WORKSPACE_ID}" \
    --name "${OCI_DEPLOY_APPLICATION_NAME}" \
    --identifier "${OCI_APPLICATION_IDENTIFIER}" \
    --model-type INTEGRATION_APPLICATION \
    --display-name "${OCI_DEPLOY_APPLICATION_NAME}" \
    --description "Habitat Sucursales migrated demo" >/dev/null
fi

OCI_DEPLOY_APPLICATION_STATE=""
for _attempt in $(seq 1 60); do
  if [[ -z "${OCI_DEPLOY_APPLICATION_KEY}" || "${OCI_DEPLOY_APPLICATION_KEY}" == "null" ]]; then
    OCI_DEPLOY_APPLICATION_KEY="$(
      oci data-integration application list \
        --region "${OCI_REGION}" \
        --workspace-id "${OCI_WORKSPACE_ID}" \
        --identifier "${OCI_APPLICATION_IDENTIFIER}" \
        --all \
        --query 'data.items[0].key' \
        --raw-output
    )"
  fi

  if [[ -n "${OCI_DEPLOY_APPLICATION_KEY}" && "${OCI_DEPLOY_APPLICATION_KEY}" != "null" ]]; then
    OCI_DEPLOY_APPLICATION_STATE="$(
      oci data-integration application get \
        --region "${OCI_REGION}" \
        --workspace-id "${OCI_WORKSPACE_ID}" \
        --application-key "${OCI_DEPLOY_APPLICATION_KEY}" \
        --query 'data."lifecycle-state"' \
        --raw-output
    )"
    if [[ "${OCI_DEPLOY_APPLICATION_STATE}" == "ACTIVE" ]]; then
      break
    fi
    if [[ "${OCI_DEPLOY_APPLICATION_STATE}" == "FAILED" ]]; then
      echo "Application ${OCI_APPLICATION_IDENTIFIER} entered FAILED state." >&2
      exit 1
    fi
  fi
  sleep 5
done

if [[ -z "${OCI_DEPLOY_APPLICATION_KEY}" \
  || "${OCI_DEPLOY_APPLICATION_KEY}" == "null" \
  || "${OCI_DEPLOY_APPLICATION_STATE}" != "ACTIVE" ]]; then
  echo "Application ${OCI_APPLICATION_IDENTIFIER} did not become ACTIVE." >&2
  exit 1
fi

OCI_DEPLOY_TASK_KEY="$(
  oci data-integration task list \
    --region "${OCI_REGION}" \
    --workspace-id "${OCI_WORKSPACE_ID}" \
    --identifier "${OCI_TASK_IDENTIFIER}" \
    --all \
    --query 'data.items[0].key' \
    --raw-output
)"
if [[ -z "${OCI_DEPLOY_TASK_KEY}" || "${OCI_DEPLOY_TASK_KEY}" == "null" ]]; then
  echo "Imported task not found: ${OCI_TASK_IDENTIFIER}" >&2
  exit 1
fi

echo "[7/7] Publishing the pipeline task"
OCI_DEPLOY_PATCH_IDENTIFIER="PUBLISH_$(date -u +%Y%m%d%H%M%S)"
OCI_DEPLOY_PATCH_KEY="$(
  oci data-integration application create-patch \
    --region "${OCI_REGION}" \
    --workspace-id "${OCI_WORKSPACE_ID}" \
    --application-key "${OCI_DEPLOY_APPLICATION_KEY}" \
    --name "${OCI_DEPLOY_PATCH_IDENTIFIER}" \
    --identifier "${OCI_DEPLOY_PATCH_IDENTIFIER}" \
    --patch-type PUBLISH \
    --object-keys "[\"${OCI_DEPLOY_TASK_KEY}\"]" \
    --query 'data.key' \
    --raw-output
)"

OCI_DEPLOY_PATCH_STATUS=""
for _attempt in $(seq 1 60); do
  OCI_DEPLOY_PATCH_STATUS="$(
    oci data-integration application get-patch \
      --region "${OCI_REGION}" \
      --workspace-id "${OCI_WORKSPACE_ID}" \
      --application-key "${OCI_DEPLOY_APPLICATION_KEY}" \
      --patch-key "${OCI_DEPLOY_PATCH_KEY}" \
      --query 'data."patch-status"' \
      --raw-output
  )"
  if [[ "${OCI_DEPLOY_PATCH_STATUS}" == "SUCCESSFUL" ]]; then
    break
  fi
  if [[ "${OCI_DEPLOY_PATCH_STATUS}" == "FAILED" ]]; then
    echo "Publish failed:" >&2
    oci data-integration application get-patch \
      --region "${OCI_REGION}" \
      --workspace-id "${OCI_WORKSPACE_ID}" \
      --application-key "${OCI_DEPLOY_APPLICATION_KEY}" \
      --patch-key "${OCI_DEPLOY_PATCH_KEY}" >&2
    exit 1
  fi
  sleep 5
done
if [[ "${OCI_DEPLOY_PATCH_STATUS}" != "SUCCESSFUL" ]]; then
  echo "Publish did not complete within five minutes." >&2
  exit 1
fi

OCI_DEPLOY_PUBLISHED_TASK_KEY="$(
  oci data-integration application list-published-objects \
    --region "${OCI_REGION}" \
    --workspace-id "${OCI_WORKSPACE_ID}" \
    --application-key "${OCI_DEPLOY_APPLICATION_KEY}" \
    --identifier "${OCI_TASK_IDENTIFIER}" \
    --all \
    --query 'data.items[0].key' \
    --raw-output
)"
if [[ -z "${OCI_DEPLOY_PUBLISHED_TASK_KEY}" || "${OCI_DEPLOY_PUBLISHED_TASK_KEY}" == "null" ]]; then
  echo "Publish succeeded but the task is not present in the application." >&2
  exit 1
fi

cat <<EOF

READY
Application: ${OCI_DEPLOY_APPLICATION_NAME}
Identifier:  ${OCI_APPLICATION_IDENTIFIER}
Task:        ${OCI_TASK_IDENTIFIER}
Mock URL:    http://${VM_PRIVATE_IP}:8080
AS_OF_DATE:  ${OCI_DEPLOY_AS_OF_DATE}

Open the application in OCI Data Integration, select the task, and click Run.
EOF
