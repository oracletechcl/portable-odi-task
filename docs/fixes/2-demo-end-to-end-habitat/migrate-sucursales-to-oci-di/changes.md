# Sucursales Migration Changes

## Root Cause Analysis

### Observed Failure

The Pentaho Sucursales workload cannot run in this repository because its
databases, vendor extractors, shared filesystems, and mail server are
unavailable.

### Underlying Cause

The original orchestration is environment-coupled. Runtime behavior depends on
external shell scripts, database connections, mutable job variables, and
environment-specific notification configuration.

### Why Existing Guardrails Allowed It

The repository previously contained only a separate customer portability proof
of concept. It had no executable Sucursales contract, mock boundary, expected
outputs, OCI import package, or tests capable of detecting behavioral drift.

## How It Was Fixed

The five Pentaho transformations and job control flow were rebuilt as
dependency-free, testable Python:

- calendar period derivation;
- strict Atenciones and Agendamiento base transformations;
- paired Motivo hierarchy expansion;
- exact ISO-8859-1, `~|`, LF-only, headerless outputs;
- success sequencing and distinct period/processing/validation failure paths.

A standard-library HTTP service now replaces every unavailable boundary. One
bash wrapper starts all endpoints and works from any current directory. A
deterministic runtime-only tar contains the wrapper, implementation,
configuration, and fixtures for a user-supplied machine.

The OCI Data Integration release contains seven synchronous REST tasks, the
complete pipeline graph, four explicit processing-failure notification
operators, one end operator, and a runnable pipeline task. Runtime parameters
provide the backend URL and demonstration date. First-class objects use the
supplied OCI sample's export envelope without copying its OCIDs or user
metadata.

Terraform, cloud-init, systemd, IAM, VCN, subnet, firewall, and machine
provisioning were removed when the user excluded infrastructure scripting.

## Summary

- Added the portable implementation, fixtures, 68 tests, configuration, and
  single startup wrapper under `migrated-pipeline-demo/implementation`.
- Added eight deterministic CSVs and a checksummed run manifest for
  `2026-07-15`.
- Added the OCI project staging directory and deterministic
  `HABITAT_SUCURSALES.project.zip`.
- Added the deterministic machine-ready backend tar and checksum.
- Added a complete Compute VM-to-OCI operator runbook covering systemd,
  private-network access, import, publication, execution, output comparison,
  and service operation.
- Added SDD/TDD/traceability records for the runbook acceptance contract.

## Validation

- Migrated implementation: 68 tests passed in 5.33 seconds in the final
  no-cache run; the preceding independent audit passed all 67 implementation
  tests that existed before the runbook acceptance test.
- Implementation and repository `compileall`: passed.
- Maven package: passed with only a JDK `Unsafe` deprecation warning.
- Existing OCI scripts and the new mock wrapper: `bash -n` passed.
- OCI project ZIP: 13 entries, including the canonical project and `Objects/`
  directory envelope, valid integrity, complete references, `USER_PROJECT`
  export root, deterministic checksum, canonical-project-shaped metadata, and
  no unresolved request placeholders.
- Backend tar: deterministic checksum, executable wrapper, no tests or caches.
- End-to-end README: Red/Green acceptance test passed; documented release,
  Compute VM, private-network, OCI import/publish/run, output verification, and
  service lifecycle commands were audited against the delivered artifacts and
  installed OCI CLI.
- Expected output: eight files; every hash, size, and row count matches the run
  manifest; encoding, delimiter, and line-ending checks passed.
- Security scan: no OCIDs, private keys, secret assignments, real endpoints, or
  machine-local paths in the new release archives.
- `git diff --check`: passed.

Repository-root `pytest -q` could not run because the command is absent. The
equivalent `python3 -m pytest` reached collection but the pre-existing
`tests/test_customer_transform.py` requires unavailable `pyspark`. This is a
baseline environment dependency, not a migrated-suite failure.

Live OCI import request `148d9419-b097-4c3b-8f84-9ca05b51ab3d` completed
`SUCCESSFUL` with 10 imported objects. Workspace verification returned project
`HABITAT_SUCURSALES`, pipeline `PL_HABITAT_SUCURSALES`, seven REST tasks, and
the runnable pipeline task, all with object status `8`. OCI accepted the REST
tasks without any invented manifest registry value.
