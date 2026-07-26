# Shared Apache Airflow 3.3.0 Test Server

This shared mock service installs vanilla Airflow 3.3.0 on the same Compute VM
as the Habitat Sucursales mock.
It is **TEST only**: SQLite, SimpleAuthManager, and `airflow standalone` are not
a production topology.

The mock stays on port 8080. Airflow listens only on `127.0.0.1:8081`, reached
through an SSH tunnel. No public Airflow port is opened.

## 1. Deploy

From the repository root:

```bash
./habitat-e2e-demo/mocks/airflow/scripts/deploy-airflow-server.sh \
  --vm-public-ip <vm-public-ip> \
  --ssh-user <ssh-user> \
  --ssh-key <ssh-private-key> \
  --airflow-port 8081 \
  --admin-user airflowadmin
```

The one-stop script:

1. validates the VM, key, port, username, and local assets;
2. checksums and uploads the installer, environment template, and systemd unit;
3. creates the `airflow` service account and writable state directories;
4. installs Airflow 3.3.0 in `/opt/airflow/venv` using Python 3.11 constraints;
5. configures loopback-only Airflow and the local execution API URL;
6. starts `airflow-standalone.service`;
7. verifies Airflow health and confirms the mock unit, PID, and `/health`
   response did not change; and
8. leaves the generated credential file mode `0600`.

## 2. Read the generated credentials

```bash
./habitat-e2e-demo/mocks/airflow/scripts/show-airflow-credentials.sh \
  --vm-public-ip <vm-public-ip> \
  --ssh-user <ssh-user> \
  --ssh-key <ssh-private-key>
```

The username was supplied through `--admin-user`. The password is generated on
the VM in:

```text
/var/lib/airflow/simple_auth_manager_passwords.json.generated
```

Do not copy that file into the repository.

## 3. Open the SSH tunnel

```bash
ssh -N \
  -L 8081:127.0.0.1:8081 \
  -i <ssh-private-key> \
  <ssh-user>@<vm-public-ip>
```

Open <http://127.0.0.1:8081> and log in with the generated credentials.

Check the API through the same tunnel:

```bash
curl --fail http://127.0.0.1:8081/api/v2/monitor/health
```

## 4. Deploy a DAG

Airflow does not upload DAG source through the UI. Copy each DAG into the local
DAG bundle:

```bash
./habitat-e2e-demo/mocks/airflow/scripts/deploy-dag.sh \
  --vm-public-ip <vm-public-ip> \
  --ssh-user <ssh-user> \
  --ssh-key <ssh-private-key> \
  --dag-file path/to/my_dag.py
```

The helper syntax-checks the Python file, verifies its remote checksum, installs
it under `/var/lib/airflow/dags`, and reports DAG import errors. New DAGs are
paused by default; review and unpause them in the UI.

## Service checks

On the VM:

```bash
sudo systemctl status airflow-standalone.service --no-pager
sudo journalctl -u airflow-standalone.service -n 100 --no-pager
sudo -u airflow /opt/airflow/venv/bin/airflow version
sudo -u airflow /opt/airflow/venv/bin/airflow dags list-import-errors
```

Rerun the deploy command to repair or verify the same installation. It does not
stop or reconfigure `habitat-sucursales-mock.service`.
