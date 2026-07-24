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
and includes the pipeline, runnable pipeline task, and referenced REST tasks. A
live OCI import is not claimed because this workspace has no tenancy access.

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

Machine creation, network rules, service management, Terraform, cloud-init, and
systemd are intentionally out of scope.

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
