# Changes: Refurbish Demo Layout

## Delivered

- The Airflow 3.3.0 server was initially grouped by migration and is now
  centralized as a shared mock under `mocks/airflow`.
- Replaced the generic OCI ODI roots with `oci-odi/sucursales` and
  `oci-odi/web`.
- Preserved both completed OCI project ZIPs, mock archives, expected outputs,
  implementations, tests, and documentation.
- Updated active README commands, the Sucursales one-stop deploy script, Web
  environment guidance, and target-artifact ignore exceptions.
- Added a directory contract and a Web test import bootstrap.
- Preserved the ignored Sucursales deployment environment at its new path.

## Validation

- Directory contract: `3 passed`.
- Airflow Sucursales: `9 passed`.
- OCI ODI Sucursales: `70 passed`.
- OCI ODI Web: `1 passed`.
- Full repository: `101 passed`.
- Both OCI project ZIP and mock archive checksums: passed.
- `python3 -m compileall -q src`: passed.
- `mvn -q -DskipTests package`: passed with only JDK deprecation warnings.
- All relevant shell scripts: `bash -n` passed.
- Active retired-path and whitespace scans: passed.
