#!/usr/bin/env bash
set -euo pipefail

VM_PUBLIC_IP=""
SSH_USER=""
SSH_KEY=""
DAG_FILE=""
REMOTE_TMP=""
DAGS_FOLDER="/var/lib/airflow/dags"

usage() {
  cat <<'EOF'
Usage:
  deploy-dag.sh \
    --vm-public-ip ADDRESS \
    --ssh-user USER \
    --ssh-key PATH \
    --dag-file PATH

Syntax-checks and atomically installs one Python DAG into the test server's
local DAG bundle. Airflow UI/API credentials are not used to upload DAG source.
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
    --dag-file)
      require_value "$1" "${2:-}"
      DAG_FILE="$2"
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
[[ -n "${DAG_FILE}" ]] || fail "--dag-file is required"
[[ -f "${SSH_KEY}" ]] || fail "SSH key does not exist: ${SSH_KEY}"
[[ -f "${DAG_FILE}" ]] || fail "DAG file does not exist: ${DAG_FILE}"
[[ "${DAG_FILE}" == *.py ]] || fail "DAG file must end with .py"

dag_name="$(basename "${DAG_FILE}")"
[[ "${dag_name}" =~ ^[A-Za-z0-9_.-]+\.py$ ]] ||
  fail "DAG filename contains unsafe characters"
python3 -c 'import pathlib,sys; p=pathlib.Path(sys.argv[1]); compile(p.read_text(encoding="utf-8"), str(p), "exec")' \
  "${DAG_FILE}"

chmod 600 "${SSH_KEY}"
SSH_OPTIONS=(
  -i "${SSH_KEY}"
  -o BatchMode=yes
  -o ConnectTimeout=15
  -o StrictHostKeyChecking=accept-new
)
TARGET="${SSH_USER}@${VM_PUBLIC_IP}"
REMOTE_TMP="$(
  ssh "${SSH_OPTIONS[@]}" "${TARGET}" "mktemp /tmp/airflow-dag.XXXXXX"
)"
[[ "${REMOTE_TMP}" == /tmp/airflow-dag.* ]] ||
  fail "remote temporary DAG path was not created safely"

cleanup() {
  ssh "${SSH_OPTIONS[@]}" "${TARGET}" \
    "rm -f -- '${REMOTE_TMP}'" >/dev/null 2>&1 || true
}
trap cleanup EXIT

scp "${SSH_OPTIONS[@]}" "${DAG_FILE}" "${TARGET}:${REMOTE_TMP}"
local_sha="$(shasum -a 256 "${DAG_FILE}" | awk '{print $1}')"

ssh "${SSH_OPTIONS[@]}" "${TARGET}" \
  "printf '%s  %s\n' '${local_sha}' '${REMOTE_TMP}' | sha256sum -c - &&
   sudo install -o airflow -g airflow -m 0644 \
     '${REMOTE_TMP}' '${DAGS_FOLDER}/.${dag_name}.new' &&
   sudo mv -f \
     '${DAGS_FOLDER}/.${dag_name}.new' '${DAGS_FOLDER}/${dag_name}' &&
   sudo -u airflow env \
     AIRFLOW_HOME=/var/lib/airflow \
     AIRFLOW__CORE__DAGS_FOLDER='${DAGS_FOLDER}' \
     /opt/airflow/venv/bin/airflow dags list-import-errors --output json"

echo "DEPLOYED ${dag_name} sha256=${local_sha}"
