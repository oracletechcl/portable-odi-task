# Habitat Sucursales OCI Data Integration Demo

This release migrates the complete documented Pentaho Sucursales job to an OCI
Data Integration pipeline whose unavailable dependencies are replaced by a
deterministic Python mock backend.

## Release Assets

- `target/HABITAT_SUCURSALES.project.zip` — OCI Data Integration
  import-oriented project bundle.
- `target/HABITAT_SUCURSALES.project.zip.sha256` — project bundle
  checksum.
- `target/habitat-sucursales-mock-backend-1.0.0.tar.gz` — runtime-only backend
  bundle for a user-supplied machine.
- `target/habitat-sucursales-mock-backend-1.0.0.tar.gz.sha256` — backend bundle
  checksum.
- `target/expected-output/` — deterministic output for `2026-07-15`.

The `.project.zip` is structurally checked against
`sot/canonical-project.project`. Its manifest exports the `USER_PROJECT` root
and includes the pipeline, runnable pipeline task, and referenced REST tasks.
OCI import request `148d9419-b097-4c3b-8f84-9ca05b51ab3d` completed
`SUCCESSFUL` with all 10 objects imported into project `HABITAT_SUCURSALES`.

## Run the Entire End-to-End Demo

This procedure starts from the release assets in this directory and ends with a
successful `TASK_RUN_HABITAT_SUCURSALES` run in OCI Data Integration. It
assumes:

- an existing Compute VM with Python 3.10 or newer;
- the VM and the OCI Data Integration workspace are connected through the same
  VCN, or through peered networks with working routes;
- SSH access to the VM;
- OCI CLI access that can upload to bucket `odi-portability-demo` and import
  into the target workspace; and
- permission to create an OCI Data Integration application and publish/run
  tasks.

The examples use an Oracle Linux VM and the `opc` account. Replace that account
name when the supplied image uses a different login.

### 1. Verify the immutable release assets

Run from `habitat-e2e-demo/migrated-pipeline-demo` on the operator machine:

```bash
cd target
sha256sum -c HABITAT_SUCURSALES.project.zip.sha256
sha256sum -c habitat-sucursales-mock-backend-1.0.0.tar.gz.sha256
cd ..
```

Both commands must report `OK`. Do not unzip and repackage the project export;
OCI Data Integration requires the canonical `HABITAT_SUCURSALES.project/`
archive envelope.

### 2. Copy and install the mock backend on the Compute VM

Set the SSH address or bastion-resolved host on the operator machine, then copy
the runtime-only archive:

```bash
export VM_SSH_HOST="<vm-ssh-host>"

scp target/habitat-sucursales-mock-backend-1.0.0.tar.gz \
  "opc@${VM_SSH_HOST}:/tmp/"
ssh "opc@${VM_SSH_HOST}"
```

On the VM:

```bash
python3 --version
sudo install -d -o opc -g opc /opt/habitat-sucursales
tar -xzf /tmp/habitat-sucursales-mock-backend-1.0.0.tar.gz \
  -C /opt/habitat-sucursales
sudo install -d -o opc -g opc /var/lib/habitat-sucursales/output
```

The backend has no third-party Python dependencies. Its single start point is
`/opt/habitat-sucursales/implementation/start-mock-backend.sh`.

For a VM service that survives logout and restarts on failure, create this
systemd unit:

```bash
sudo tee /etc/systemd/system/habitat-sucursales-mock.service >/dev/null <<'UNIT'
[Unit]
Description=Habitat Sucursales mock backend
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=opc
WorkingDirectory=/opt/habitat-sucursales/implementation
Environment=MOCK_HOST=0.0.0.0
Environment=MOCK_PORT=8080
Environment=MOCK_OUTPUT_DIR=/var/lib/habitat-sucursales/output
ExecStart=/opt/habitat-sucursales/implementation/start-mock-backend.sh
Restart=on-failure
RestartSec=3

[Install]
WantedBy=multi-user.target
UNIT

sudo systemctl daemon-reload
sudo systemctl enable --now habitat-sucursales-mock.service
sudo systemctl status habitat-sucursales-mock.service --no-pager
curl --fail --silent --show-error http://127.0.0.1:8080/health
```

The health response must be:

```json
{"service": "habitat-sucursales-mock", "status": "ok"}
```

### 3. Allow only the private OCI Data Integration path

Record the VM private IP:

```bash
hostname -I
```

Configure the VM NSG or subnet security list to allow inbound TCP 8080 only
from the OCI Data Integration workspace private-endpoint subnet CIDR or its
NSG. Keep the VM private; do not allow TCP 8080 from `0.0.0.0/0`. If the VM
host firewall is enabled, add the equivalent source-restricted rule there.

From a host on the same private route, verify:

```bash
curl --fail --silent --show-error \
  "http://<vm-private-ip>:8080/health"
```

Do not continue until this returns HTTP 200. A local health check proves the
process is running; this private-IP check also proves the VCN path and firewall
rules.

### 4. Upload and import the OCI project

This repository's target workspace already contains the project from successful
import request `148d9419-b097-4c3b-8f84-9ca05b51ab3d`. Skip this step there.
For a clean workspace, run from the operator machine:

```bash
export OCI_REGION="us-sanjose-1"
export OCI_WORKSPACE_ID="<workspace-ocid>"
export OCI_BUCKET_NAME="odi-portability-demo"
export OCI_PROJECT_OBJECT="releases/HABITAT_SUCURSALES.project.zip"

oci os object put \
  --region "${OCI_REGION}" \
  --bucket-name "${OCI_BUCKET_NAME}" \
  --name "${OCI_PROJECT_OBJECT}" \
  --file target/HABITAT_SUCURSALES.project.zip \
  --force

export OCI_IMPORT_REQUEST_KEY="$(
  oci data-integration import-request create \
    --region "${OCI_REGION}" \
    --workspace-id "${OCI_WORKSPACE_ID}" \
    --bucket-name "${OCI_BUCKET_NAME}" \
    --file-name "${OCI_PROJECT_OBJECT}" \
    --object-storage-region "${OCI_REGION}" \
    --import-conflict-resolution \
      '{"importConflictResolutionType":"RETAIN"}' \
    --query 'data.key' \
    --raw-output
)"

oci data-integration import-request get \
  --region "${OCI_REGION}" \
  --workspace-id "${OCI_WORKSPACE_ID}" \
  --import-request-key "${OCI_IMPORT_REQUEST_KEY}" \
  --query 'data.{status:status,totalImportedObjects:"total-imported-object-count",errors:"error-messages"}'
```

Repeat the final `get` command until `status` is `SUCCESSFUL`. `FAILED` is
terminal: inspect `errors` before retrying. A successful import reports 10
objects: one project, one pipeline, one pipeline task, and seven REST tasks.

### 5. Publish the pipeline task

Imported project tasks are design-time objects. OCI Data Integration requires a
published application task before execution:

1. Open the workspace in the OCI Console.
2. Under **Applications**, create `HABITAT_SUCURSALES_DEMO` if it does not
   exist.
3. Open project `HABITAT_SUCURSALES`, then **Tasks**.
4. Publish `TASK_RUN_HABITAT_SUCURSALES` to
   `HABITAT_SUCURSALES_DEMO`. Include its referenced objects when prompted.
5. Wait for the publish patch to complete successfully.

Publishing the top-level pipeline task brings its `PL_HABITAT_SUCURSALES`
pipeline and REST task dependencies into the application.

### 6. Run the migrated pipeline

Open **Applications** > **HABITAT_SUCURSALES_DEMO** > **Tasks**, select
`TASK_RUN_HABITAT_SUCURSALES`, and choose **Run**. Override both runtime
parameters:

- `MOCK_BASE_URL` = `http://<vm-private-ip>:8080`
- `AS_OF_DATE` = `2026-07-15`

Never accept the packaged `MOCK_BASE_URL` default: it intentionally uses the
reserved `.invalid` domain. Start the run and follow it under the application's
**Runs** page until its status is **Succeeded**.

The execution order is period calculation, previous/current Atenciones,
previous/current Agendamientos, and final validation. Any failed branch invokes
`REST_NOTIFY_ERROR`; the successful path ends at `REST_VALIDATE`.

### 7. Verify the deterministic result

On the VM, a successful run creates eight CSV files: four under `202606/` and
four under `202607/`.

```bash
sudo find /var/lib/habitat-sucursales/output \
  -type f -name '*.csv' -print | sort
```

For the exact byte comparison, copy the runtime output back to the operator
machine:

```bash
export RUNTIME_CAPTURE_DIR="$(mktemp -d)"
scp -r \
  "opc@${VM_SSH_HOST}:/var/lib/habitat-sucursales/output/." \
  "${RUNTIME_CAPTURE_DIR}/"
diff -ru \
  -x run-manifest.json \
  target/expected-output/ \
  "${RUNTIME_CAPTURE_DIR}/"
```

`diff` must produce no output. The checked-in
`target/expected-output/run-manifest.json` records the expected periods, row
counts, SHA-256 values, step order, and final `SUCCEEDED` status for
`2026-07-15`.

### 8. Operate or stop the VM service

```bash
sudo journalctl -u habitat-sucursales-mock.service -n 100 --no-pager
sudo systemctl restart habitat-sucursales-mock.service
sudo systemctl stop habitat-sucursales-mock.service
```

Reusing the same date is deterministic. Before running a different
`AS_OF_DATE`, use a new empty `MOCK_OUTPUT_DIR`; validation intentionally rejects
missing or unexpected CSV files. Connection failures usually mean
`MOCK_BASE_URL`, routing, NSG/security-list rules, or the VM firewall does not
match the private path.

## Start Every Mock Endpoint

Python 3.10 or newer is the only runtime requirement. The bash wrapper is the
single public backend startup point.

```bash
cd implementation
MOCK_HOST=0.0.0.0 MOCK_PORT=8080 ./start-mock-backend.sh
```

The wrapper also accepts these environment variables:

- `MOCK_FIXTURES_DIR` — raw fixture root.
- `MOCK_OUTPUT_DIR` — generated output root.
- `MOCK_PYTHON_BIN` — Python executable; defaults to `python3`.

Health check:

```bash
curl http://127.0.0.1:8080/health
```

Available endpoints:

- `GET /health`
- `POST /v1/periods`
- `POST /v1/process/atenciones`
- `POST /v1/process/agendamientos`
- `POST /v1/validate`
- `POST /v1/notify-error`

## Run the Complete Mock Flow

```bash
cd implementation
python3 -m habitat_sucursales run \
  --as-of-date 2026-07-15 \
  --output-dir ../target/runtime-output
```

The flow runs period calculation, Atenciones for previous/current month,
Agendamientos for previous/current month, and final validation. Each processing
request creates the base and matching Motivo output.

## Put the Backend on the Supplied Machine

Copy the runtime archive to the machine, then:

```bash
tar -xzf habitat-sucursales-mock-backend-1.0.0.tar.gz
cd implementation
MOCK_HOST=0.0.0.0 MOCK_PORT=8080 ./start-mock-backend.sh
```

Machine creation, Terraform, and cloud-init remain out of scope. The complete
runbook above covers the VM network rule, systemd service, OCI publish, run, and
verification steps.

## Import and Configure OCI Data Integration

Import `target/HABITAT_SUCURSALES.project.zip` into the OCI Data
Integration workspace. Configure these runtime parameters:

- `MOCK_BASE_URL` — reachable backend URL, for example
  `http://<private-backend-host>:8080`.
- `AS_OF_DATE` — ISO date, for example `2026-07-15`.

The packaged `MOCK_BASE_URL` default uses the reserved `.invalid` domain so it
cannot accidentally contact a real service. Override it before execution.

Promote the same checksummed ZIP to TEST and PROD; only runtime parameter values
change.

## Rebuild the OCI Asset

```bash
cd implementation
python3 -m habitat_sucursales package-oci \
  --export-dir ../target/HABITAT_SUCURSALES.project \
  --zip-path ../target/HABITAT_SUCURSALES.project.zip
```

Rebuild the machine-ready backend:

```bash
cd implementation
python3 -m habitat_sucursales package-backend \
  --implementation-dir . \
  --tar-path ../target/habitat-sucursales-mock-backend-1.0.0.tar.gz
```

## Test

```bash
cd implementation
python3 -m pytest -q
bash -n start-mock-backend.sh
```
