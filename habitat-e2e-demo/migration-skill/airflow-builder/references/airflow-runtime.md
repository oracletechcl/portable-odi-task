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

Before deploying, inspect the target host as the Airflow service user. Record an
absolute executable `AIRFLOW_BIN`, `AIRFLOW_HOME`, and the `dags_folder` reported
by `airflow config get-value core dags_folder`; require configured and active
folders to match. Service accounts commonly have no usable login `PATH`, so
invoke the absolute binary with a deterministic `PATH`. Use `sudo -n` so missing
authorization fails clearly, and poll for the exact DAG ID after the atomic move
because the DAG processor indexes files asynchronously.
Validate the DAG folder as the Airflow service user, not the SSH login user:
restricted Airflow home permissions are expected on hardened hosts.
Airflow CLI commands can emit plugin or warning lines alongside `--output json`.
The deployer must isolate and parse the JSON payload before testing for import
errors or an exact DAG ID; `[]` is a valid clean import-error response.
An `external-reuse` mock must not be health-probed by deployment. Its URL is a
runtime-topology decision, not a presumed source port. For a user-authorized
connection-refused diagnosis, compare the Airflow Variable with the service
listener; correct both the ignored config and the Variable when they disagree.
Public UI endpoint and username are optional ignored-config handoff fields. Verify
that an advertised public port actually serves Airflow before publishing its URL.
Never derive or store a UI password in tracked artifacts. Print a password from
ignored configuration only for an explicitly user-authorized demo handoff guarded
by `AIRFLOW_PRINT_UI_PASSWORD=yes`; otherwise state only that it is configured.

Keep the instance OCID, public IP, SSH user, key-file reference, Airflow home,
binary, DAG folder, and DAG ID in ignored configuration. Templates and skill
instructions must be parameterized and must never contain target values or key
material.
