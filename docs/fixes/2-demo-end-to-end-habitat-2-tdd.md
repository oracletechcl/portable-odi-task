# Branch TDD Readout: Sucursales OCI Data Integration Migration

## Identity

- Branch: `2-demo-end-to-end-habitat`
- Numeric token: `2`
- Task: `migrate-sucursales-to-oci-di`
- Detailed task log:
  `docs/fixes/2-demo-end-to-end-habitat/migrate-sucursales-to-oci-di/tdd.md`
- Specification:
  `docs/fixes/2-demo-end-to-end-habitat/migrate-sucursales-to-oci-di/spec.md`
- Status: complete; live OCI import verified

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
- The final project export must pass both offline structure checks and a live
  OCI Data Integration import.
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

The project-packaging specification change then entered Red with four expected
failures. The manifest still rooted the export at `PIPELINE_TASK`, while the
writer and packager still required `.pipeline` and `.pipeline.zip`. The new
contract roots `objectKeysProvidedForExport` at `USER_PROJECT` and requires
`.project` plus `PROJECT-NAME.project.zip`.

The first live OCI import then failed at archive parsing with zero imported
objects. A canonical-ZIP comparison showed that the package was missing the
required top-level `PROJECT-NAME.project/` envelope and explicit `Objects/`
directory entry. The revised packaging test failed on that exact mismatch
before the packager was changed.

The hardened Green includes exact placeholder-derived parameters,
canonical-project-shaped first-class objects, complete bidirectional graph links,
pipeline-task bindings, zero-row consistency, and deterministic OCI/backend
packaging. The project-export Green passed all four focused tests in 0.07
seconds.

The operator-runbook cycle then entered Red with one expected failure because
the README did not contain a complete Compute VM-to-OCI procedure. Green added
release verification, wrapper-backed systemd deployment, private VCN rules,
OCI import/publication/execution, deterministic result comparison, and service
operations. The final migrated suite passed 68 tests in 5.33 seconds.

The prepared-VM documentation was then simplified into six ordered quick-start
steps. Its revised acceptance test passed, the endpoint-safety scan found no
tracked environment values, and the migrated suite passed 68 tests in 5.08
seconds.

## Refactor

Complete. Shared metadata, parameter, checksum, and packaging helpers remove
duplication. The runtime tar excludes tests and caches. Terraform and machine
provisioning were removed from scope and from the tree.

## Verification

- Migrated no-cache suite: 67 passed.
- Package and source compileall: passed.
- Maven package: passed with a JDK deprecation warning.
- OCI scripts and mock wrapper syntax: passed.
- Project ZIP/tar integrity and checksums: passed.
- Project manifest: sole export root is the `USER_PROJECT`; 10 referenced
  objects and staging bytes match the 13-entry canonical-envelope ZIP.
- Live OCI import: request `148d9419-b097-4c3b-8f84-9ca05b51ab3d` completed
  `SUCCESSFUL` with all 10 objects imported.
- Workspace inventory: one `HABITAT_SUCURSALES` project, one
  `PL_HABITAT_SUCURSALES` pipeline, seven REST tasks, and one runnable pipeline
  task, all status `8`.
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

- Executing the imported pipeline still requires the mock backend to be
  deployed and `MOCK_BASE_URL` to be set.
- The source extractor shell scripts are absent.
- Pre-existing SOT contains environment metadata outside this task's change
  scope.

## Next Recommended Step

Deploy the mock backend on the supplied machine, set `MOCK_BASE_URL` and
`AS_OF_DATE` on `TASK_RUN_HABITAT_SUCURSALES`, and run the imported pipeline.
Promote the same checksummed project ZIP to TEST and PROD.

## Final Resolution

Complete. The requested code, mock backend, expected output, machine-ready
runtime archive, import-oriented OCI project ZIP, and end-to-end Compute
VM-to-OCI operator runbook are delivered. Live OCI import completed
successfully with all 10 objects present in the target workspace. No unverified
`REST_TASK` registry value was invented.
