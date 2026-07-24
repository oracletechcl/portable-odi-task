# Changes: Standalone ODI Builder Skill

## Need

The working Habitat migration accumulated reusable knowledge across Pentaho source
analysis, mock design, OCI project packaging, Compute deployment, import,
publication, UI pagination, zero-parameter execution, and output validation. That
knowledge needed one isolated, reusable migration skill.

## Delivered

- `odi-builder/SKILL.md`: complete Intake-to-Handoff SDD/TDD workflow.
- `references/`: focused discovery, workflow, project, mock, live OCI, and
  troubleshooting contracts.
- `scripts/inspect_pentaho.py`: deterministic, secret-safe KJB/KTR inventory.
- `scripts/scaffold_migration.py`: no-default workspace scaffolder with dry-run.
- `scripts/validate_odi_project.py`: directory/ZIP envelope, manifest, registry,
  parameter, REST payload, endpoint, and secret validation.
- `assets/`: migration spec, traceability, blank deployment config, and concise
  operator README templates.
- `agents/openai.yaml`: isolated `$odi-builder` invocation metadata.
- `migration-skill/tests/`: structural, isolation, stdlib, functional, security,
  dry-run, and negative OCI fixture coverage.
- Migrated demo README: Mermaid architecture showing deployment, OCI objects,
  success integrations, four notification branches, private-VCN mock, pure
  transformations, validation, and outputs.

## Key OCI caveats preserved

- Canonical `PROJECT-NAME.project.zip` envelope with explicit root/`Objects/`
  directory entries.
- Sole `USER_PROJECT` export root, first-class `objectStatus: 8`, child aggregator
  metadata, and empty exported workspace identity.
- Parameter-free pipeline/REST/runnable tasks.
- `JSON_TEXT` request payload and inert `.invalid` tracked endpoints.
- One notification task per processing failure branch.
- Post-import private URL/date materialization, import `REPLACE`, manual
  application polling, terminal `get-patch` failure handling, and `--all`
  pagination.
- Console Page-2/filter guidance and zero-parameter run.
- Immutable checksummed artifacts, private VCN mock access, and no Terraform.

## Validation

- `odi-builder`: 14 tests passed.
- Migrated implementation: 70 tests passed.
- Full repository with pinned dependencies isolated under `/private/tmp`: 88 tests
  passed.
- Pentaho forward discovery: 6 documents, no parse failures.
- Known-good OCI project directory and ZIP: valid.
- Official skill validator, Python compile, Maven package, OCI shell syntax,
  artifact checksums/integrity, nested-archive secret scan, and diff checks passed.
