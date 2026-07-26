# Changes

- Moved the shared Airflow 3.3.0 test server to `habitat-e2e-demo/mocks/airflow`.
- Flattened `config`, `docs`, `scripts`, `systemd`, and `tests` under that root.
- Updated all operator commands to the new location.
- Removed the obsolete `airflow/sucursales` and `airflow/web` split.
- Preserved loopback-only Airflow, runtime-generated credentials, and existing
  Habitat mock protection.
