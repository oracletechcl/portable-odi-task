# Changes: execute OCI Data Integration CI/CD PoC

## Root Cause Analysis

The repository contains only the documented PoC and no executable portable code, CI workflow, or OCI deployment artifacts. Therefore none of the documented acceptance criteria can be executed or verified.

## How It Was Fixed

The portable transformation implementation now resides in `src/pyspark/customer_transform.py` and is covered by `tests/test_customer_transform.py`. The function performs the portable rules independent of OCI: it excludes inactive customers, normalizes the name, and calculates a tax-inclusive amount. OCI adapters, CI workflow, and OCI provisioning remain in progress.

## Summary

Tracking task opened. The portable transformation and validation jobs, test data, neutral specification, environment configuration, Databricks mapping, OCI Object Storage scripts, GitHub Actions workflow, and Bitbucket-compatible pipeline definition are present. OCI resource execution remains in progress.

## Validation

### Tracking gate evidence

- Confirmed branch: `feature/oci-data-integration-cicd-poc`.
- Confirmed tracking commits: `05b0097` and `bfb2cc1`.
- Confirmed draft PR recorded in `plan.md`: `https://github.com/oracletechcl/portable-odi-task/pull/1`.
- Source, tests, CI definitions, and OCI assets were not yet present at this audit point. No executable validation was possible.

### Audit update: test environment prerequisite

- `tests/test_customer_transform.py` was added after the initial audit.
- `python3 -m pytest -q` currently stops during collection with `ModuleNotFoundError: No module named 'pyspark'`.
- `requirements-dev.txt` declares `pyspark==4.1.1`, `pytest==9.0.2`, and `pyyaml==6.0.3`; dependency installation and a rerun are required before this can serve as the TDD Red/Green evidence.

### Audit update: portable transformation Green

- With `/private/tmp/portable-odi-venv`, `/private/tmp/portable-odi-venv/bin/python -m pytest -q` passed: `1 passed in 5.08s`.
- The local sandbox prevents Spark's Java gateway from binding a loopback port; the passing test ran outside that sandbox after explicit approval.
- `/private/tmp/portable-odi-venv/bin/python -m compileall -q src` passed with no output.

### Audit update: portable configuration checks

- `bash -n` passed for each shell script under `platforms/oci/scripts`.
- PyYAML parsed 7 YAML files: the GitHub Actions workflow, Bitbucket simulation, environment files, portable specification, and Databricks mapping.
- The full available local suite passed outside the network-restricted sandbox: `1 passed in 5.19s`.

### Audit update: CI and security review

- OCI credentials are referenced through CI secrets; no secret values or private-key contents are tracked in the reviewed artifacts.
- OCI scripts validate required environment variables and use `set -euo pipefail`; the generated key is restricted with `chmod 600`.
- Both CI definitions validate and upload only. They do not provision or run Data Flow/Data Integration resources, and deployment triggers only on `main`. Manual OCI provisioning/run evidence is required for the PoC acceptance criteria.

### Final cloud execution evidence

- Direct OCI Data Flow transformation: `SUCCEEDED`.
- Direct OCI Data Flow validation: `SUCCEEDED`.
- OCI Data Integration pipeline: published and exported successfully.
- OCI Data Integration end-to-end execution: `ERROR` because the workspace principal receives `NotAuthorizedOrNotFound` while creating a Data Flow run. The required IAM policy already exists by task assumption, but the effective workspace-principal authorization still needs correction; no IAM changes were made because they are out of scope.
- The default global Python environment fails before test collection because `pyspark` is absent. The declared isolated environment ran the full available suite successfully (`1 passed`).
- Controlled direct validation with `--minimum-records=100`: `FAILED` as expected with `RuntimeError`. This verifies the intended quality-gate failure behavior without relying on the blocked Data Integration pipeline path.
- Pipeline-level success and failure demonstrations remain blocked until the workspace principal is authorized to create Data Flow runs.

## Follow-up: language flavors and movable platforms

### Root Cause Analysis

The initial PoC demonstrated only Python in OCI Data Flow and only Databricks as a non-OCI mapping. It did not visibly cover every Data Flow language in the service UI or the requested target platforms.

### How It Was Fixed

Added runnable Java, Scala, and Spark SQL probe sources plus a Maven build that creates OCI Data Flow-ready Java and Scala JARs. Added artifact-only adapters for Amazon EMR, Microsoft Fabric, and Google Dataproc, and aligned the retained Databricks mapping with repository-source paths. OCI Data Flow applications and runs remain an integration-owner step, so no OCI claim is made here.

### Summary

The follow-up now provides one portable source flavor for each OCI Data Flow language option: Python (existing), Java, SQL, and Scala. Its supported movable-platform adapters are Databricks, Amazon EMR, Microsoft Fabric, and Google Dataproc.

### Validation

- Red: isolated `pytest` reported 3 expected failures before `pom.xml` and Java/Scala/SQL artifacts existed.
- Green: isolated `pytest` passed all 3 language-artifact tests.
- `mvn -q -DskipTests package` passed and produced the Java and Scala JARs (warnings only).
- EMR/Dataproc JSON and Fabric/Databricks YAML parsed successfully; `git diff --check` passed.
- Isolated full suite: `4 passed`; `python -m compileall src`, OCI shell syntax validation, and consolidated portable mapping YAML/JSON parsing all passed.
- Direct OCI Data Flow reruns succeeded: Java `RUN_JAVA_LANGUAGE_PROBE_RERUN` (`ocid1.dataflowrun.oc1.us-sanjose-1.anzwuljrfioir7iakicmlegqau4uq2e5gsqnlmm5z556grzngcw4hgsrgpzq`), Scala `RUN_SCALA_LANGUAGE_PROBE_RERUN` (`ocid1.dataflowrun.oc1.us-sanjose-1.anzwuljrfioir7ia5ajodklhlpj5zaf5mi2j7lf62vxqjwyy65dlmgsv2oza`), and SQL `RUN_SQL_LANGUAGE_PROBE_RERUN` (`ocid1.dataflowrun.oc1.us-sanjose-1.anzwuljrfioir7iawzienxwkltcros2lyq7bfcydnrjegjff6uxsmxgrfqeq`).
- The initial language runs supplied diagnostics, not final evidence: Java used a Java 17 JAR with no arguments; Scala had no arguments; and SQL parameters were undeclared. The successful reruns used Java 8, explicit Java/Scala arguments, and declared SQL parameters.
- Remaining: OCID inventory cross-check and the original blocked Data Integration pipeline execution. The workspace principal still cannot create Data Flow runs (`CreateRun` authorization).
