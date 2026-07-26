# Apache Airflow 3.3.0 Sources

These deployment decisions use the official Apache Airflow 3.3.0 documentation.

- [Prerequisites](https://airflow.apache.org/docs/apache-airflow/3.3.0/installation/prerequisites.html):
  Airflow 3.3.0 supports Python 3.10 through 3.14; SQLite is for local/test use.
- [Installation from PyPI](https://airflow.apache.org/docs/apache-airflow/3.3.0/installation/installing-from-pypi.html):
  install the exact Airflow version with the matching Python constraints file.
- [Quick Start](https://airflow.apache.org/docs/apache-airflow/3.3.0/start.html):
  `airflow standalone` initializes the database, creates a user, and starts the
  components required for local development/testing.
- [SimpleAuthManager](https://airflow.apache.org/docs/apache-airflow/3.3.0/core-concepts/auth-manager/simple/):
  configure `username:role`; generated passwords are stored in the configured
  JSON password file. This auth manager is for development/testing.
- [Configuration reference](https://airflow.apache.org/docs/apache-airflow/3.3.0/configurations-ref.html):
  `[api] host/port`, the absolute DAG folder, generated password path, and the
  execution API URL are environment-configurable.
- [Health checks](https://airflow.apache.org/docs/apache-airflow/3.3.0/administration-and-deployment/logging-monitoring/check-health.html):
  query `/api/v2/monitor/health` and inspect component status, not HTTP status
  alone.
- [DAG bundles](https://airflow.apache.org/docs/apache-airflow/3.3.0/administration-and-deployment/dag-bundles.html):
  the local DAG bundle reads source files from the configured DAG directory.
- [Airflow 3 migration guidance](https://airflow.apache.org/docs/apache-airflow/3.3.0/installation/upgrading_to_airflow3.html):
  DAG authors should use Airflow 3 public interfaces such as `airflow.sdk`.

## Test-server choices

- Python 3.11 matches the supplied VM and has a published Airflow 3.3.0
  constraints file.
- SQLite, SimpleAuthManager, and `airflow standalone` are intentionally TEST
  only.
- The existing Habitat mock owns port 8080. Airflow binds only to
  `127.0.0.1:8081`.
- The execution API URL is set explicitly because its fallback is
  `http://localhost:8080/execution/`, which would collide with the mock.
- The UI is reached through an SSH tunnel, so no public firewall rule is added.
