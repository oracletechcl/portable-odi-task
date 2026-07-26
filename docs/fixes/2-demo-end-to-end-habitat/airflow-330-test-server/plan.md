# Plan: Airflow 3.3.0 Test Server

## Goal

Install a vanilla Apache Airflow 3.3.0 test server on the same OCI Compute VM as
the Habitat mock backend. Keep Airflow isolated from the mock's port, generate
SimpleAuthManager credentials on the VM, and provide a safe filesystem-based DAG
deployment path.

## Decisions

- Use official PyPI installation with the Airflow 3.3.0/Python 3.11 constraints.
- Use an application virtual environment under `/opt/airflow`.
- Use `airflow standalone`, SQLite, and SimpleAuthManager only for TEST.
- Bind the API/UI to `127.0.0.1:8081`; operators connect through an SSH tunnel.
- Keep the existing mock on port 8080 unchanged.
- Store generated passwords under `AIRFLOW_HOME` with mode `0600`.
- Deploy DAG source over SSH/SCP into the configured DAG directory.
- Do not commit VM addresses, SSH keys, passwords, OCIDs, or other environment
  values.

## Plan

- [x] Research official Airflow 3.3.0 installation, auth, config, and health docs.
- [x] Write failing asset, security, dry-run, and operator-contract tests.
- [x] Implement the one-stop deploy, remote installer, systemd unit, credential
  helper, DAG deployer, and README.
- [x] Run offline tests, syntax checks, secret scans, and documentation checks.
- [x] Deploy to the supplied VM and verify version, service, health, credentials,
  and coexistence with the existing mock.

## Agent roster

| Agent | Assignment | Files |
| --- | --- | --- |
| Root | Tests, implementation, VM deployment, verification | All implementation files |
| `airflow_330_docs` | Official documentation research | None |
| `airflow_server_tests` | Read-only TDD/security contract | None |
