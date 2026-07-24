# Sucursales Migration Traceability

| ID | Requirement | Planned implementation | Planned test/validation | Status |
| --- | --- | --- | --- | --- |
| AC-01 | Preserve complete job topology | `pipeline.py`, OCI pipeline object | `test_pipeline.py`, `test_oci_export.py` | Passed: 67-test migrated suite |
| AC-02 | Calculate period windows | `periods.py` | `test_periods.py` | Passed: calendar and boundary tests |
| AC-03 | Preserve base transformations | `contracts.py`, `transformations.py` | `test_transformations.py` | Passed: strict schema and byte contracts |
| AC-04 | Preserve motivo expansion | `transformations.py` | `test_transformations.py` | Passed: pairing and malformed-input tests |
| AC-05 | Provide all mock endpoints | `mock_api.py` | `test_mock_api.py` | Passed: API and media/error contracts |
| AC-06 | Use one bash startup point | `start-mock-backend.sh` | `test_start_wrapper.py`, `bash -n` | Passed: lifecycle, arbitrary-CWD, and shell checks |
| AC-07 | Preserve period-abort and processing notification/abort behavior | `pipeline.py`, `mock_api.py`, OCI failure nodes | `test_pipeline.py`, `test_mock_api.py`, `test_oci_export.py` | Passed: local and OCI graph failure paths |
| AC-08 | Produce deterministic expected output | `pipeline.py`, fixtures, target output | `test_pipeline.py`, manifest hash/row verification | Passed: eight CSVs plus canonical manifest |
| AC-09 | Package `HABITAT_SUCURSALES.project.zip` with a `USER_PROJECT` export root | `oci_export.py`, generated OCI objects | `test_oci_export.py`, ZIP integrity and manifest-root checks | Passed offline canonical-project structural and integrity checks |
| AC-10 | Package a machine-ready mock backend | deterministic runtime archive | `test_start_wrapper.py`, archive-content checks | Passed: runtime-only tar and checksum |
| AC-11 | Exclude secrets and promote one artifact | `.gitignore`, parameterized config, checksums | `test_security.py`, checksum verification | Passed on new release and both archives |
| AC-12 | Pass completion gates | All task files | Compile, pytest, Maven, shell commands | Completed; root pytest blocked by missing baseline `pyspark`, recorded in TDD |

## Evidence Policy

- Canonical behavior comes from the approved migration specification.
- Missing details may be resolved from the original Pentaho files.
- The customer portability pipeline supplies export-layout conventions only.
- Source environment values are not valid target configuration.
- Every final `Passed` status must cite an executed command or focused test.
