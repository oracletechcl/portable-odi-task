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

### Iterations 1–3: Periods, Transformations, and Pipeline

Status: confirmed on 2026-07-24.

Tests and raw fixtures were created before their implementation modules:

- `test_periods.py` for calendar-window behavior.
- `test_transformations.py` for the base and motivo contracts.
- `test_pipeline.py` for the complete previous/current orchestration.

Command:

```text
python3 -m pytest -q \
  habitat-e2e-demo/migrated-pipeline-demo/implementation/tests/test_periods.py \
  habitat-e2e-demo/migrated-pipeline-demo/implementation/tests/test_transformations.py \
  habitat-e2e-demo/migrated-pipeline-demo/implementation/tests/test_pipeline.py
```

Result: expected failure, exit code 2. Pytest reported three collection errors:

- `ModuleNotFoundError: habitat_sucursales.periods`
- `ModuleNotFoundError: habitat_sucursales.transformations`
- `ModuleNotFoundError: habitat_sucursales.pipeline`

The failures matched the intended missing implementation seam. Minimum Green
followed.

### Iteration 4: Mock API, Wrapper, OCI Export, and Runtime Bundle

Status: confirmed on 2026-07-24.

Tests were created before `mock_api.py` and `oci_export.py`.

Command:

```text
cd habitat-e2e-demo/migrated-pipeline-demo/implementation
python3 -m pytest -q \
  tests/test_mock_api.py \
  tests/test_start_wrapper.py \
  tests/test_oci_export.py \
  tests/test_security.py
```

Result: expected failure, exit code 2. Pytest stopped collection with three
errors for the missing `habitat_sucursales.mock_api` and
`habitat_sucursales.oci_export` modules. Minimum Green followed.

The initial Red also included a Compute provisioning contract. The user then
removed Terraform and machine provisioning from scope, so that test and all
provisioning artifacts were deleted before Green.

## Green

### Iterations 1–3: Periods, Transformations, and Pipeline

Status: audit-hardened Green complete on 2026-07-24.

Command:

```text
python3 -m pytest -q \
  habitat-e2e-demo/migrated-pipeline-demo/implementation/tests/test_periods.py \
  habitat-e2e-demo/migrated-pipeline-demo/implementation/tests/test_transformations.py \
  habitat-e2e-demo/migrated-pipeline-demo/implementation/tests/test_pipeline.py
```

Initial Green result: 13 passed in 0.07 seconds.

A second Red added the six date-window values evidenced by the period KTR and
reported three expected missing-attribute/date failures. After Green, the
focused result was 14 passed.

Covered:

- `2026-07-15` resolves to periods `202606` and `202607`, with exact
  previous/current start and end dates.
- Calendar boundaries and invalid date handling.
- Exact base schemas and `YYYYMM01` `fechaCierre`.
- Literal-dot removal from DNI/RUT while preserving hyphens.
- Date compaction and `~|` output.
- Comma-first then `$` Motivo parsing, business-key/ordinal pairing, whitespace,
  duplicates, empty values, missing `$`, and explicit unequal-pair rejection.
- Eight output files and source job order.
- Processing failure notification/abort.
- Period failure abort without notification.

The independent audit requested additional schema/type, failure-matrix, and
byte-exact output tests.

Audit Red result: 14 failed and 20 passed. The failures captured the missing
strict-contract behavior.

Audit Green result: 34 passed in 0.10 seconds.

The hardened contract now also covers:

- Exact input header, order, and row-width checks.
- Pentaho integer, date, and `HH:mm:ss` parsing.
- Nullable date fields.
- All four processing failure notification paths.
- Period and validation failures aborting without notification.
- Unknown failure-stage rejection and notifier-error preservation.
- Zero-row, zero-byte headerless outputs.
- Byte-exact ISO-8859-1, `~|`, and LF-only output.
- CR, LF, and output-separator injection rejection.

Compileall and `git diff --check` passed for this slice.

### Iteration 4: Mock API, Wrapper, OCI Export, and Runtime Bundle

Status: Green. The full implementation suite passed 63 tests in 5.19 seconds.
Package compileall and wrapper `bash -n` also passed.

### Iteration 5: Import and Runtime Consistency Hardening

Status: Red confirmed on 2026-07-24.

Independent review found that first-class generated objects did not match the
supplied export envelope, processing request JSON referenced undeclared
period-window placeholders, and HTTP validation rejected valid zero-row
outputs. Tests were added before implementation changes.

Command:

```text
python3 -m pytest -q -p no:cacheprovider \
  tests/test_oci_export.py::test_export_documents_match_import_bundle_contract \
  tests/test_oci_export.py::test_processing_tasks_use_only_declared_request_parameters \
  tests/test_mock_api.py::test_validate_accepts_eight_zero_row_outputs
```

Result: expected Red, 3 failed in 0.12 seconds:

- missing top-level `metadata` on exported first-class objects;
- extra undeclared `${PREVIOUS_*}`/`${CURRENT_*}` request placeholders;
- `ValueError` for eight present zero-byte output files.

Green:

- First-class export objects now use the supplied sample's `metadata` envelope,
  `objectStatus=8`, and no top-level `parentRef`.
- REST parameters are derived from actual URL/body placeholders; processing
  bodies contain only `as_of_date` and `window`.
- Zero-row, headerless output is valid when all eight files exist.
- Notification branches connect bidirectionally to the single `END`, whose
  `ALL_SUCCESS` rule keeps processing failures failed after notification.
- The pipeline task binds runtime parameters and embeds the sample-shaped
  pipeline stub.
- `package-backend` creates the deterministic runtime tar and checksum.

Result: 67 passed in 5.57 seconds in the owner run; independent no-cache reruns
passed 67 tests in 4.95 and 5.33 seconds.

## Refactor

Status: complete.

Metadata construction, placeholder extraction, checksum writing, and archive
packaging are centralized. Tests and caches are excluded from the runtime
archive. Provisioning artifacts and their test were removed after the user
excluded Terraform and machine provisioning.

## Verification

Status: complete with one baseline dependency limitation.

| Command | Result |
| --- | --- |
| Migrated implementation no-cache suite | Passed: 67 tests in 5.33 seconds |
| `python3 -m compileall -q habitat-e2e-demo/migrated-pipeline-demo/implementation/habitat_sucursales` | Passed |
| `python -m compileall src` | Passed |
| `pytest -q` | Could not start: command is not installed in the shell |
| `python3 -m pytest -q -p no:cacheprovider` from repository root | Baseline collection blocked: `pyspark` is not installed |
| `mvn -q -DskipTests package` | Passed; emitted only a JDK `Unsafe` deprecation warning |
| `find platforms/oci/scripts -name "*.sh" -exec bash -n {} \;` | Passed |
| `bash -n implementation/start-mock-backend.sh` | Passed |
| `git diff --check` | Passed |
| OCI ZIP and backend tar integrity/checksums | Passed |
| Expected-output hashes, sizes, row counts, encoding, delimiter, and LF checks | Passed |
| New release/archive security scan | Passed; no OCIDs, private keys, secrets, or machine-local paths |

## Risks

- Offline schema checks cannot replace a live OCI import request.
- The original extractor shell scripts were not supplied, so their network
  calls are modeled from job arguments and fixture-backed behavior.
- Source evidence is already tracked in the task baseline and contains
  sensitive environment metadata. This task must not modify it or copy those
  values into new release files.
- The security test is scoped to the new migration release and runtime; it
  cannot truthfully assert that the pre-existing repository contains no
  environment values.

## Final Status

Complete. The complete mock-backed migration, expected output, deterministic
backend bundle, and OCI `.pipeline.zip` are generated. Offline structure and
integrity are verified. Live OCI import remains unproven because no tenancy is
available, and the supplied evidence does not expose the internal manifest
registry ID for `REST_TASK`; no unsupported value was invented.
