# Migration Workflow

This workflow combines specification-driven development and test-driven development
without relying on another skill.

## Required working evidence

Create these files under the migration output root before implementation:

```text
analysis/behavior-contract.md
analysis/gap-register.md
spec/target-design.md
tests/
docs/tdd-evidence.md
```

## Deployment ownership

Every migrated application must contain its own executable one-stop deployment
engine under `platforms/oci/scripts/`. Its top-level `deploy.sh` may delegate
only to a script inside the same migration root. Do not piggyback on another
application's deployment script, release archive, configuration file, or
systemd unit.

The engine must accept `--config PATH` and `--app-name NAME`, use
`set -euo pipefail`, validate all files and checksums before mutation, and make
the mock lifecycle explicit. Manage and health-check only a migration-managed
mock; for a user-supplied external mock, materialize the endpoint without a
probe or lifecycle action.

The scaffold wrapper is not an implementation. In the same migration pass,
create executable `platforms/oci/scripts/deploy-internal.sh`; it must validate
the explicit config and immutable project checksum, upload/import with
replacement, materialize REST tasks, create or reuse the exact application,
publish the root task, and verify publication. Before handoff run `bash -n` on
both scripts and `./deploy.sh --config CONFIG --app-name NAME --dry-run`.

## Fresh-build rule

Implement the selected migration from its own Pentaho XML, approved
specification, and canonical OCI export only. Another migration may be consulted
as non-authoritative background, but its runtime code, fixtures, tests, release
archives, expected outputs, and deployment files must never be copied or relabeled
into the new output root. Record all source evidence and derive every target
artifact independently.

The target design must trace every Pentaho stage and branch to either pure business
logic, an OCI orchestration object, a mock boundary, or an explicitly deferred gap.

Record a mock decision for every external boundary. A `yes` decision requires an
existing-mock audit and creation of every missing or incomplete mock before
packaging. A `no` decision requires evidence that the real boundary is available,
authorized, safe, stable, and repeatable.

## Specification-driven sequence

1. Read the complete approved specification.
2. Run Pentaho discovery and reconcile XML evidence with the specification.
3. Freeze schemas, field order, date rules, file contracts, success semantics,
   failure semantics, and external boundaries.
4. Define OCI project, pipeline, runnable task, REST task, mock, and deployment
   contracts.
5. Record assumptions and obtain approval for any assumption that changes business
   behavior.

Do not put business transformations exclusively in OCI visual operators. Keep them
in Python, PySpark, SQL, YAML, or JSON so they run without OCI.

## Test-driven sequence

For each behavior:

1. **Red:** write the smallest failing test and record why it fails.
2. **Green:** implement the smallest behavior that makes it pass.
3. **Refactor:** simplify while the suite remains green.

Cover at least:

- period and calendar edge cases;
- each filter, mapping, join, derivation, and row-width rule;
- exact source and target schemas, types, and field order;
- encoding, delimiter, quoting, LF newlines, and byte-exact golden outputs;
- zero rows, malformed values, injection-like input, and duplicate input;
- ordered orchestration and every failure/notification branch;
- mock method, path, JSON body, response, error, and unknown-route contracts;
- the explicit mock decision, existing-mock audit, missing-mock creation, and final
  `READY` or `NOT_REQUIRED` status;
- deterministic project ZIP and mock archive packaging;
- required deployment arguments, dry-run behavior, shell syntax, and the app-root
  `deploy.sh` operator entry point;
- secret, real-endpoint, OCID, IP, and private-key scans;
- import, publish, zero-parameter run, and expected-output verification.

Record unrelated repository baseline failures separately. Do not hide them and do
not misclassify them as migration regressions.

## Golden outputs

Generate a manifest containing, for every expected file:

- relative path;
- SHA-256;
- byte size;
- row count;
- encoding, delimiter, and newline contract;
- run inputs and resolved periods.

Valid zero-byte outputs remain part of the expected file set. Build the result twice
from clean directories and byte-compare both the files and manifest.

## Completion gates

Run repository-specific checks plus:

```bash
python3 -m compileall implementation
python3 -m pytest -q
find platforms/oci/scripts -name "*.sh" -exec bash -n {} \;
python3 scripts/validate_odi_project.py target/PROJECT-NAME.project.zip
unzip -t target/PROJECT-NAME.project.zip
tar -tzf target/mock-release.tar.gz
```

Offline tests are necessary but insufficient when live OCI access is in scope. A
complete live proof includes import, inventory, publication, task run, and output
comparison. Ask before making live changes when the user has not authorized them.
