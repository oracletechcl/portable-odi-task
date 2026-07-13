# Plan: execute OCI Data Integration CI/CD PoC

## Scope and decisions

- Execute the complete portable PySpark proof of concept in OCI region `us-sanjose-1`.
- Use the assigned Data Integration workspace and compartment.
- Treat existing IAM as a prerequisite. Document the least-privilege policy forms; do not create, change, or delete IAM policies.
- Use the GitHub repository as the Bitbucket simulation: retain the Bitbucket-compatible pipeline contract and provide an equivalent GitHub Actions workflow for executable CI.
- Record all newly created OCI assets and OCIDs in `docs/documented-poc.md`. Do not commit credentials or local paths.

## Approved implementation plan

1. Create portable PySpark transformation and output-validation code, fixture data, a neutral pipeline specification, and an independent unit test.
2. Add OCI adapter scripts, environment templates, artifact handling, and a Databricks job mapping without placing business logic in OCI-specific artifacts.
3. Add GitHub Actions CI equivalent to the documented Bitbucket pipeline and preserve a Bitbucket-format reference pipeline.
4. Use OCI CLI to provision the Object Storage bucket, upload the source and test data, create and run the Data Flow applications, and verify their output.
5. Use OCI CLI payloads generated from the installed CLI schema to create the Data Integration project, tasks, pipeline, pipeline task/application, successful execution, controlled validation failure, and exported ZIP/hash.
6. Run targeted and full validation. Document OCI results and asset OCIDs in `docs/documented-poc.md`.
7. Commit, push, and move the draft pull request to ready for review after all validation passes.

## Tests and validation

- `tests/test_customer_transform.py::test_transform_filters_and_calculates_tax`
- `python -m compileall src`
- `pytest -q`
- `find platforms/oci/scripts -name '*.sh' -exec bash -n {} \;`
- GitHub Actions workflow syntax review
- OCI Object Storage listing, Data Flow run status, Data Integration task-run status, exported ZIP checksum

## Agent roster and file ownership

To be assigned after the tracking pull request exists and before implementation begins.

| Owner | Files or scope | State |
|---|---|---|
| Integration owner | `src/`, `tests/`, `specification/`, `environments/`, `platforms/`, `.github/`, OCI provisioning | Pending |
| TDD auditor | `docs/fixes/feature/oci-data-integration-cicd-poc/execute-poc/` review and independent validation | Pending |

## Tracking PR

Pending creation.
