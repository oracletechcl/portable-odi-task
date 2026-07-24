# Habitat Sucursales OCI Data Integration Demo

This demo replaces the unavailable Pentaho dependencies with a deterministic
Python mock and runs the migrated flow in OCI Data Integration.

## Quick Start: Run the Mock and Trigger OCI Data Integration

The supplied Compute VM is already prepared:

- Login user: `opc`
- SSH key: `../ssh-keys/ssh-key-2026-07-24.key`
- Service: `habitat-sucursales-mock.service`
- Runtime: `/opt/habitat-sucursales/current`
- Output: `/var/lib/habitat-sucursales/output`
- Backend entrypoint:
  `/opt/habitat-sucursales/current/implementation/start-mock-backend.sh`
- Runtime version: Python 3.11
- Network: TCP 8080 is allowed only from the OCI Data Integration workspace
  subnet.

Repository policy does not allow real environment endpoints in tracked files.
Replace the two placeholders below with the supplied VM addresses.

### 1. Connect to the VM

From this directory:

```bash
export VM_PUBLIC_IP="<vm-public-ip>"
export VM_PRIVATE_IP="<vm-private-ip>"
export SSH_KEY="../ssh-keys/ssh-key-2026-07-24.key"

chmod 600 "${SSH_KEY}"
ssh -i "${SSH_KEY}" "opc@${VM_PUBLIC_IP}"
```

### 2. Start and check the mock

On the VM:

```bash
sudo systemctl enable --now habitat-sucursales-mock.service
sudo systemctl status habitat-sucursales-mock.service --no-pager
curl --fail http://127.0.0.1:8080/health
```

Expected response:

```json
{"service":"habitat-sucursales-mock","status":"ok"}
```

The service is already configured to listen on `0.0.0.0:8080` and to write
results under `/var/lib/habitat-sucursales/output`.

### 3. Publish the imported task once

The project is already imported. In the OCI Console:

1. Open **Data Integration** → **Workspaces** → the target workspace.
2. Under **Applications**, create `HABITAT_SUCURSALES_DEMO` if it does not
   exist.
3. Open **Projects** → `HABITAT_SUCURSALES` → **Tasks**.
4. Select `TASK_RUN_HABITAT_SUCURSALES`.
5. Publish it to `HABITAT_SUCURSALES_DEMO`, including referenced objects.

### 4. Run the OCI Data Integration task

1. Open **Applications** → `HABITAT_SUCURSALES_DEMO` → **Tasks**.
2. Select `TASK_RUN_HABITAT_SUCURSALES` and choose **Run**.
3. Override:

```text
MOCK_BASE_URL = http://<vm-private-ip>:8080
AS_OF_DATE    = 2026-07-15
```

4. Start the run and wait for **Succeeded** under **Runs**.

Use the VM private IP in `MOCK_BASE_URL`, not its public IP. The packaged
`.invalid` URL is deliberately unusable.

### 5. Check the result

On the VM:

```bash
sudo find /var/lib/habitat-sucursales/output \
  -type f -name '*.csv' -print | sort
```

A successful `2026-07-15` run creates eight CSV files: four under `202606/`
and four under `202607/`. Their deterministic reference is in
`target/expected-output`.

### 6. Logs, restart, and stop

```bash
sudo journalctl -u habitat-sucursales-mock.service -f
sudo systemctl restart habitat-sucursales-mock.service
sudo systemctl stop habitat-sucursales-mock.service
```

If OCI reports a connection timeout, verify the private IP, TCP 8080 route,
workspace subnet, and VM firewall. If the run uses `mock-backend.invalid`,
`MOCK_BASE_URL` was not overridden.

## Release Assets

- `target/HABITAT_SUCURSALES.project.zip` — importable OCI project.
- `target/HABITAT_SUCURSALES.project.zip.sha256` — project checksum.
- `target/habitat-sucursales-mock-backend-1.0.0.tar.gz` — mock VM runtime.
- `target/habitat-sucursales-mock-backend-1.0.0.tar.gz.sha256` — runtime
  checksum.
- `target/expected-output/` — reference output for `2026-07-15`.

The OCI project is also stored in bucket `odi-portability-demo` as
`releases/HABITAT_SUCURSALES.project.zip`.

For a clean workspace, upload/import `HABITAT_SUCURSALES.project.zip`, then
follow steps 3–5 above.

## Local Mock

Python 3.10 or newer is required.

```bash
cd implementation
MOCK_HOST=0.0.0.0 MOCK_PORT=8080 ./start-mock-backend.sh
```

Endpoints:

- `GET /health`
- `POST /v1/periods`
- `POST /v1/process/atenciones`
- `POST /v1/process/agendamientos`
- `POST /v1/validate`
- `POST /v1/notify-error`

## Build and Test

```bash
cd implementation
python3 -m pytest -q
bash -n start-mock-backend.sh

python3 -m habitat_sucursales package-oci \
  --export-dir ../target/HABITAT_SUCURSALES.project \
  --zip-path ../target/HABITAT_SUCURSALES.project.zip

python3 -m habitat_sucursales package-backend \
  --implementation-dir . \
  --tar-path ../target/habitat-sucursales-mock-backend-1.0.0.tar.gz
```
