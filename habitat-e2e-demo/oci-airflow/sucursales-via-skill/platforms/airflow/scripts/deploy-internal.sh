#!/usr/bin/env bash
set -euo pipefail
APP_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"; CONFIG=""; APP_NAME=""; DRY_RUN=no
while (($#)); do case "$1" in --config) CONFIG="${2:-}"; shift 2;; --app-name) APP_NAME="${2:-}"; shift 2;; --dry-run) DRY_RUN=yes; shift;; *) echo 'usage: ./deploy.sh --config PATH --app-name NAME [--dry-run]' >&2; exit 2;; esac; done
[[ -n "$CONFIG" && -n "$APP_NAME" && -f "$CONFIG" ]] || exit 2
set -a; source "$CONFIG"; set +a
for name in VM_PUBLIC_IP VM_SSH_USER VM_SSH_KEY_PATH AIRFLOW_DAGS_FOLDER AIRFLOW_BIN AIRFLOW_DAG_ID DAG_FILE DAG_CHECKSUM MOCK_OWNERSHIP MOCK_BASE_URL; do [[ -n "${!name:-}" ]] || { echo "missing config: $name" >&2; exit 2; }; done
[[ "$MOCK_OWNERSHIP" == external-reuse ]] || { echo 'this migration requires MOCK_OWNERSHIP=external-reuse' >&2; exit 2; }
dag="$DAG_FILE"; [[ "$dag" = /* ]] || dag="$APP_ROOT/$dag"; checksum="$DAG_CHECKSUM"; [[ "$checksum" = /* ]] || checksum="$APP_ROOT/$checksum"
python3 -c 'import pathlib,sys; compile(pathlib.Path(sys.argv[1]).read_text(),sys.argv[1],"exec")' "$dag"
(cd "$(dirname "$dag")" && shasum -a 256 -c "$(basename "$checksum")")
echo "Dependency gates: DAG checksum valid; external mock URL will be materialized; app=${APP_NAME}"
[[ "$DRY_RUN" == yes ]] && { echo 'DRY-RUN: no SSH, Airflow, or mock action performed.'; exit 0; }
chmod 600 "$VM_SSH_KEY_PATH"; options=(-i "$VM_SSH_KEY_PATH" -o BatchMode=yes -o ConnectTimeout=15 -o StrictHostKeyChecking=accept-new); target="$VM_SSH_USER@$VM_PUBLIC_IP"; filename="$(basename "$dag")"; tmp="$(ssh "${options[@]}" "$target" 'mktemp /tmp/sucursales-dag.XXXXXX')"; trap 'ssh "${options[@]}" "$target" "rm -f -- $tmp" >/dev/null 2>&1 || true' EXIT
scp "${options[@]}" "$dag" "$target:$tmp"; digest="$(shasum -a 256 "$dag" | awk '{print $1}')"
ssh "${options[@]}" "$target" "printf '%s  %s\\n' '$digest' '$tmp' | sha256sum -c - && sudo install -o airflow -g airflow -m 0644 '$tmp' '$AIRFLOW_DAGS_FOLDER/.$filename.new' && sudo mv -f '$AIRFLOW_DAGS_FOLDER/.$filename.new' '$AIRFLOW_DAGS_FOLDER/$filename' && sudo -u airflow env AIRFLOW_HOME=/var/lib/airflow AIRFLOW__CORE__DAGS_FOLDER='$AIRFLOW_DAGS_FOLDER' $AIRFLOW_BIN variables set sucursales_mock_base_url '$MOCK_BASE_URL' && sudo -u airflow env AIRFLOW_HOME=/var/lib/airflow AIRFLOW__CORE__DAGS_FOLDER='$AIRFLOW_DAGS_FOLDER' $AIRFLOW_BIN dags list-import-errors --output json && sudo -u airflow env AIRFLOW_HOME=/var/lib/airflow AIRFLOW__CORE__DAGS_FOLDER='$AIRFLOW_DAGS_FOLDER' $AIRFLOW_BIN dags unpause '$AIRFLOW_DAG_ID'"
echo "READY: ${AIRFLOW_DAG_ID} installed and unpaused; external mock untouched."
