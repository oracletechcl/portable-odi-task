---
name: odi-builder
description: Migrate Pentaho Data Integration projects and individual Kettle KJB/KTR flows to OCI Data Integration end to end. Use when Codex must analyze Pentaho source and migration specifications, preserve transformations in testable code, decide whether mocks are required, audit or create runnable mocks for unavailable backends, generate a canonical importable OCI .project.zip, automate Compute VM mock deployment and OCI publication, run live validation, or troubleshoot OCI import, REST task, pipeline, and Application execution failures.
---

# ODI Builder

Build a complete, evidence-backed Pentaho-to-OCI Data Integration migration.
Treat this skill as self-contained. Do not require another workflow skill,
prompt, or external template to perform the migration.

## Operating contract

### Incremental defect hardening

For every incremental fix to migration behavior, packaging, deployment, or live
OCI execution, update the skill in the same change set before closing the fix.
Add a durable workflow/reference guardrail, a deterministic validator or template
rule when the condition is structural, and a regression test. Record the failing
evidence and prevention rule in the migration TDD log. A one-off application-only
fix is incomplete.

Never construct nested OCI payload JSON as an untested shell heredoc or one-line
expression. Put deployment payload builders in importable Python modules, unit-test
their exact OCI envelope, and invoke those modules from the shell deployer.

- Migrate one explicitly selected Pentaho flow at a time unless the user asks
  for a portfolio.
- Treat source KJB/KTR files and user specifications as read-only evidence.
- Preserve business transformations in testable Python, PySpark, SQL, YAML, or
  JSON. Do not leave business behavior only in visual OCI operators.
- Decide whether each external boundary requires a mock from source evidence,
  access, safety, and repeatability. Never assume either answer.
- Audit every migration-managed required mock before implementation. Reuse it only when its
  routes, fixtures, tests, start wrapper, health contract, release, deployment,
  and runbook satisfy the complete contract.
- Create every missing or incomplete required mock and validate it before OCI
  packaging or live publication.
- Produce an importable `PROJECT-NAME.project.zip`, a runnable mock backend,
  expected outputs, tests, and an operator handoff.
- Keep the `--config`/`--app-name` one-stop deployment engine self-contained in
  the migration output root; it must not delegate to another application's
  scripts or configuration.
- Treat `deploy.sh` as a wrapper only. Before handoff, create the executable
  `platforms/oci/scripts/deploy-internal.sh` and implement the selected
  migration's complete dependency sequence: checksum gate, Object Storage
  upload, import polling, endpoint materialization, exact Application
  create/reuse, publish polling, and published-root verification. Do not leave a
  scaffold placeholder or a wrapper whose target is absent.
- Build every migration from the selected Pentaho source, approved specification,
  and canonical OCI export. Do not copy, rsync, vendor, or relabel another
  application's runtime, fixtures, tests, archives, expected outputs, or OCI
  project as the implementation of a new migration.
- Make live OCI and SSH operations only when the user supplies or authorizes
  the relevant workspace, bucket, VM, keys, and region.
- Never store credentials, private keys, OCIDs, passwords, or real environment
  endpoints in tracked files.
- Do not generate Terraform or other infrastructure provisioning unless the
  user explicitly adds it to scope.

## Required inputs

Resolve these from the request and local evidence before asking questions:

1. Pentaho source directory or selected `.kjb`/`.ktr` files.
2. Migration specification, if present.
3. Canonical OCI project export used as the structural reference.
4. Output root and required project/release name.
5. Backend availability, explicit mock-required decisions, and evidence for
   any existing mock.
6. Live OCI workspace, bucket, region, VM, SSH user, and key only when live
   deployment is in scope.

Ask only for missing choices that would materially change the migration.

## Resource routing

Read each required reference completely when entering its phase:

- Read [references/pentaho-discovery.md](references/pentaho-discovery.md) for
  KJB/KTR inventory, behavior extraction, and evidence precedence.
- Read [references/migration-workflow.md](references/migration-workflow.md) for
  the specification, test-first implementation, output, and handoff contract.
- Read [references/oci-project-contract.md](references/oci-project-contract.md)
  before generating or changing OCI import artifacts.
- Read [references/mock-deployment.md](references/mock-deployment.md) when any
  backend is mocked or a Compute VM deployment is requested.
- Read [references/live-oci-operations.md](references/live-oci-operations.md)
  before calling OCI CLI or publishing an Application.
- Read
  [references/validation-troubleshooting.md](references/validation-troubleshooting.md)
  before final verification or when import, publication, or execution fails.

Use the bundled tools:

- Run [scripts/inspect_pentaho.py](scripts/inspect_pentaho.py) to create a
  deterministic source inventory.
- Run [scripts/scaffold_migration.py](scripts/scaffold_migration.py) to create a
  clean migration workspace.
- Run
  [scripts/validate_mock_backend.py](scripts/validate_mock_backend.py) with an
  explicit `--required yes|no` decision before implementation and again after
  creating, packaging, or deploying a required mock.
- Run [scripts/validate_odi_project.py](scripts/validate_odi_project.py) against
  the unpacked project and final ZIP before import.
- Reuse [assets/migration-spec.template.md](assets/migration-spec.template.md),
  [assets/mock-contract.template.md](assets/mock-contract.template.md),
  [assets/traceability.template.md](assets/traceability.template.md),
  [assets/deployment.env.example](assets/deployment.env.example), and
  [assets/deploy.template.sh](assets/deploy.template.sh), and
  [assets/operator-readme.template.md](assets/operator-readme.template.md).

## Mandatory mock lifecycle

When the user supplies an externally managed mock, record it as `external-reuse`.
Do not create, package, deploy, start, stop, health-probe, or otherwise mutate it
from the migration deployment engine. Materialize its approved endpoint only.
Validate its routes through the OCI task run or a user-authorized environment;
an agent sandbox's inability to reach it is not a deployment failure.
Never static contract parity: verify from the packaged artifact that the REST
task method and path, deployment-materialized endpoint path, and service launch
port contract agree before live deployment. This is an artifact/configuration
check only for `external-reuse`; it must not contact the service.

Apply this gate to every external database, API, file source, script,
filesystem, extractor, validator, and notification boundary:

1. **Decide:** Decide whether each external boundary requires a mock. Record
   `yes` or `no` plus evidence in `analysis/mock-contract.md`. Require a mock
   when the dependency is unavailable, inaccessible, unsafe, non-deterministic,
   or unsuitable for repeatable tests.
2. **Audit:** Validate whether every required mock already exists by running
   `scripts/validate_mock_backend.py`. Inspect behavior, not merely filenames.
   A complete mock includes deterministic runtime code, synthetic fixtures,
   route and failure tests, `GET /health`, one strict start wrapper, operator
   documentation, and any requested Compute VM and release assets.
3. **Create:** Create every missing or incomplete required mock from the
   recovered source contract. Do not substitute an empty server, static success
   response, or placeholder for missing behavior.
4. **Revalidate:** Rerun the validator until it returns `READY`, or
   `NOT_REQUIRED` for an evidence-backed `no` decision. Then run the mock-backed
   flow locally. When Compute VM deployment is in scope, also verify systemd,
   VCN reachability, firewall scope, and live health.

Gate: do not package, publish, or declare the migration runnable while a
required mock is `MISSING`.

Hard guardrail: a user may waive live network probes, but never static contract
parity. Before packaging, compare every generated REST task method and path with
the mock's registered route table and fail on any missing or extra required
route. Also require the deployment `MOCK_BASE_URL` port, service launch port, and
workspace-scoped firewall port to match. Record a probe waiver separately; do not
convert it into permission to skip these deterministic checks.

## End-to-end workflow

### 1. Intake

1. Confirm the single flow, source/spec/canonical paths, output root, mock
   boundaries, and whether live OCI deployment is required.
2. Record explicit in-scope and out-of-scope items.
3. Keep source-of-truth inputs unchanged.
4. Create a migration workspace with `scripts/scaffold_migration.py` when the
   requested output structure does not already exist.

Gate: do not design the target until the flow and evidence roots are known.

### 2. Discover

1. Run `scripts/inspect_pentaho.py` over the source root.
2. Read every selected KJB/KTR file, not only the top-level job.
3. Reconstruct steps, enabled hops, success/failure branches, variables,
   queries, scripts, schemas, field conversions, encodings, delimiters, file
   naming, date formats, and notification behavior.
4. Inventory every external boundary, record availability and authorization,
   and make the explicit mock decision for each.
5. Write an evidence table linking each behavior to the spec or Pentaho file.

Gate: every target behavior and failure path must have source evidence or an
explicitly labeled assumption.

### 3. Specify

1. Write the migration specification from
   `assets/migration-spec.template.md`.
2. Define exact inputs, outputs, schemas, order, encoding, delimiters,
   success/failure semantics, mock decision evidence, mock routes, and
   packaging names.
3. Write the traceability matrix from
   `assets/traceability.template.md`.
4. Split the work into independently testable slices.
5. Obtain user direction only for unresolved material choices.

Gate: each acceptance criterion must have a planned test.

### 4. Test

Use Red → Green → Refactor for every slice:

1. Red: write a failing test for the exact source behavior or artifact
   contract.
2. Green: implement only enough to satisfy it.
3. Refactor: simplify while keeping the test Green.
4. Record commands and outcomes in the migration TDD log.

Test at minimum:

- period/date boundaries and malformed input;
- exact field order, types, nullability, and transformations;
- byte-exact outputs, encoding, delimiter, line endings, and zero-row cases;
- each success and failure branch;
- every mock route and the single start wrapper;
- deterministic backend and OCI archives;
- OCI object graph, manifest, ZIP layout, and secret scans.

### 5. Implement

1. Run `scripts/validate_mock_backend.py` with the recorded decision.
2. If it reports `MISSING`, create or complete the required mock before
   continuing.
3. Put transformation logic in importable, service-independent modules.
4. Use fixture-backed mocks only for boundaries marked `mock-required: yes`.
5. Preserve job ordering and distinct failure semantics.
6. Make notification failure branches explicit.
7. Keep mock effects observable through output files or deterministic event
   logs.
8. Create expected outputs from the same fixed fixtures and date used by tests.
9. Rerun the mock validator and the complete local flow.

Gate: the complete flow must run locally without OCI services.

### 6. Package

1. Build the canonical OCI project described in
   `references/oci-project-contract.md`.
2. Prefer parameter-free REST, pipeline, and pipeline-task objects for a
   mock-backed demo; materialize environment values during deployment.
3. Create a separate notification task per failure branch when the body must
   contain a different failed-step value.
4. Generate a deterministic `.project` directory, `.project.zip`, and checksum.
5. Package the mock backend with fixtures, implementation, wrapper, and
   checksum; exclude tests, caches, secrets, and runtime output.
6. Run `scripts/validate_odi_project.py` on both the directory and ZIP.

   Require `USER_PROJECT` as the first `manifest.objects` entry and exact
   `MODEL_TYPE_IDENTIFIER_KEY.json` object filenames. These are OCI import gates,
   not cosmetic conventions.

Hard gate: offline validation and checksum verification must pass before upload.
Never upload a pipeline containing flat `TASK_OPERATOR` nodes. Every pipeline node
must be a canonical `FLOW_NODE` wrapping a START, TASK, or END operator, with
reciprocal `INPUT_LINK.fromLink` and `OUTPUT_LINK.toLinks` references. REST tasks
and pipeline-task stubs must also pass the complete canonical-envelope checks in
the validator. Do not weaken or bypass these checks to make an archive pass.

### 7. Deploy

1. Build one generic bash entrypoint with `set -euo pipefail` at the migrated
   application root as `deploy.sh`, inside the migrated application.
   Platform-specific helpers may remain under `platforms/oci`, but operators
   invoke only the root script.
   Apply this layout to every migration; never require the operator to enter a
   platform directory or invoke a nested helper.
2. Make it the single operator entry point for Compute mock installation, OCI
   project import, Application creation, and task publication.
   The internal deployer must exist before this phase is considered complete;
   make it executable and test `./deploy.sh --config CONFIG --app-name NAME
   --dry-run` successfully. For `external-reuse`, omit every mock lifecycle and
   health action, including `curl`; only materialize its URL in imported tasks.
3. Require `--config`, `--app-name`, and every migration-specific run input. Use
   no environment defaults.
4. Load VM/workspace/bucket settings only from the explicitly supplied ignored
   local config.
5. Verify immutable checksums before transfer.
6. For migration-managed mocks only, install the mock release on the Compute VM,
   configure systemd, restrict the mock port to the workspace subnet, and pass
   `/health`. For `external-reuse`, materialize the endpoint without probing it.
7. Upload the project ZIP, import with conflict mode `REPLACE`, and poll to a
   terminal state.
8. Materialize the VM private URL and run inputs into the imported REST tasks
   using the OCI-native payload shape.

Gate: stop immediately and print service diagnostics on a failed import. Print
`READY` only after the project import is successful and the runnable root task is
published; the runnable root task is published and verified before handoff. For a
migration-managed mock, `READY` additionally
requires that the mock is healthy; an externally reused mock is validated only by
the later task run.

### 8. Publish

1. Create or reuse the user-supplied Application.
2. Locate the imported pipeline task by identifier.
3. Publish the pipeline task and its dependencies through a patch.
4. Poll `get-patch`; fail immediately on `FAILED`.
5. Verify the root pipeline task with `list-published-objects --all`.

Gate: a successful patch alone is insufficient; the root published task must
be present.

### 9. Run

1. Open the Application task, enter no runtime parameters, and run it.
2. If the Console shows ten REST tasks on Page 1, use Page 2 or the name filter
   to locate the pipeline task.
3. For CLI smoke tests, create the task run under the published task registry
   owner and poll it to `SUCCESS`, `ERROR`, or `TERMINATED`.
4. Capture execution errors and child task identifiers on failure.

### 10. Verify

1. Run focused and full tests.
2. Compile supported source packages and syntax-check every shell script.
3. Verify artifact checksums and deterministic regeneration.
4. Require `validate_mock_backend.py` to report `READY` or `NOT_REQUIRED`.
5. Scan tracked deliverables for secrets, OCIDs, keys, and real endpoints.
6. Confirm the live run succeeds without parameters.
7. Confirm the expected output count, names, contents, encoding, and hashes.
8. Update traceability so every criterion has evidence.

### 11. Handoff

1. Replace long-form operator notes with a short numbered README based on
   `assets/operator-readme.template.md`.
2. Show the one-stop command, what it does, where the task appears, how to
   click Run, and where outputs are written.
3. Include a Mermaid "How the POC works" diagram showing the operator,
   deployment wrapper, OCI project/Application/task, mock service, health
   check, routes, and expected outputs.
4. State whether a mock was required, whether it existed, what was created or
   reused, how it starts, and how its health and route contracts were verified.
5. Report exact validation results and any environment-only limitation.
6. Link the importable ZIP, mock bundle, implementation, tests, expected
   outputs, and deployment script.

## Completion conditions

Do not declare the migration complete until:

- the source behavior and failure matrix are traceable;
- every external boundary has an evidence-backed mock decision;
- each required mock exists and the validator reports `READY`;
- each non-required mock decision reports `NOT_REQUIRED`;
- local mock-backed execution passes;
- the OCI project directory and ZIP validate;
- every pipeline uses canonical `FLOW_NODE` wrappers and reciprocal links;
- the deploy wrapper is app-local, generic, secret-free, and uses no environment
  defaults;
- `platforms/oci/scripts/deploy-internal.sh` exists, is executable, and the root
  `deploy.sh --dry-run` reaches it successfully;
- live import/publication succeeds when access is available;
- the published root task is visible and a zero-parameter run succeeds;
- expected outputs are verified; and
- the operator can reproduce the demo from the README.

A scaffold, inventory, specification template, or deployment configuration alone
is never a migration result. SDD execution must continue past Intake/Discover and
Specify into Test, Implement, Package, Deploy, Publish, Run, Verify, and Handoff.
For every selected flow, the migration output must contain source-derived:

- pure, executable transformation/orchestration code;
- deterministic synthetic fixtures and golden outputs;
- Red/Green/Refactor test evidence for each contract slice;
- a canonical, OCI-importable project ZIP and checksum;
- a self-contained `--config`/`--app-name` deployment engine; and
- live import, published-task, and zero-parameter run evidence when access is
  supplied.

After any failure, add its signature, corrected invariant, and regression command
to the skill and migration TDD evidence before retrying.

If any of these are missing, report the phase as incomplete and continue work;
do not hand off a scaffold as a migration.

When live access is unavailable, complete the offline artifact and mock work,
mark live import/run as unverified, and provide the exact commands needed for
the eventual live gate.
