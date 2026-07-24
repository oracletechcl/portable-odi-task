# Branch TDD Readout: Sucursales OCI Data Integration Migration

## Identity

- Branch: `2-demo-end-to-end-habitat`
- Numeric token: `2`
- Task: `migrate-sucursales-to-oci-di`
- Detailed task log:
  `docs/fixes/2-demo-end-to-end-habitat/migrate-sucursales-to-oci-di/tdd.md`
- Specification:
  `docs/fixes/2-demo-end-to-end-habitat/migrate-sucursales-to-oci-di/spec.md`
- Status: complete; offline OCI structure verified

## Problem Statement

The original Pentaho Sucursales job cannot run outside its source environment
because its database, extractor, filesystem, and notification dependencies are
unavailable. The task migrates the complete behavior to OCI Data Integration
with deterministic mocks and a machine-ready runtime bundle.

## Assumptions

- The approved migration specification is canonical.
- Pentaho XML resolves missing behavioral detail.
- The absent extractor shell scripts are represented by fixture-backed REST
  operations.
- A live OCI import cannot be run in this environment; offline structural
  compatibility and ZIP integrity are required.
- The pre-existing tracked SOT contains environment metadata and is not
  modified or copied into the release.

## Target Files

- Pure behavior under
  `habitat-e2e-demo/migrated-pipeline-demo/implementation/habitat_sucursales/`
- Tests and raw fixtures under
  `habitat-e2e-demo/migrated-pipeline-demo/implementation/`
- Release assets under
  `habitat-e2e-demo/migrated-pipeline-demo/target/`

## Planned Test Scope

- Calendar period calculation and boundary cases.
- Base Atenciones and Agendamiento transformations.
- Motivo split, hierarchy, pairing, and mismatch guardrail.
- Complete success and failure orchestration.
- Mock HTTP API and single bash wrapper smoke test.
- OCI REST task/pipeline object structure and deterministic ZIP.
- Deterministic runtime-only backend bundle.
- New-release security and portability checks.

## Red

### Periods, Transformations, and Pipeline

Tests and raw fixtures were created before implementation. The focused command
failed during collection with three expected missing-module errors for
`periods`, `transformations`, and `pipeline`.

### Mock API, Wrapper, OCI Export, and Runtime Bundle

Tests were created before implementation. The focused command failed during
collection with three expected missing-module errors for `mock_api` and
`oci_export`.

Detailed commands and results are recorded in the task TDD log.

## Green

The focused period, transformation, and pipeline suite first passed 13 tests.
A second Red/Green cycle added the period KTR's previous/current start and end
dates; the focused suite then passed 14 tests.

The audit-hardening Red produced 14 failures and 20 passes for missing strict
contracts. Green completed with 34 passes in 0.10 seconds.

This covers exact period windows, schemas, `YYYYMM01`, dot-only DNI cleanup,
Motivo pairing and malformed-input guardrails, eight outputs, job order, and
the distinct period/processing failure paths, exact schema/type checks,
zero-row output, byte-exact encoding/delimiters, and injection guards.

The full implementation suite passed 63 tests in 5.19 seconds. Package
compileall and wrapper `bash -n` passed. The initial Compute contract was
removed after the user explicitly excluded Terraform and provisioning.

An independent import/runtime consistency cycle then entered Red with three
expected failures: supplied-sample object metadata envelopes, undeclared REST
payload placeholders, and zero-row output validation. Detailed evidence is in
the task TDD log.

The hardened Green includes exact placeholder-derived parameters,
sample-shaped first-class objects, complete bidirectional graph links,
pipeline-task bindings, zero-row consistency, and deterministic OCI/backend
packaging. The final migrated suite passed 67 tests.

## Refactor

Complete. Shared metadata, parameter, checksum, and packaging helpers remove
duplication. The runtime tar excludes tests and caches. Terraform and machine
provisioning were removed from scope and from the tree.

## Verification

- Migrated no-cache suite: 67 passed.
- Package and source compileall: passed.
- Maven package: passed with a JDK deprecation warning.
- OCI scripts and mock wrapper syntax: passed.
- ZIP/tar integrity and checksums: passed.
- Eight output hashes, sizes, row counts, ISO-8859-1 decoding, `~|`, and LF:
  passed.
- New release/archive security scan: passed.
- Repository-root pytest: baseline collection blocked because `pyspark` is not
  installed; the migrated suite itself is fully Green.

## Root Cause / Design Rationale

The source application couples orchestration to mutable variables, external
shell commands, connection metadata, and SMTP. The target separates pure
transformations from a mock boundary and keeps OCI Data Integration responsible
only for orchestration.

## Remaining Risks

- A handcrafted export cannot be called live-import proven without an OCI
  import request.
- The source extractor shell scripts are absent.
- Pre-existing SOT contains environment metadata outside this task's change
  scope.

## Next Recommended Step

Upload the `.pipeline.zip` to Object Storage, import it into OCI Data
Integration, set `MOCK_BASE_URL` and `AS_OF_DATE`, and record the live import
result. The same checksummed asset should then be promoted to TEST and PROD.

## Final Resolution

Complete. The requested code, mock backend, expected output, machine-ready
runtime archive, and import-oriented OCI pipeline ZIP are delivered. Live OCI
import is not claimed because this environment has no tenancy access. The
supplied offline evidence also omits the internal `REST_TASK` manifest registry
ID, so no unverified registry value was invented.
