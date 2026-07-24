# Sucursales Migration TDD Log

## Task

Build a mock-backed OCI Data Integration migration of the complete Pentaho
Sucursales flow and package it as a deterministic `.pipeline.zip`.

## Initial State

- Approved specification: recorded in `spec.md`.
- Existing implementation: none.
- Existing focused tests: none.
- External backend access: unavailable by design.
- Live OCI import: unavailable.

## Red

Status: planned; no test has been written or run yet.

The first Red iteration will add:

- `test_periods.py` for calendar-window behavior.
- `test_transformations.py` for the base and motivo contracts.

Expected failure: imports fail because the `habitat_sucursales` implementation
does not exist.

No implementation file may be added before this expected failure is observed
and recorded.

## Green

Status: pending Red evidence.

## Refactor

Status: pending Green evidence.

## Verification

Status: not run.

| Command | Result |
| --- | --- |
| Focused tests | Not run |
| `python -m compileall habitat-e2e-demo/migrated-pipeline-demo/implementation/habitat_sucursales` | Not run |
| `python -m compileall src` | Not run |
| `pytest -q` | Not run |
| `mvn -q -DskipTests package` | Not run |
| OCI shell syntax checks | Not run |
| Terraform formatting/validation | Not run |

## Risks

- Offline schema checks cannot replace a live OCI import request.
- The original extractor shell scripts were not supplied, so their network
  calls are modeled from job arguments and fixture-backed behavior.
- Source evidence contains sensitive environment metadata and must remain
  untracked.

## Final Status

Open.

