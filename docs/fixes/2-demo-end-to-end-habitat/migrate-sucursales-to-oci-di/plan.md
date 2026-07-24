# Migrate Sucursales to OCI Data Integration

## Status

- Approved: 2026-07-24
- Branch: `2-demo-end-to-end-habitat`
- Base branch: `main`
- Task: `migrate-sucursales-to-oci-di`
- Initial tracking commit: `8f3d5e0`
- Tracking pull request:
  `https://github.com/oracletechcl/portable-odi-task/pull/3`
- Pull request state: draft
- Spec-driven development: enabled
- Test-driven development: Red → Green → Refactor

## Goal

Migrate the complete Pentaho `Sucursales` workload into a portable OCI Data
Integration pipeline. Preserve the documented orchestration and all five
transformations while replacing unavailable databases, vendor extractors, file
shares, and email delivery with a deterministic mock service.

The final release must include:

1. A locally executable mock-backed implementation.
2. Expected output for a fixed demonstration date.
3. A deterministic, machine-ready mock backend bundle.
4. A deterministic OCI Data Integration `.pipeline.zip` import artifact.

## Sources of Truth

1. `habitat-e2e-demo/sot/Pentaho_Habitat_Sucursales-llm-assets/migration-spec/Sucursales/spec.md`
2. Pentaho job and transformation files under
   `habitat-e2e-demo/sot/Pentaho_Habitat_Sucursales-llm-assets/source-code/Sucursales/`
3. `habitat-e2e-demo/sot/customer-portability-demo-1.0.0.pipeline/` for OCI
   export structure
4. Current OCI Data Integration REST-task, pipeline, and import contracts

Source-of-truth inputs are evidence only. They are part of the pre-existing
tracked baseline and contain environment metadata and credential fields. This
task must not modify them or copy their values into the migrated release.

## Approved Scope

- Preserve `cargaArchivoExterno.kjb` sequencing:
  period calculation, Atenciones previous/current month, Agendamiento
  previous/current month, validation, success, and notification/abort behavior.
- Preserve:
  - `transf_obtenerPeriodoExtraer.ktr`
  - `transf_AtencionesZeroQ_TDS.ktr`
  - `transf_AgendamientoZeroQ_TDS.ktr`
  - `transf_MotivoAtencionZeroQ_TDS.ktr`
  - `transf_MotivoAgendamientoZeroQ_TDS.ktr`
- Implement business transformations as testable Python.
- Run all inferred backend behavior through one dependency-free HTTP service.
- Start that service only through
  `habitat-e2e-demo/migrated-pipeline-demo/implementation/start-mock-backend.sh`.
- Make the wrapper and backend bundle runnable on a user-supplied machine.
- Orchestrate it with OCI Data Integration synchronous REST tasks.
- Produce deterministic expected CSV outputs and checksums.
- Package the OCI export as
  `habitat-e2e-demo/migrated-pipeline-demo/target/habitat-sucursales-1.0.0.pipeline.zip`.

## Non-Goals

- Contacting the original databases, vendor services, file shares, or SMTP
  servers.
- Deploying to a live tenancy during this task.
- Provisioning a machine, network, service manager, or OCI infrastructure.
- Terraform, cloud-init, systemd, IAM, VCN, subnet, and firewall scripting.
- Copying source credentials, OCIDs, hostnames, email addresses, or endpoints.
- Encoding business transformations exclusively in OCI visual operators.
- Changing the existing customer portability proof of concept.

## Target Design

### Mock API

One Python standard-library HTTP service exposes:

- `GET /health`
- `POST /v1/periods`
- `POST /v1/process/atenciones`
- `POST /v1/process/agendamientos`
- `POST /v1/validate`
- `POST /v1/notify-error`

The processing operations accept `as_of_date` and
`window=previous|current`. Each base processing operation also creates the
matching `Motivo*` output. Requests may inject a stage failure so the
notification and abort behavior can be tested.

### OCI Pipeline

The success path is:

1. Calculate periods.
2. Process previous-month Atenciones and MotivoAtencion.
3. Process current-month Atenciones and MotivoAtencion.
4. Process previous-month Agendamiento and MotivoAgendamiento.
5. Process current-month Agendamiento and MotivoAgendamiento.
6. Validate outputs.
7. End successfully.

The four Atenciones/Agendamiento tasks have `ALL_FAILED` notification branches.
A period-calculation failure goes directly to the failed end state, matching
the Pentaho job. The pipeline uses a required `MOCK_BASE_URL` parameter and
contains no environment endpoint.

### Machine-Ready Mock Bundle

The release includes a deterministic runtime-only archive containing the mock
service, raw fixtures, configuration, and the same bash wrapper used locally.
The user supplies and operates the destination machine. No machine, network, or
service-manager provisioning is part of this task.

## TDD Plan

### Iteration 1 — Period Contract

Red:

- Previous and current month boundaries for a fixed date.
- December/January rollover.
- Leap-year month end.
- Invalid date input.

Green:

- Implement pure period-window calculation.

### Iteration 2 — Transformation Contract

Red:

- Atenciones and Agendamiento schemas, ordering, date/time formatting,
  `fechaCierre`, `~|` delimiter, and literal-dot removal from DNI values while
  preserving hyphens.
- Motivo ID/description splitting, ordinal alignment, hierarchy fields, and
  mismatched-pair rejection.

Green:

- Implement minimum pure transformation and delimited-output functions.

### Iteration 3 — Pipeline and Mock API

Red:

- Complete previous/current orchestration.
- Expected eight outputs and checksummed run manifest.
- HTTP contracts, wrapper-started health check, validation, notification, and
  injected failure handling.

Green:

- Implement the orchestrator, API, CLI, and single bash entrypoint.

### Iteration 4 — OCI Export and Machine-Ready Runtime

Red:

- Complete manifest references, valid object types, unique stable keys,
  parameterized private endpoint, deterministic ZIP, and `.pipeline.zip`
  suffix.
- No credentials, real OCIDs, or real endpoints.
- Runtime-only deterministic backend archive and single-wrapper contract.

Green:

- Implement export generation, packaging, checksums, and runtime bundle
  documentation.

### Refactor

- Remove duplication from schemas, response creation, task generation, and
  fixture handling while keeping all focused tests green.

## Planned Files

### Documentation

- `docs/fixes/2-demo-end-to-end-habitat/migrate-sucursales-to-oci-di/plan.md`
- `docs/fixes/2-demo-end-to-end-habitat/migrate-sucursales-to-oci-di/spec.md`
- `docs/fixes/2-demo-end-to-end-habitat/migrate-sucursales-to-oci-di/traceability.md`
- `docs/fixes/2-demo-end-to-end-habitat/migrate-sucursales-to-oci-di/tdd.md`
- `docs/fixes/2-demo-end-to-end-habitat/migrate-sucursales-to-oci-di/changes.md`
- `docs/fixes/2-demo-end-to-end-habitat-2-tdd.md`
- `habitat-e2e-demo/migrated-pipeline-demo/README.md`
- `.gitignore`

### Implementation

- `habitat-e2e-demo/migrated-pipeline-demo/implementation/pyproject.toml`
- `habitat-e2e-demo/migrated-pipeline-demo/implementation/start-mock-backend.sh`
- `habitat-e2e-demo/migrated-pipeline-demo/implementation/config/pipeline.yaml`
- `habitat-e2e-demo/migrated-pipeline-demo/implementation/habitat_sucursales/__init__.py`
- `habitat-e2e-demo/migrated-pipeline-demo/implementation/habitat_sucursales/__main__.py`
- `habitat-e2e-demo/migrated-pipeline-demo/implementation/habitat_sucursales/cli.py`
- `habitat-e2e-demo/migrated-pipeline-demo/implementation/habitat_sucursales/contracts.py`
- `habitat-e2e-demo/migrated-pipeline-demo/implementation/habitat_sucursales/mock_api.py`
- `habitat-e2e-demo/migrated-pipeline-demo/implementation/habitat_sucursales/oci_export.py`
- `habitat-e2e-demo/migrated-pipeline-demo/implementation/habitat_sucursales/periods.py`
- `habitat-e2e-demo/migrated-pipeline-demo/implementation/habitat_sucursales/pipeline.py`
- `habitat-e2e-demo/migrated-pipeline-demo/implementation/habitat_sucursales/transformations.py`

### Fixtures and Tests

- Four raw fixture CSVs under
  `habitat-e2e-demo/migrated-pipeline-demo/implementation/fixtures/raw/{202606,202607}/`
- `habitat-e2e-demo/migrated-pipeline-demo/implementation/tests/conftest.py`
- `habitat-e2e-demo/migrated-pipeline-demo/implementation/tests/test_mock_api.py`
- `habitat-e2e-demo/migrated-pipeline-demo/implementation/tests/test_oci_export.py`
- `habitat-e2e-demo/migrated-pipeline-demo/implementation/tests/test_periods.py`
- `habitat-e2e-demo/migrated-pipeline-demo/implementation/tests/test_pipeline.py`
- `habitat-e2e-demo/migrated-pipeline-demo/implementation/tests/test_security.py`
- `habitat-e2e-demo/migrated-pipeline-demo/implementation/tests/test_start_wrapper.py`
- `habitat-e2e-demo/migrated-pipeline-demo/implementation/tests/test_transformations.py`

### Generated Release and Expected Outputs

- Eight CSVs under
  `habitat-e2e-demo/migrated-pipeline-demo/target/expected-output/{202606,202607}/`
- `habitat-e2e-demo/migrated-pipeline-demo/target/expected-output/run-manifest.json`
- OCI manifest plus ten object JSON files under
  `habitat-e2e-demo/migrated-pipeline-demo/target/habitat-sucursales-1.0.0.pipeline/`
- `habitat-e2e-demo/migrated-pipeline-demo/target/habitat-sucursales-1.0.0.pipeline.zip`
- `habitat-e2e-demo/migrated-pipeline-demo/target/habitat-sucursales-1.0.0.pipeline.zip.sha256`
- `habitat-e2e-demo/migrated-pipeline-demo/target/habitat-sucursales-mock-backend-1.0.0.tar.gz`
- `habitat-e2e-demo/migrated-pipeline-demo/target/habitat-sucursales-mock-backend-1.0.0.tar.gz.sha256`

## Agent Roster and File Ownership

Phase 3 roster started after the tracking pull request became visible:

| Agent | State | Responsibility | Files |
| --- | --- | --- | --- |
| `/root/transformation_owner` | Audit-hardened Green complete: 34 passed | Red/Green for periods and transformations | `contracts.py`, `periods.py`, `transformations.py`, `pipeline.py`, raw fixtures, period/transformation/pipeline tests |
| `/root/oci_mock_owner` | Green complete: full implementation suite 67 passed | Red/Green for mock service, OCI export, wrapper, and runtime bundle | `mock_api.py`, `oci_export.py`, CLI, wrapper, config, related tests |
| `/root/verification_auditor` | Final package audit complete | Independent security, SDD/TDD, and validation audit | Read-only; reports findings to integration owner |
| `/root` | Integration owner | Tracking docs, integration, packaging, conflict resolution, commits, PR | Task docs, branch TDD readout, README, `.gitignore`, `pyproject.toml`, generated target outputs, final validation |

Concurrent editing of the same file is prohibited. Conflicts: none planned.

## Validation

Focused Red/Green commands:

```text
pytest -q habitat-e2e-demo/migrated-pipeline-demo/implementation/tests/test_periods.py
pytest -q habitat-e2e-demo/migrated-pipeline-demo/implementation/tests/test_transformations.py
pytest -q habitat-e2e-demo/migrated-pipeline-demo/implementation/tests/test_pipeline.py
pytest -q habitat-e2e-demo/migrated-pipeline-demo/implementation/tests/test_mock_api.py habitat-e2e-demo/migrated-pipeline-demo/implementation/tests/test_start_wrapper.py
pytest -q habitat-e2e-demo/migrated-pipeline-demo/implementation/tests/test_oci_export.py habitat-e2e-demo/migrated-pipeline-demo/implementation/tests/test_security.py
```

Completion gates:

```text
python -m compileall habitat-e2e-demo/migrated-pipeline-demo/implementation/habitat_sucursales
python -m compileall src
pytest -q
mvn -q -DskipTests package
find platforms/oci -name "*.sh" -exec bash -n {} \;
```

Live OCI import is out of scope because no tenancy access is available;
offline structural compatibility remains mandatory. Security scans cover the
new migration release and machine-ready runtime files;
pre-existing tracked SOT risks are reported separately and not rewritten by
this task.
