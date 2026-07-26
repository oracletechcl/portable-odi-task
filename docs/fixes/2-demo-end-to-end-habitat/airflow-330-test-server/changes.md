# Changes: Airflow 3.3.0 Test Server

## Delivered

- A generic one-stop local deployment wrapper with required VM, key, port, and
  admin-user arguments.
- A remote Airflow 3.3.0/Python 3.11 constrained installer.
- A test-only, loopback-bound `airflow standalone` systemd service.
- Idempotent SimpleAuthManager credential generation that preserves existing
  passwords and adds a requested user only when missing.
- A credential retrieval helper and an atomic DAG source deployment helper.
- A concise end-to-end operator README and version-locked official sources.
- Hard pre/post guards for the existing Habitat mock service, health endpoint,
  process, systemd unit, and port.

## Validation

- Focused Airflow asset tests: `9 passed`.
- Existing repository plus Airflow tests, excluding a concurrently added
  untracked web demo: `97 passed`.
- All new shell scripts: `bash -n` passed.
- Existing OCI shell scripts: `bash -n` passed.
- `python3 -m compileall -q src`: passed.
- `mvn -q -DskipTests package`: passed with only JDK deprecation warnings.
- Runtime secret and dangerous-operation scan: no matches.
- Live Airflow health: all required components healthy.
- Live mock health: active and healthy; port 8080 unchanged.

Plain workspace-wide `pytest -q` was blocked at validation time by the then
untracked Web migration: it duplicated the top-level
`test_pipeline` module name and its own test fails because Python's CSV writer
does not accept the two-character `~|` delimiter. Those files were not changed
as part of the Airflow work.
