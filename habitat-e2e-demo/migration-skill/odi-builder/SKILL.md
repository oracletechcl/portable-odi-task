---
name: odi-builder
description: Migrate Pentaho Data Integration projects and individual Kettle KJB/KTR flows to OCI Data Integration end to end. Use when Codex must analyze Pentaho source and migration specifications, preserve transformations in testable code, create mock replacements for unavailable backends, generate a canonical importable OCI .project.zip, automate Compute VM mock deployment and OCI publication, run live validation, or troubleshoot OCI import, REST task, pipeline, and Application execution failures.
---

# ODI Builder

Build a complete, evidence-backed Pentaho-to-OCI Data Integration migration.
Treat this skill as self-contained. Do not require another workflow skill,
prompt, or external template to perform the migration.

## Operating contract

- Migrate one explicitly selected Pentaho flow at a time unless the user asks
  for a portfolio.
- Treat source KJB/KTR files and user specifications as read-only evidence.
- Preserve business transformations in testable Python, PySpark, SQL, YAML, or
  JSON. Do not leave business behavior only in visual OCI operators.
- Replace unavailable databases, scripts, extractors, filesystems, and
  notification services with deterministic mocks.
- Produce an importable `PROJECT-NAME.project.zip`, a runnable mock backend,
  expected outputs, tests, and an operator handoff.
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
5. Backend availability and mock boundaries.
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
- Run [scripts/validate_odi_project.py](scripts/validate_odi_project.py) against
  the unpacked project and final ZIP before import.
- Reuse [assets/migration-spec.template.md](assets/migration-spec.template.md),
  [assets/traceability.template.md](assets/traceability.template.md),
  [assets/deployment.env.example](assets/deployment.env.example), and
  [assets/operator-readme.template.md](assets/operator-readme.template.md).

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
4. Identify absent dependencies and define a mock boundary for each.
5. Write an evidence table linking each behavior to the spec or Pentaho file.

Gate: every target behavior and failure path must have source evidence or an
explicitly labeled assumption.

### 3. Specify

1. Write the migration specification from
   `assets/migration-spec.template.md`.
2. Define exact inputs, outputs, schemas, order, encoding, delimiters,
   success/failure semantics, mock routes, and packaging names.
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

1. Put transformation logic in importable, service-independent modules.
2. Use fixture-backed mocks for external boundaries.
3. Preserve job ordering and distinct failure semantics.
4. Make notification failure branches explicit.
5. Keep mock effects observable through output files or deterministic event
   logs.
6. Create expected outputs from the same fixed fixtures and date used by tests.

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

Gate: offline validation and checksum verification must pass before upload.

### 7. Deploy

1. Build one generic bash entrypoint with `set -euo pipefail`.
2. Require the Application name and run date; do not hide them behind defaults.
3. Load VM/workspace/bucket settings from an ignored local config.
4. Verify immutable checksums before transfer.
5. Install the mock release on the Compute VM, configure systemd, restrict the
   mock port to the workspace subnet, and pass `/health`.
6. Upload the project ZIP, import with conflict mode `REPLACE`, and poll to a
   terminal state.
7. Materialize the VM private URL and run date into the imported REST tasks
   using the OCI-native payload shape.

Gate: stop immediately and print service diagnostics on a failed import.

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
4. Scan tracked deliverables for secrets, OCIDs, keys, and real endpoints.
5. Confirm the live run succeeds without parameters.
6. Confirm the expected output count, names, contents, encoding, and hashes.
7. Update traceability so every criterion has evidence.

### 11. Handoff

1. Replace long-form operator notes with a short numbered README based on
   `assets/operator-readme.template.md`.
2. Show the one-stop command, what it does, where the task appears, how to
   click Run, and where outputs are written.
3. Report exact validation results and any environment-only limitation.
4. Link the importable ZIP, mock bundle, implementation, tests, expected
   outputs, and deployment script.

## Completion conditions

Do not declare the migration complete until:

- the source behavior and failure matrix are traceable;
- local mock-backed execution passes;
- the OCI project directory and ZIP validate;
- the deploy wrapper is generic and secret-free;
- live import/publication succeeds when access is available;
- the published root task is visible and a zero-parameter run succeeds;
- expected outputs are verified; and
- the operator can reproduce the demo from the README.

When live access is unavailable, complete the offline artifact and mock work,
mark live import/run as unverified, and provide the exact commands needed for
the eventual live gate.
