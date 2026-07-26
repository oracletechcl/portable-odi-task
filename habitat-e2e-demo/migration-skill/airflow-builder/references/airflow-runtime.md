# Airflow runtime and deployment

Use the user-supplied Airflow server when available. Its DAG source is installed
on the host filesystem, not uploaded through the UI. Require an explicit config
with SSH host/user/key, DAG folder, Airflow command path, DAG ID, and release
paths. Never track these values or credentials.

For a supplied same-host mock, keep ownership separate. An `external-reuse` mock
is not part of deployment: do not probe it from the deployer. A managed mock must
have deterministic fixtures, route/failure tests, strict start wrapper, health
contract, immutable archive, and idempotent service deployment.

Deploy atomically: syntax-check locally, checksum, copy to a temporary remote
path, checksum remotely, install as the Airflow service user, run
`airflow dags list-import-errors`, verify the exact DAG ID is listed, and use the
Airflow CLI/API to unpause only when scope permits. A UI page is not evidence.
