#!/usr/bin/env bash
set -euo pipefail

AIRFLOW_VERSION="3.3.0"
PYTHON_BIN="/usr/bin/python3.11"
VENV_ROOT="/opt/airflow/venv"
AIRFLOW_HOME_DIR="/var/lib/airflow"
DAGS_FOLDER="${AIRFLOW_HOME_DIR}/dags"
PASSWORD_FILE="${AIRFLOW_HOME_DIR}/simple_auth_manager_passwords.json.generated"
ENV_FILE="/etc/airflow/airflow.env"
SERVICE_FILE="/etc/systemd/system/airflow-standalone.service"
CONSTRAINT_URL="https://raw.githubusercontent.com/apache/airflow/constraints-3.3.0/constraints-3.11.txt"

AIRFLOW_PORT=""
ADMIN_USER=""
ENV_TEMPLATE=""
SYSTEMD_UNIT=""

usage() {
  cat <<'EOF'
Usage:
  install-airflow-server.sh \
    --airflow-port PORT \
    --admin-user USERNAME \
    --env-template PATH \
    --systemd-unit PATH

Installs Apache Airflow 3.3.0 as a loopback-only standalone TEST service.
Run as root. A random SimpleAuthManager password is generated once and preserved.
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
    --env-template)
      require_value "$1" "${2:-}"
      ENV_TEMPLATE="$2"
      shift 2
      ;;
    --systemd-unit)
      require_value "$1" "${2:-}"
      SYSTEMD_UNIT="$2"
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

[[ -n "${AIRFLOW_PORT}" ]] || fail "--airflow-port is required"
[[ -n "${ADMIN_USER}" ]] || fail "--admin-user is required"
[[ -n "${ENV_TEMPLATE}" ]] || fail "--env-template is required"
[[ -n "${SYSTEMD_UNIT}" ]] || fail "--systemd-unit is required"
[[ "${EUID}" -eq 0 ]] || fail "run this installer as root"
[[ "${AIRFLOW_PORT}" =~ ^[0-9]+$ ]] || fail "airflow port must be numeric"
((AIRFLOW_PORT >= 1024 && AIRFLOW_PORT <= 65535)) ||
  fail "airflow port must be between 1024 and 65535"
[[ "${AIRFLOW_PORT}" != "8080" ]] ||
  fail "port 8080 is reserved for the existing mock backend"
[[ "${ADMIN_USER}" =~ ^[A-Za-z][A-Za-z0-9_.-]{2,63}$ ]] ||
  fail "admin username must be 3-64 safe characters"
[[ -r "${ENV_TEMPLATE}" ]] || fail "environment template is unreadable"
[[ -r "${SYSTEMD_UNIT}" ]] || fail "systemd unit is unreadable"
[[ -x "${PYTHON_BIN}" ]] || fail "Python 3.11 is required at ${PYTHON_BIN}"

memory_kib="$(awk '/MemTotal/{print $2}' /proc/meminfo)"
((memory_kib >= 4194304)) ||
  fail "Airflow test server requires at least 4 GiB RAM"
free_kib="$(df -Pk /opt | awk 'NR==2{print $4}')"
((free_kib >= 4194304)) ||
  fail "Airflow installation requires at least 4 GiB free under /opt"

MOCK_SERVICE="habitat-sucursales-mock.service"
MOCK_UNIT="/etc/systemd/system/habitat-sucursales-mock.service"
systemctl is-active --quiet "${MOCK_SERVICE}" ||
  fail "existing mock service must be active before Airflow deployment"
curl --fail --silent --show-error \
  http://127.0.0.1:8080/health >/dev/null ||
  fail "existing mock health check failed before Airflow deployment"
[[ -f "${MOCK_UNIT}" ]] || fail "existing mock systemd unit is missing"
MOCK_PID_BEFORE="$(systemctl show --property MainPID --value "${MOCK_SERVICE}")"
MOCK_UNIT_SHA_BEFORE="$(sha256sum "${MOCK_UNIT}" | awk '{print $1}')"
[[ "${MOCK_PID_BEFORE}" =~ ^[1-9][0-9]*$ ]] ||
  fail "existing mock has no running main process"

if ss -ltnH "sport = :${AIRFLOW_PORT}" | grep -q . &&
  ! systemctl is-active --quiet airflow-standalone.service; then
  fail "port ${AIRFLOW_PORT} is already owned by another process"
fi

if ! id airflow >/dev/null 2>&1; then
  useradd \
    --system \
    --home-dir "${AIRFLOW_HOME_DIR}" \
    --create-home \
    --shell /sbin/nologin \
    airflow
fi

install -d -o root -g root -m 0755 /opt/airflow
install -d -o airflow -g airflow -m 0750 "${AIRFLOW_HOME_DIR}"
install -d -o airflow -g airflow -m 02750 "${DAGS_FOLDER}"
install -d -o root -g airflow -m 0750 /etc/airflow

if [[ ! -x "${VENV_ROOT}/bin/python" ]]; then
  "${PYTHON_BIN}" -m venv "${VENV_ROOT}"
fi

"${VENV_ROOT}/bin/python" -m pip install --disable-pip-version-check --quiet \
  --upgrade pip
"${VENV_ROOT}/bin/python" -m pip install --disable-pip-version-check --quiet \
  "apache-airflow[standard]==${AIRFLOW_VERSION}" \
  --constraint "${CONSTRAINT_URL}"
"${VENV_ROOT}/bin/python" -m pip check

installed_version="$("${VENV_ROOT}/bin/airflow" version)"
[[ "${installed_version}" == "${AIRFLOW_VERSION}" ]] ||
  fail "expected Airflow ${AIRFLOW_VERSION}, found ${installed_version}"

sed \
  -e "s|@@AIRFLOW_HOME@@|${AIRFLOW_HOME_DIR}|g" \
  -e "s|@@DAGS_FOLDER@@|${DAGS_FOLDER}|g" \
  -e "s|@@PASSWORD_FILE@@|${PASSWORD_FILE}|g" \
  -e "s|@@AIRFLOW_PORT@@|${AIRFLOW_PORT}|g" \
  -e "s|@@ADMIN_USER@@|${ADMIN_USER}|g" \
  "${ENV_TEMPLATE}" >"${ENV_FILE}.tmp"
install -o root -g airflow -m 0640 "${ENV_FILE}.tmp" "${ENV_FILE}"
rm -f "${ENV_FILE}.tmp"
install -o root -g root -m 0644 "${SYSTEMD_UNIT}" "${SERVICE_FILE}"

chown -R root:root /opt/airflow
chmod -R go-w /opt/airflow
chown -R airflow:airflow "${AIRFLOW_HOME_DIR}"

set -a
# shellcheck disable=SC1090
source "${ENV_FILE}"
set +a
runuser -u airflow -- "${VENV_ROOT}/bin/airflow" db migrate

ADMIN_USER="${ADMIN_USER}" PASSWORD_FILE="${PASSWORD_FILE}" \
  "${PYTHON_BIN}" - <<'PY'
import json
import os
import secrets

path = os.environ["PASSWORD_FILE"]
username = os.environ["ADMIN_USER"]
temporary_path = f"{path}.tmp"
credentials = {}
if os.path.exists(path) and os.path.getsize(path):
    with open(path, encoding="utf-8") as handle:
        credentials = json.load(handle)
    if not isinstance(credentials, dict):
        raise ValueError(f"credential file must contain a JSON object: {path}")
if not credentials.get(username):
    credentials[username] = secrets.token_urlsafe(32)
with open(temporary_path, "w", encoding="utf-8") as handle:
    json.dump(credentials, handle, sort_keys=True)
    handle.write("\n")
os.chmod(temporary_path, 0o600)
os.replace(temporary_path, path)
PY
chown airflow:airflow "${PASSWORD_FILE}"
chmod 0600 "${PASSWORD_FILE}"

systemctl daemon-reload
if systemctl is-active --quiet airflow-standalone.service; then
  systemctl enable airflow-standalone.service
  systemctl restart airflow-standalone.service
else
  systemctl enable --now airflow-standalone.service
fi

HEALTH_URL="http://127.0.0.1:${AIRFLOW_PORT}/api/v2/monitor/health"
ready="false"
for _ in {1..90}; do
  if HEALTH_URL="${HEALTH_URL}" "${PYTHON_BIN}" - <<'PY'
import json
import os
import urllib.request

required = ("metadatabase", "scheduler", "dag_processor", "triggerer")
try:
    with urllib.request.urlopen(os.environ["HEALTH_URL"], timeout=2) as response:
        payload = json.load(response)
except Exception:
    raise SystemExit(1)

for component in required:
    if payload.get(component, {}).get("status") != "healthy":
        raise SystemExit(1)
PY
  then
    ready="true"
    break
  fi
  sleep 2
done
[[ "${ready}" == "true" ]] || {
  systemctl status airflow-standalone.service --no-pager >&2 || true
  journalctl -u airflow-standalone.service -n 100 --no-pager >&2 || true
  fail "Airflow health did not become ready at ${HEALTH_URL}"
}

for _ in {1..60}; do
  [[ -s "${PASSWORD_FILE}" ]] && break
  sleep 1
done
[[ -s "${PASSWORD_FILE}" ]] ||
  fail "SimpleAuthManager credential file is unavailable: ${PASSWORD_FILE}"
chown airflow:airflow "${PASSWORD_FILE}"
chmod 0600 "${PASSWORD_FILE}"

systemctl is-active --quiet "${MOCK_SERVICE}" ||
  fail "existing mock service stopped during Airflow installation"
curl --fail --silent --show-error \
  http://127.0.0.1:8080/health >/dev/null ||
  fail "existing mock health check failed after Airflow installation"
MOCK_PID_AFTER="$(systemctl show --property MainPID --value "${MOCK_SERVICE}")"
MOCK_UNIT_SHA_AFTER="$(sha256sum "${MOCK_UNIT}" | awk '{print $1}')"
[[ "${MOCK_PID_AFTER}" == "${MOCK_PID_BEFORE}" ]] ||
  fail "existing mock process changed during Airflow installation"
[[ "${MOCK_UNIT_SHA_AFTER}" == "${MOCK_UNIT_SHA_BEFORE}" ]] ||
  fail "existing mock systemd unit changed during Airflow installation"
ss -ltnH "sport = :8080" | grep -q . ||
  fail "existing mock listener on port 8080 is unavailable"
ss -ltnH "sport = :${AIRFLOW_PORT}" | grep -q "127.0.0.1:${AIRFLOW_PORT}" ||
  fail "Airflow is not listening on loopback port ${AIRFLOW_PORT}"

echo "READY Airflow ${AIRFLOW_VERSION} at 127.0.0.1:${AIRFLOW_PORT}"
echo "Credentials: sudo cat ${PASSWORD_FILE}"
