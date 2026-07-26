# TDD Log: Airflow 3.3.0 Test Server

## Red

The first focused run failed because the requested Airflow directory and all
runtime assets were absent. The contract required:

- a pinned official Airflow 3.3.0/Python 3.11 installation;
- a hardened test-only standalone systemd service;
- loopback port isolation from the existing port-8080 mock;
- generated mode-0600 SimpleAuthManager credentials;
- one-stop deployment with a mutation-free dry-run;
- a credential retrieval helper and DAG deployment helper;
- no committed environment values or secrets; and
- concise operator instructions and official source links.

## Green

Implemented the runtime assets and reran:

```text
.........                                                                [100%]
9 passed in 0.10s
```

The tests cover the exact Airflow/Python constraint, loopback-only networking,
explicit arguments with no defaults, generated credentials, mock protection,
systemd hardening, shell syntax, offline dry-run behavior, DAG deployment, and
the operator runbook.

## Live verification

Deployed on 2026-07-25. Read-only post-deployment checks confirmed:

- Airflow 3.3.0 and `airflow-standalone.service` are active;
- metadata database, scheduler, DAG processor, and triggerer are healthy;
- the SQLite metadata database check passes;
- the generated credential file contains the requested admin user and is mode
  `0600`;
- Airflow listens only on `127.0.0.1:8081`;
- the existing mock remains active and healthy on port 8080; and
- the installer observed the same mock PID and unit checksum before and after
  installation.
