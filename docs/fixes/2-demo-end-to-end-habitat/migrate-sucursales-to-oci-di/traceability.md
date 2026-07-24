# Sucursales Migration Traceability

| ID | Requirement | Planned implementation | Planned test/validation | Status |
| --- | --- | --- | --- | --- |
| AC-01 | Preserve complete job topology | `pipeline.py`, OCI pipeline object | `test_pipeline.py`, `test_oci_export.py` | Planned |
| AC-02 | Calculate period windows | `periods.py` | `test_periods.py` | Planned |
| AC-03 | Preserve base transformations | `contracts.py`, `transformations.py` | `test_transformations.py` | Planned |
| AC-04 | Preserve motivo expansion | `transformations.py` | `test_transformations.py` | Planned |
| AC-05 | Provide all mock endpoints | `mock_api.py` | `test_mock_api.py` | Planned |
| AC-06 | Use one bash startup point | `start-mock-backend.sh`, cloud-init | `test_start_wrapper.py`, `bash -n` | Planned |
| AC-07 | Preserve notification/abort behavior | `pipeline.py`, `mock_api.py`, OCI failure nodes | `test_pipeline.py`, `test_mock_api.py` | Planned |
| AC-08 | Produce deterministic expected output | `pipeline.py`, fixtures, target output | `test_pipeline.py` | Planned |
| AC-09 | Package an import-oriented `.pipeline.zip` | `oci_export.py`, generated OCI objects | `test_oci_export.py`, ZIP integrity check | Planned |
| AC-10 | Deploy mock service to private Compute | `platforms/oci/habitat-sucursales-mock/` | `test_compute_contract.py`, Terraform validation | Planned |
| AC-11 | Exclude secrets and promote one artifact | `.gitignore`, parameterized config, checksums | `test_security.py`, checksum verification | Planned |
| AC-12 | Pass completion gates | All task files | Compile, pytest, Maven, shell, Terraform commands | Planned |

## Evidence Policy

- Canonical behavior comes from the approved migration specification.
- Missing details may be resolved from the original Pentaho files.
- The customer portability pipeline supplies export-layout conventions only.
- Source environment values are not valid target configuration.
- Every final `Passed` status must cite an executed command or focused test.

