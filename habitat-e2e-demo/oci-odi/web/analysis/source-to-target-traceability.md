# Source-to-Target Traceability

| Requirement | Source | Target | Test | Status |
| --- | --- | --- | --- | --- |
| FR-PDI-001 | KJB start/success/failure hops | ordered pipeline; stop-on-failure | `test_web_pipeline.py` | Pass |
| FR-PDI-002 | Mesa Excel/TextFileOutput | `DATASET_CONTRACTS` + renderer | `test_web_transformations.py` | Pass |
| FR-PDI-003 | Usuario filename/session/date steps | `transform_configuracion_equipo_usuario` | `test_web_transformations.py` | Pass |
| FR-PDI-004 | OPC table/output | `DATASET_CONTRACTS["OPC_OPCION"]` | renderer and golden test | Pass |
| FR-PDI-005 | SEC table/output | `DATASET_CONTRACTS["SEC_SECCION"]` | byte-format test | Pass |
| FR-PDI-006 | SUB table/output | `DATASET_CONTRACTS["SUB_SUBSECCION"]` | missing-field test | Pass |
| FR-PDI-007 | log date/query/output | `DATASET_CONTRACTS["TB_LOG_SISTEMA"]` | renderer and golden test | Pass |
| FR-PDI-008 | subsystem/service table/output | `DATASET_CONTRACTS["TB_SUB_SISTEMA_SERVICIO"]` | renderer and golden test | Pass |
| OCI package | canonical export contract | deterministic exporter and ZIP | `test_oci_export.py` + validator | Pass offline |
| Existing mock | user evidence | configurable REST tasks | user waived validation | Unverified |
| Live OCI | unavailable authorization | deploy wrapper | dry-run only | Unverified |
