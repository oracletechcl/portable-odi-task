# Specification: Sucursales OCI Data Integration Migration

## Status

- State: approved
- Date: 2026-07-24
- Canonical input:
  `habitat-e2e-demo/sot/Pentaho_Habitat_Sucursales-llm-assets/migration-spec/Sucursales/spec.md`
- Supporting evidence: the original Pentaho job and five transformations
- Target: OCI Data Integration pipeline with a machine-ready mock backend

## Problem

The Sucursales Pentaho workload depends on unavailable databases, extraction
scripts, file shares, and mail infrastructure. It cannot be demonstrated or
tested safely outside its original environment. The migration must preserve
the evidenced processing contract while replacing every unavailable boundary
with deterministic mocks.

## Functional Scope

### Orchestration

The migrated flow must preserve:

1. Resolve the current and previous calendar-month periods.
2. Process previous-month Atenciones.
3. Process current-month Atenciones.
4. Process previous-month Agendamiento.
5. Process current-month Agendamiento.
6. Validate all outputs.
7. Complete successfully only when every processing step succeeds.
8. Finish as failed without notification when period resolution fails.
9. Record a mock error notification and finish as failed when one of the four
   Atenciones/Agendamiento processing stages fails.

### Transformations

The implementation must preserve the evidenced behavior of:

- `transf_obtenerPeriodoExtraer`
- `transf_AtencionesZeroQ_TDS`
- `transf_AgendamientoZeroQ_TDS`
- `transf_MotivoAtencionZeroQ_TDS`
- `transf_MotivoAgendamientoZeroQ_TDS`

This includes source field ordering, target field ordering, date/time formats,
`fechaCierre`, literal-dot removal from DNI values while preserving hyphens,
`~|` output separation, and aligned motivo hierarchy expansion.

### Mock Boundaries

One standard-library HTTP service must replace all unavailable boundaries. It
must expose:

- `GET /health`
- `POST /v1/periods`
- `POST /v1/process/atenciones`
- `POST /v1/process/agendamientos`
- `POST /v1/validate`
- `POST /v1/notify-error`

The service must be started through exactly one public startup entrypoint:
`implementation/start-mock-backend.sh`. The same wrapper is included in the
runtime bundle for a user-supplied machine.

Processing requests use `as_of_date` and `window=previous|current`. The API
adapter derives and reports the source shell contract values: start date, end
date, literal `true`, and period `YYYYMM`. Each base processing request also
creates its matching approved `Motivo*` output.

### Machine-Ready Runtime

- The mock service is packaged as a deterministic runtime-only archive.
- The archive contains the wrapper, Python package, configuration, and fixtures.
- The user supplies and operates the destination machine and network.
- No Terraform, cloud-init, systemd, IAM, VCN, subnet, or firewall scripting is
  included.
- No credentials, keys, OCIDs, or environment endpoints are introduced into
  the migrated release.

### OCI Data Integration Artifact

- The pipeline uses OCI Data Integration synchronous REST task operators.
- The private backend URL is a required runtime parameter.
- Success and failure branches reflect the Pentaho job contract.
- Referenced REST tasks are included in the export.
- The final asset is a deterministic ZIP named
  `HABITAT_SUCURSALES.project.zip`.
- The ZIP uses the manifest/object layout of
  `habitat-e2e-demo/sot/canonical-project.project`, roots
  `objectKeysProvidedForExport` at the `USER_PROJECT`, and passes offline
  structural validation.

### Expected Output

For the demonstration date `2026-07-15`, the release must contain output for
periods `202606` and `202607`. Each period contains:

- `AtencionesZeroQ.csv`
- `MotivoAtencionZeroQ.csv`
- `AgendamientoZeroQ.csv`
- `MotivoAgendamientoZeroQ.csv`

A run manifest records periods, task status, row counts, and SHA-256 checksums.

## Acceptance Criteria

### AC-01 — Job Topology

The complete flow runs in the approved order and implements deterministic
success, notification, and abort behavior.

### AC-02 — Period Calculation

Previous/current calendar-month windows are correct for normal dates,
year-boundary dates, and leap years. Invalid dates fail clearly.

### AC-03 — Base Transformations

Atenciones and Agendamiento preserve their evidenced schemas, ordering,
formatting, punctuation cleanup, and output delimiter.

### AC-04 — Motivo Transformations

Motivo IDs and descriptions split by ordinal, remain aligned to their parent
record, populate the evidenced hierarchy fields, and reject mismatched pairs.

### AC-05 — Mock API

All six inferred endpoints work locally with JSON responses and no external
dependency. Processing supports previous/current windows.

### AC-06 — Single Startup Point

The bash wrapper starts the complete mock service locally or on a user-supplied
machine. A wrapper-started smoke test reaches the health endpoint.

### AC-07 — Failure Semantics

An injected processing failure records one mock notification, prevents later
success-path work, and returns a failed run state. An injected period failure
aborts without notification.

### AC-08 — Expected Output

A fixed run produces eight deterministic CSV files and a checksummed manifest.

### AC-09 — OCI Import Asset

The `HABITAT_SUCURSALES.project.zip` has valid ZIP integrity, a complete
manifest rooted at `USER_PROJECT`, existing object references, supported model
types, unique stable keys, and a parameterized backend URL.

### AC-10 — Machine-Ready Backend Bundle

A deterministic runtime-only archive contains the backend, fixtures,
configuration, and shared wrapper without tests, caches, or provisioning files.

### AC-11 — Security and Portability

New migration release and runtime files contain no source credential
values, real OCIDs, real hostnames, real email addresses, or machine-local
absolute paths. TEST and PROD consume the same checksummed immutable ZIP.
Pre-existing tracked SOT findings are reported without modifying the evidence.

### AC-12 — Validation

Focused tests and all repository completion commands run and are recorded.
Unavailable external tooling or live OCI access is reported accurately.

## Non-Functional Requirements

- Pure transformation functions must run without OCI services.
- The mock runtime has no third-party production dependency.
- API responses remain below OCI Data Integration REST task response limits.
- ZIP content and checksums are deterministic.
- Shell scripts use `set -euo pipefail`.
- The release is configuration-driven and environment-neutral.

## Non-Goals

- Live deployment or import.
- Machine, network, firewall, or service-manager provisioning.
- Terraform, cloud-init, systemd, IAM, VCN, and subnet scripting.
- Original backend connectivity.
- Real email delivery.
- Secret management implementation.
- Production sizing, availability, or disaster recovery.
- Changing unrelated portability-demo assets.

## Assumptions

- The supplied Pentaho XML is sufficient evidence for transformation behavior.
- The absent extractor shell scripts are represented by fixture-backed HTTP
  operations whose request arguments match the job's period/window intent.
- The base Atenciones/Agendamiento transformations do not literally invoke the
  Motivo transformations. Producing each base/Motivo pair in one target
  processing operation is the approved integration design for whole-flow
  coverage.
- Rejecting unequal Motivo ID/description pairs is an explicit target guardrail
  because the source has no rejection branch for that malformed input.
- A zero-row source produces a zero-byte, headerless output file, matching the
  Pentaho no-header output contract.
- Per-period output directories prevent the original constant output names
  from overwriting each other while preserving the filenames within each run.
- A live OCI import remains the final environmental verification after this
  offline proof of compatibility.

## Open Questions

None.
