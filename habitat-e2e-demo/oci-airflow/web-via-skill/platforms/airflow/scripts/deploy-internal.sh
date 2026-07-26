#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_ROOT="$(cd "${SCRIPT_DIR}/../../.." && pwd)"
CONFIG=""
APP_NAME=""
DRY_RUN=no

usage() {
  echo "usage: ./deploy.sh --config PATH --app-name NAME [--dry-run]" >&2
}

while (($#)); do
  case "$1" in
    --config) CONFIG="${2:-}"; shift 2 ;;
    --app-name) APP_NAME="${2:-}"; shift 2 ;;
    --dry-run) DRY_RUN=yes; shift ;;
    *) usage; exit 2 ;;
  esac
done

[[ -n "$CONFIG" && -f "$CONFIG" && -n "$APP_NAME" ]] || { usage; exit 2; }
CONFIG="$(cd "$(dirname "$CONFIG")" && pwd)/$(basename "$CONFIG")"
CONFIG_DIR="$(dirname "$CONFIG")"
set -a
# shellcheck disable=SC1090
source "$CONFIG"
set +a

[[ "$VM_SSH_KEY_PATH" = /* ]] || VM_SSH_KEY_PATH="$CONFIG_DIR/$VM_SSH_KEY_PATH"
for name in VM_PUBLIC_IP VM_SSH_USER VM_SSH_KEY_PATH AIRFLOW_INSTANCE_OCID AIRFLOW_HOME AIRFLOW_DAGS_FOLDER AIRFLOW_BIN AIRFLOW_DAG_ID DAG_FILE DAG_CHECKSUM MOCK_OWNERSHIP MOCK_BASE_URL; do
  [[ -n "${!name:-}" ]] || { echo "missing config: $name" >&2; exit 2; }
done
[[ "$MOCK_OWNERSHIP" == "external-reuse" ]] || { echo "MOCK_OWNERSHIP must be external-reuse" >&2; exit 2; }
[[ -f "$VM_SSH_KEY_PATH" ]] || { echo "SSH key is not a readable file: $VM_SSH_KEY_PATH" >&2; exit 2; }

dag="$DAG_FILE"
checksum="$DAG_CHECKSUM"
[[ "$dag" = /* ]] || dag="$APP_ROOT/$dag"
[[ "$checksum" = /* ]] || checksum="$APP_ROOT/$checksum"
[[ -f "$dag" && -f "$checksum" ]] || { echo "DAG or checksum file is missing" >&2; exit 2; }
python3 -c 'import pathlib,sys; compile(pathlib.Path(sys.argv[1]).read_text(),sys.argv[1],"exec")' "$dag"
(cd "$(dirname "$dag")" && shasum -a 256 -c "$(basename "$checksum")")
python3 "$APP_ROOT/../../migration-skill/airflow-builder/scripts/validate_airflow_dag.py" "$dag" --dag-id "$AIRFLOW_DAG_ID"
echo "Dependency gates: DAG checksum valid; external mock URL will be materialized; app=${APP_NAME}"

if [[ "$DRY_RUN" == yes ]]; then
  echo "DRY-RUN: no SSH, Airflow, or mock action performed."
  exit 0
fi

ssh_options=(-i "$VM_SSH_KEY_PATH" -o BatchMode=yes -o ConnectTimeout=15 -o StrictHostKeyChecking=accept-new)
target="$VM_SSH_USER@$VM_PUBLIC_IP"
filename="$(basename "$dag")"
remote_tmp="$(ssh "${ssh_options[@]}" "$target" "mktemp /tmp/${filename}.XXXXXX")"
pipeline_file="$APP_ROOT/implementation/web_pipeline.py"
transformations_file="$APP_ROOT/implementation/web_transformations.py"
[[ -f "$pipeline_file" && -f "$transformations_file" ]] || { echo "Airflow implementation modules are missing" >&2; exit 2; }
remote_pipeline="$(ssh "${ssh_options[@]}" "$target" "mktemp /tmp/habitat-web-pipeline.XXXXXX")"
remote_transformations="$(ssh "${ssh_options[@]}" "$target" "mktemp /tmp/habitat-web-transformations.XXXXXX")"

cleanup() {
  ssh "${ssh_options[@]}" "$target" "rm -f -- '$remote_tmp' '$remote_pipeline' '$remote_transformations'" >/dev/null 2>&1 || true
}
trap cleanup EXIT

scp "${ssh_options[@]}" "$dag" "$target:$remote_tmp"
scp "${ssh_options[@]}" "$pipeline_file" "$target:$remote_pipeline"
scp "${ssh_options[@]}" "$transformations_file" "$target:$remote_transformations"
local_digest="$(shasum -a 256 "$dag" | awk '{print $1}')"
pipeline_digest="$(shasum -a 256 "$pipeline_file" | awk '{print $1}')"
transformations_digest="$(shasum -a 256 "$transformations_file" | awk '{print $1}')"

ssh "${ssh_options[@]}" "$target" bash -s -- "$remote_tmp" "$remote_pipeline" "$remote_transformations" "$AIRFLOW_DAGS_FOLDER" "$filename" "$local_digest" "$pipeline_digest" "$transformations_digest" "$AIRFLOW_HOME" "$AIRFLOW_BIN" "$AIRFLOW_DAG_ID" "$MOCK_BASE_URL" <<'REMOTE'
set -euo pipefail
remote_tmp="$1"
remote_pipeline="$2"
remote_transformations="$3"
configured_dags_folder="$4"
filename="$5"
expected_digest="$6"
pipeline_digest="$7"
transformations_digest="$8"
airflow_home="$9"
airflow_bin="${10}"
dag_id="${11}"
mock_base_url="${12}"
airflow_path="$(dirname "$airflow_bin"):/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"

[[ -x "$airflow_bin" ]] || { echo "Airflow binary is not executable: $airflow_bin" >&2; exit 2; }
pgrep -u airflow -f 'airflow scheduler' >/dev/null || { echo "Airflow scheduler is inactive; start its existing service, then retry deployment" >&2; exit 2; }
sudo -n -u airflow test -d "$configured_dags_folder" || { echo "Airflow DAG folder is unavailable to the service user: $configured_dags_folder" >&2; exit 2; }
airflow() {
  sudo -n -u airflow env AIRFLOW_HOME="$airflow_home" AIRFLOW__CORE__DAGS_FOLDER="$configured_dags_folder" PATH="$airflow_path" "$airflow_bin" "$@"
}
airflow_json() {
  airflow "$@" 2>/dev/null | sed -n '/^[[:space:]]*\[/,$p'
}
actual_dags_folder="$(airflow config get-value core dags_folder)"
[[ "$actual_dags_folder" == "$configured_dags_folder" ]] || { echo "configured DAG folder differs from active Airflow config: $configured_dags_folder != $actual_dags_folder" >&2; exit 2; }
printf '%s  %s
' "$expected_digest" "$remote_tmp" | sha256sum -c -
printf '%s  %s
' "$pipeline_digest" "$remote_pipeline" | sha256sum -c -
printf '%s  %s
' "$transformations_digest" "$remote_transformations" | sha256sum -c -
sudo -n install -d -o airflow -g airflow -m 0755 "$configured_dags_folder/habitat_web"
sudo -n install -o airflow -g airflow -m 0644 "$remote_pipeline" "$configured_dags_folder/habitat_web/.web_pipeline.py.new"
sudo -n install -o airflow -g airflow -m 0644 "$remote_transformations" "$configured_dags_folder/habitat_web/.web_transformations.py.new"
sudo -n mv -f "$configured_dags_folder/habitat_web/.web_pipeline.py.new" "$configured_dags_folder/habitat_web/web_pipeline.py"
sudo -n mv -f "$configured_dags_folder/habitat_web/.web_transformations.py.new" "$configured_dags_folder/habitat_web/web_transformations.py"
sudo -n install -o airflow -g airflow -m 0644 "$remote_tmp" "$configured_dags_folder/.${filename}.new"
sudo -n mv -f "$configured_dags_folder/.${filename}.new" "$configured_dags_folder/$filename"
airflow variables set habitat_web_mock_base_url "$mock_base_url"

for attempt in $(seq 1 18); do
  import_errors="$(airflow_json dags list-import-errors --output json)"
  if [[ "$import_errors" != "[]" ]]; then
    echo "Airflow reports DAG import errors:" >&2
    printf '%s
' "$import_errors" >&2
    exit 1
  fi
  if airflow_json dags list --output json | grep -Fq "\"dag_id\": \"$dag_id\""; then
    airflow dags unpause "$dag_id"
    exit 0
  fi
  sleep 5
done
echo "DAG was installed but was not indexed within 90 seconds: $dag_id" >&2
exit 1
REMOTE

echo "READY: ${AIRFLOW_DAG_ID} installed and unpaused; external mock untouched."
echo "Airflow public URL: ${AIRFLOW_PUBLIC_URL:-not configured}"
echo "Airflow user: ${AIRFLOW_UI_USERNAME:-not configured}"
if [[ "${AIRFLOW_PRINT_UI_PASSWORD:-no}" == yes && -n "${AIRFLOW_UI_PASSWORD:-}" ]]; then
  echo "Airflow password: ${AIRFLOW_UI_PASSWORD}"
elif [[ -n "${AIRFLOW_UI_PASSWORD:-}" ]]; then
  echo "Airflow password: configured in AIRFLOW_UI_PASSWORD (not displayed)"
else
  echo "Airflow password: not configured"
fi
