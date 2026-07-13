# TDD log: execute OCI Data Integration CI/CD PoC

## Feature need

Create a portable PySpark integration proof of concept that OCI Data Flow executes and OCI Data Integration orchestrates. GitHub simulates Bitbucket CI/CD.

## Red

`tests/test_customer_transform.py` now defines the required behavior: filter inactive customers, trim and uppercase names, and calculate a tax-inclusive amount.

Observed command: `python3 -m pytest -q`

Observed result: collection failed before the behavior assertion because the local interpreter lacks `pyspark` (`ModuleNotFoundError: No module named 'pyspark'`). This establishes an environment prerequisite only; it does **not** yet prove the intended Red failure against the missing `src.pyspark.customer_transform` implementation. Install the declared development requirements and rerun before Green.

## Green

`src/pyspark/customer_transform.py` now supplies `transform_customers`. Independent verification used the isolated PySpark environment:

```text
/private/tmp/portable-odi-venv/bin/python -m pytest -q
1 passed in 5.08s
```

The sandbox blocks the PySpark JVM loopback gateway (`SocketException: Operation not permitted`), so the passing test was rerun with the required unsandboxed permission. `python3 -m compileall -q src` completed after the passing test with no output and exit status 0.

## Refactor

The implementation keeps transformation and validation rules in portable PySpark modules. OCI-specific concerns are limited to upload/configuration shell scripts and CI workflow definitions; the neutral pipeline specification and Databricks mapping preserve the same logical workload outside OCI.

## Validation

### Independent audit

- Targeted suite passed: 1 test.
- Source compilation passed: `src/`.
- Shell syntax passed: all `platforms/oci/scripts/*.sh` via `bash -n`.
- YAML parsing passed: 7 configuration/workflow files (`bitbucket-pipelines.yml`, GitHub Actions workflow, environment files, portable specification, and Databricks mapping).
- Full local suite passed with required loopback permission: `1 passed in 5.19s`.
- OCI Data Flow, OCI Data Integration, Object Storage, and export checks remain pending.

### CI/security review

- No credentials, OCIDs beyond user-supplied identifiers, or private-key contents were found in the portable source or workflow files.
- OCI credentials are consumed from CI secrets and the generated private-key file is permissioned `0600`.
- GitHub Actions and the Bitbucket-simulation pipeline validate and upload artifacts only. They do not create or execute Data Flow/Data Integration resources. The push deployment trigger is restricted to `main`; pull requests validate only. OCI execution must therefore remain the separately documented manual PoC action.

### Final cloud execution evidence

- The direct OCI Data Flow transformation run succeeded.
- The direct OCI Data Flow validation run succeeded.
- The OCI Data Integration pipeline was published and exported.
- Its end-to-end Data Integration run ended in `ERROR`: the workspace principal cannot create the Data Flow run (`NotAuthorizedOrNotFound`). This is an IAM/workspace-principal prerequisite failure, not a portable transformation or validation failure. IAM policy changes were explicitly out of scope.
- The default global Python environment cannot run the suite because it lacks `pyspark`. The declared isolated environment (`/private/tmp/portable-odi-venv`) ran the complete available suite successfully: `1 passed`.
- Controlled direct validation run with `--minimum-records=100`: `FAILED` as expected with `RuntimeError`, demonstrating the quality gate's failure behavior.
- Pipeline-level success and controlled-failure execution remain blocked by the workspace principal's Data Flow `CreateRun` authorization failure.

### Tracking gate evidence

- Branch verified: `feature/oci-data-integration-cicd-poc`.
- Tracking commits verified: `05b0097` and `bfb2cc1`.
- Draft PR recorded in `plan.md`: `https://github.com/oracletechcl/portable-odi-task/pull/1`.
- No implementation artifacts or tests existed at this audit point; the Red step remains pending.

Pending.
