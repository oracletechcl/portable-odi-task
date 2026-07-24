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

- Added the portable implementation, fixtures, 67 tests, configuration, and
  single startup wrapper under `migrated-pipeline-demo/implementation`.
- Added eight deterministic CSVs and a checksummed run manifest for
  `2026-07-15`.
- Added the OCI staging directory and deterministic
  `habitat-sucursales-1.0.0.pipeline.zip`.
- Added the deterministic machine-ready backend tar and checksum.
- Added operator instructions and SDD/TDD/traceability records.

## Validation

- Migrated implementation: 67 tests passed in the root no-cache run; an
  independent audit also passed all 67.
- Implementation and repository `compileall`: passed.
- Maven package: passed with only a JDK `Unsafe` deprecation warning.
- Existing OCI scripts and the new mock wrapper: `bash -n` passed.
- OCI ZIP: 11 entries, valid integrity, complete references, deterministic
  checksum, sample-shaped metadata, and no unresolved request placeholders.
- Backend tar: deterministic checksum, executable wrapper, no tests or caches.
- Expected output: eight files; every hash, size, and row count matches the run
  manifest; encoding, delimiter, and line-ending checks passed.
- Security scan: no OCIDs, private keys, secret assignments, real endpoints, or
  machine-local paths in the new release archives.
- `git diff --check`: passed.

Repository-root `pytest -q` could not run because the command is absent. The
equivalent `python3 -m pytest` reached collection but the pre-existing
`tests/test_customer_transform.py` requires unavailable `pyspark`. This is a
baseline environment dependency, not a migrated-suite failure.

Live OCI import is not claimed because no tenancy is available. The supplied
sample establishes the export layout but does not expose OCI's internal
manifest registry ID for `REST_TASK`; no guessed value was added.
