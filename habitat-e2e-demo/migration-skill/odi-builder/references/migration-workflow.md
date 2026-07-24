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

The target design must trace every Pentaho stage and branch to either pure business
logic, an OCI orchestration object, a mock boundary, or an explicitly deferred gap.

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
- deterministic project ZIP and mock archive packaging;
- required deployment arguments, dry-run behavior, and shell syntax;
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
