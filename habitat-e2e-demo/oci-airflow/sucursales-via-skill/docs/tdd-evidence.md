# TDD evidence

- `test_period_rollover_and_rut_cleanup`: current/prior period boundary and RUT
  normalization pass.
- `test_motivo_pairing`: paired motivo/submotivo expansion passes.
- DAG source compiles and `validate_airflow_dag.py` validates
  `habitat_sucursales_carga_archivo_externo`.
- Root deployment `--dry-run` validates config and the immutable DAG checksum
  without contacting or changing the external mock.

Live Airflow DAG import and run remain pending operator-authorized deployment.

Regression: test modules use an Airflow-Sucursales-specific basename to avoid
pytest collection collisions with other migrations' `test_transformations.py`.
