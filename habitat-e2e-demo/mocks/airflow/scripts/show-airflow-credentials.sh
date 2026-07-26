#!/usr/bin/env bash
set -euo pipefail

VM_PUBLIC_IP=""
SSH_USER=""
SSH_KEY=""
PASSWORD_FILE="/var/lib/airflow/simple_auth_manager_passwords.json.generated"

usage() {
  cat <<'EOF'
Usage:
  show-airflow-credentials.sh \
    --vm-public-ip ADDRESS \
    --ssh-user USER \
    --ssh-key PATH

Reads the runtime-only Airflow SimpleAuthManager credential JSON over SSH.
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
[[ -f "${SSH_KEY}" ]] || fail "SSH key does not exist: ${SSH_KEY}"

chmod 600 "${SSH_KEY}"
echo "Sensitive output follows; do not paste it into logs or version control." >&2
ssh \
  -i "${SSH_KEY}" \
  -o BatchMode=yes \
  -o ConnectTimeout=15 \
  -o StrictHostKeyChecking=accept-new \
  "${SSH_USER}@${VM_PUBLIC_IP}" \
  "test \"\$(sudo stat -c '%a' '${PASSWORD_FILE}')\" = 600 &&
   sudo cat '${PASSWORD_FILE}'"

