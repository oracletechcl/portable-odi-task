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

Draft PR: https://github.com/oracletechcl/portable-odi-task/pull/1

## Follow-up: language flavors and movable platforms

### Approved scope

- Retain the existing Python Data Flow application and add runnable Java, SQL, and Scala language samples.
- Keep Databricks as a supported movable platform.
- Add artifact-only deployment mappings for Amazon EMR, Microsoft Fabric, and Google Dataproc. No resources are created outside OCI.
- Build and validate the Java and Scala artifacts, upload all OCI language artifacts, create and directly run the three new OCI Data Flow applications, and record their OCIDs.

### Follow-up plan

1. Add minimal Java, Scala, and Spark SQL language samples with build configuration and tests or compile checks.
2. Add Amazon EMR, Microsoft Fabric, and Google Dataproc adapters while retaining the Databricks adapter.
3. Extend CI to validate Python, Java, Scala, SQL, and all portable platform mapping files.
4. Upload OCI artifacts and create/run Java, SQL, and Scala Data Flow applications in `us-sanjose-1`.
5. Update the neutral specification, portability matrix, inventory, TDD record, draft PR, and final validation evidence.

### Follow-up ownership

| Owner | Files or scope | State |
|---|---|---|
| Language owner | Java, Scala, SQL samples; build and test configuration | Pending Phase 3 |
| Platform owner | EMR, Fabric, Dataproc, Databricks portability artifacts | Pending Phase 3 |
| TDD auditor | Follow-up TDD and change-record evidence | Pending Phase 3 |
| Integration owner | OCI Data Flow provisioning, inventory, CI integration, final validation | Root |
