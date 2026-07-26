# TDD Evidence

## Red

The new layout contract failed because `habitat-e2e-demo/mocks/airflow` did not
exist: 1 failed, 2 passed.

## Green

- Airflow asset and layout tests: 12 passed.
- Repository excluding the unrelated Web OCI exporter test file: 120 passed.
- The old `habitat-e2e-demo/airflow` root is absent.
- All Airflow scripts remain executable and pass shell syntax checks.

The complete repository run reached 122 passed and 2 unrelated failures in
`oci-odi/web/implementation/tests/test_web_oci_export.py`. Those tests exercise
Web OCI object selection/envelopes and do not reference Airflow or this move.

## Refactor

The Sucursales-specific wrapper directory and unused Web placeholder were
removed. The shared server now owns one flat config, scripts, systemd, docs,
tests, and README structure.
