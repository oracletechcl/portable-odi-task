#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVER_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
INSTALLER="${SCRIPT_DIR}/install-airflow-server.sh"
ENV_TEMPLATE="${SERVER_ROOT}/config/airflow.env.template"
SYSTEMD_UNIT="${SERVER_ROOT}/systemd/airflow-standalone.service"

VM_PUBLIC_IP=""
SSH_USER=""
SSH_KEY=""
AIRFLOW_PORT=""
ADMIN_USER=""
DRY_RUN="false"
REMOTE_DIR=""

usage() {
  cat <<'EOF'
Usage:
  deploy-airflow-server.sh \
    --vm-public-ip ADDRESS \
    --ssh-user USER \
    --ssh-key PATH \
    --airflow-port PORT \
    --admin-user USERNAME \
    [--dry-run]

Uploads and installs a vanilla Airflow 3.3.0 standalone TEST server. Every
environment value is required; no VM, credential, user, or port default is used.
EOF
}

fail() {
  echo "ERROR: $*" >&2
  exit 1
}

require_value() {
  local option="$1"
  local value="${2:-}"
  [[ -n "${value}" ]] || fail "${option} requires a value"
}

while (($#)); do
  case "$1" in
    --vm-public-ip)
      require_value "$1" "${2:-}"
      VM_PUBLIC_IP="$2"
      shift 2
      ;;
    --ssh-user)
      require_value "$1" "${2:-}"
      SSH_USER="$2"
      shift 2
      ;;
    --ssh-key)
      require_value "$1" "${2:-}"
      SSH_KEY="$2"
      shift 2
      ;;
    --airflow-port)
      require_value "$1" "${2:-}"
      AIRFLOW_PORT="$2"
      shift 2
      ;;
    --admin-user)
      require_value "$1" "${2:-}"
      ADMIN_USER="$2"
      shift 2
      ;;
    --dry-run)
      DRY_RUN="true"
      shift
      ;;
    --help|-h)
      usage
      exit 0
      ;;
    *)
      fail "unknown option: $1"
      ;;
  esac
done

[[ -n "${VM_PUBLIC_IP}" ]] || fail "--vm-public-ip is required"
[[ -n "${SSH_USER}" ]] || fail "--ssh-user is required"
[[ -n "${SSH_KEY}" ]] || fail "--ssh-key is required"
[[ -n "${AIRFLOW_PORT}" ]] || fail "--airflow-port is required"
[[ -n "${ADMIN_USER}" ]] || fail "--admin-user is required"
[[ -f "${SSH_KEY}" ]] || fail "SSH key does not exist: ${SSH_KEY}"
[[ "${VM_PUBLIC_IP}" =~ ^[A-Za-z0-9.:_-]+$ ]] ||
  fail "VM address contains unsafe characters"
[[ "${SSH_USER}" =~ ^[A-Za-z_][A-Za-z0-9_.-]{0,31}$ ]] ||
  fail "SSH user contains unsafe characters"
[[ "${ADMIN_USER}" =~ ^[A-Za-z][A-Za-z0-9_.-]{2,63}$ ]] ||
  fail "admin username must be 3-64 safe characters"
[[ "${AIRFLOW_PORT}" =~ ^[0-9]+$ ]] || fail "airflow port must be numeric"
((AIRFLOW_PORT >= 1024 && AIRFLOW_PORT <= 65535)) ||
  fail "airflow port must be between 1024 and 65535"
[[ "${AIRFLOW_PORT}" != "8080" ]] ||
  fail "port 8080 is reserved for the existing mock backend"

for asset in "${INSTALLER}" "${ENV_TEMPLATE}" "${SYSTEMD_UNIT}"; do
  [[ -r "${asset}" ]] || fail "required asset is unreadable: ${asset}"
done

echo "Airflow deployment plan"
echo "  target: ${SSH_USER}@${VM_PUBLIC_IP}"
echo "  airflow: 3.3.0 on loopback port ${AIRFLOW_PORT}"
echo "  admin user: ${ADMIN_USER}"
echo "  existing mock port: 8080 (unchanged)"

if [[ "${DRY_RUN}" == "true" ]]; then
  echo "DRY RUN: no SSH, SCP, remote, or local mutations performed"
  exit 0
fi

chmod 600 "${SSH_KEY}"
SSH_OPTIONS=(
  -i "${SSH_KEY}"
  -o BatchMode=yes
  -o ConnectTimeout=15
  -o StrictHostKeyChecking=accept-new
)
TARGET="${SSH_USER}@${VM_PUBLIC_IP}"

cleanup() {
  if [[ -n "${REMOTE_DIR}" ]]; then
    ssh "${SSH_OPTIONS[@]}" "${TARGET}" \
      "rm -f -- \
         '${REMOTE_DIR}/install-airflow-server.sh' \
         '${REMOTE_DIR}/airflow.env.template' \
         '${REMOTE_DIR}/airflow-standalone.service';
       rmdir -- '${REMOTE_DIR}'" >/dev/null 2>&1 || true
  fi
}
trap cleanup EXIT

REMOTE_DIR="$(
  ssh "${SSH_OPTIONS[@]}" "${TARGET}" \
    "mktemp -d /tmp/airflow-server.XXXXXX"
)"
[[ "${REMOTE_DIR}" == /tmp/airflow-server.* ]] ||
  fail "remote temporary directory was not created safely"

scp "${SSH_OPTIONS[@]}" \
  "${INSTALLER}" \
  "${ENV_TEMPLATE}" \
  "${SYSTEMD_UNIT}" \
  "${TARGET}:${REMOTE_DIR}/"

installer_sha="$(shasum -a 256 "${INSTALLER}" | awk '{print $1}')"
template_sha="$(shasum -a 256 "${ENV_TEMPLATE}" | awk '{print $1}')"
unit_sha="$(shasum -a 256 "${SYSTEMD_UNIT}" | awk '{print $1}')"

ssh "${SSH_OPTIONS[@]}" "${TARGET}" \
  "cd '${REMOTE_DIR}' &&
   printf '%s  %s\n%s  %s\n%s  %s\n' \
     '${installer_sha}' 'install-airflow-server.sh' \
     '${template_sha}' 'airflow.env.template' \
     '${unit_sha}' 'airflow-standalone.service' |
   sha256sum -c - &&
   sudo bash '${REMOTE_DIR}/install-airflow-server.sh' \
     --airflow-port '${AIRFLOW_PORT}' \
     --admin-user '${ADMIN_USER}' \
     --env-template '${REMOTE_DIR}/airflow.env.template' \
     --systemd-unit '${REMOTE_DIR}/airflow-standalone.service'"

ssh "${SSH_OPTIONS[@]}" "${TARGET}" \
  "sudo systemctl is-active --quiet airflow-standalone.service &&
   sudo systemctl is-active --quiet habitat-sucursales-mock.service &&
   test \"\$(sudo stat -c '%a' \
     /var/lib/airflow/simple_auth_manager_passwords.json.generated)\" = 600"

echo "READY"
echo "Retrieve credentials with scripts/show-airflow-credentials.sh."
echo "Open an SSH tunnel to 127.0.0.1:${AIRFLOW_PORT}."
