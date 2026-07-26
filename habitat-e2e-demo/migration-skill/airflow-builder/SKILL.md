---
name: airflow-builder
description: Migrate Pentaho Data Integration KJB/KTR flows to deployable Apache Airflow DAG runtimes. Use when Codex must discover Pentaho behavior, preserve transformations in testable Python/SQL, generate DAGs, decide/audit/create mocks, package a runnable Airflow migration, deploy it to the supplied Airflow server, or troubleshoot DAG import, scheduling, task, or mock failures.
---

# Airflow Builder

Build an evidence-backed Pentaho-to-Airflow migration. Migrate one selected flow
at a time unless the user requests a portfolio. Keep source KJB/KTR and approved
specifications read-only. Preserve business transformations in importable Python,
PySpark, SQL, YAML, or JSON—not solely in DAG callables.

## Required evidence

Resolve source root, selected flow, approved spec, output root, Airflow server
access, and every external boundary. Read `references/pentaho-discovery.md` and
`references/airflow-runtime.md` before implementation. Record source anchors,
schemas, dates, file contracts, enabled hops, success/failure branches, and gaps.
Run `scripts/scaffold_airflow_migration.py --output-root OUTPUT --spec SPEC` to
create the required app-local deployer, config example, DAG, implementation,
test, evidence, and expected-output layout.

## Mock ownership

Classify each boundary as `managed`, `external-reuse`, or `not-required`.

- `managed`: audit it, create deterministic fixtures/routes/tests/`GET /health`
  if missing, then package and deploy it safely.
- `external-reuse`: materialize only its approved URL. Never create, package,
  start, stop, probe, SSH into, or otherwise mutate it from the migration
  deployer. Validate it through the Airflow task run or a user-authorized host.
- `not-required`: document availability, authorization, safety, stability, and
  repeatability evidence.

Never substitute a static-success server for missing behavior. Use a deterministic
mock only when source behavior is recoverable. The same method/path contract must
appear in the Python client, DAG task, deployment materialization, and mock route.

## SDD and TDD workflow

1. Discover with the Pentaho inventory; write behavior contract, gap register,
   mock contract, source-to-target traceability, and target design.
2. Write failing tests for each slice: dates, schemas/order, transformations,
   empty/malformed/duplicate input, byte-format output, branch failure, retries,
   notification, and idempotency.
3. Implement pure transformation modules, then thin Airflow tasks that call them
   or the approved boundary. DAG tasks orchestrate; they do not own business logic.
4. Generate a DAG with an explicit `dag_id`, no parse-time network/filesystem
   effects, no secrets/endpoints, deterministic task IDs, trigger rules matching
   Pentaho success/failure hops, and a testable failure-notification branch.
5. Create exact golden outputs and a manifest; run twice from clean output roots.

## Deployment contract

Every migration contains executable `deploy.sh` and
`platforms/airflow/scripts/deploy-internal.sh`. The root script is the only
operator entry point and accepts `--config PATH --app-name NAME [--dry-run]`.
The internal engine must:

1. validate explicit config, DAG syntax, Airflow import, checksums, DAG ID, and
   immutable release files before mutation;
2. create or verify Airflow runtime dependencies on the supplied host only when
   the user authorizes runtime installation; otherwise verify the supplied server;
3. deploy the DAG atomically into the configured DAG folder, verify remote
   checksum, wait for Airflow to report no import error, and leave the DAG ready
   to run (unpaused unless the user explicitly requests paused);
4. create/deploy managed mocks only; for `external-reuse`, materialize the URL
   without a health probe or lifecycle action; and
5. print `READY` only after the DAG is visible, import-clean, and ready to run.

Do not leave a scaffold wrapper whose internal deployer is absent. Run `bash -n`
on both scripts and execute root `--dry-run` before handoff. Keep all config local,
ignored, explicit, and secret-free in tracked examples.

## Airflow gates

Run `scripts/validate_airflow_dag.py DAG.py --dag-id DAG_ID`, compile modules,
unit/integration tests, and Airflow DAG import checks. Require a DAG listing and
zero import errors from the target server after deployment. Do not claim execution
success until a task run reaches a terminal successful state and matches golden
outputs, when the user authorizes running it.

## Incremental defect hardening

For every fix, update this skill or a directly referenced contract, add a
deterministic validator/template guardrail when structural, add a regression test,
and record the failure signature and prevention rule in TDD evidence. Never use an
untested nested JSON/shell payload; build it in importable code and unit test it.

## Handoff

Provide README steps for config, dry run, deployment, Airflow UI path, DAG ID,
manual Run action, logs, outputs, and mock ownership. Include a Mermaid diagram.
Link source traceability, implementation, tests, expected outputs, deployer, and
the immutable release checksum.
