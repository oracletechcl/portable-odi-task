# TDD Log: Standalone ODI Builder Skill

## Red

Initial contract:

```text
python3 -m pytest -q -p no:cacheprovider \
  habitat-e2e-demo/migration-skill/tests/test_odi_builder_skill.py
```

Expected result: 5 failed. The skill package, routed knowledge, OCI caveats,
reusable scripts, and output templates did not exist.

The expanded functional contract then exposed:

- missing direct Markdown links to scripts/assets;
- a scaffolder bug that copied the approved spec before creating its parent;
- a validator implementation smell that inferred ZIP entries from a closure;
- Habitat-specific cardinality assertions that did not belong in a generic skill.

README diagram regression:

```text
python3 -m pytest -q \
  habitat-e2e-demo/migrated-pipeline-demo/implementation/tests/test_start_wrapper.py::test_readme_documents_the_entire_compute_vm_to_oci_demo
```

Expected result: failed because the separate-agent diagram documented
`GET /v1/periods`; the actual dispatcher exposes every business route through POST.

## Green

- Added the standalone skill, six references, three standard-library tools, four
  templates, and agent metadata.
- Added direct resource links and an explicit 11-phase end-to-end workflow.
- Fixed scaffolding parent creation and replaced the ZIP closure lookup with stored
  archive metadata.
- Corrected the README route to `POST /v1/periods`.
- Replaced the stale `${MOCK_BASE_URL}` security assertion with the proven
  `mock-backend.invalid` tracked-artifact contract.

Results:

```text
14 passed in 1.20s  # odi-builder contract
1 passed in 0.03s   # Mermaid README contract
70 passed in 5.29s  # complete migrated implementation suite
```

## Refactor

- Kept the reusable rules generic; source/spec manifests derive all object and
  output counts.
- Retained the ten-dependency/Page-2 and eight-output observations only as labeled
  case-study diagnostics.
- Redacted connection values, credentials, IPs, OCID-like values, e-mail-like
  values, and absolute referenced paths in Pentaho inventory output.
- Ensured the skill has no dependency on external workflow skills, absolute local
  paths, symlinks, embedded environment values, or non-standard-library scripts.

## Forward verification

`inspect_pentaho.py` ran read-only against the supplied source:

```text
documents 6; jobs 1; transformations 5; parse errors 0
job entries 9; steps 40; hops 49
```

`validate_odi_project.py` accepted both the known-good unpacked project and its
importable `.project.zip`. Synthetic negative tests reject missing explicit ZIP
directories, non-empty workspace identity, bad aggregator metadata, string
payloads instead of `JSON_TEXT`, and parameterized REST tasks.

The official `quick_validate.py` entry point passed using a temporary isolated
PyYAML install under `/private/tmp`; no validator dependency was added to the
repository or system Python.
