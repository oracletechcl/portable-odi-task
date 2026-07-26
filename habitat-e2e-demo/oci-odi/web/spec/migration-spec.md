# Habitat Web OCI Data Integration Migration Specification

## Inputs and evidence

- Approved SDD spec: `sot/Pentaho_Habitat_Web-llm-assets/migration-spec/Web/spec.md`
- Primary behavior: `app-by-app-analysis/Web/deep-dive.md` B7/B9
- Pentaho XML: one KJB and seven KTR files under `source-code/Web`
- OCI shape reference: `sot/canonical-project.project`
- Target: OCI Data Integration

## Acceptance criteria

1. Preserve FR-PDI-001 through FR-PDI-008 and source field order.
2. Produce seven `.csv` files using `~|`, ISO-8859-1, LF, and no header.
3. Preserve zero-row files and fail on malformed or incomplete rows.
4. Recover Usuario period month from `bi_[A-Z]{5}_DD-MM-YYYY.txt`.
5. Prefer session time 1; use session time 2 only when time 1 is empty.
6. Stop after the first failed external stage; do not record false success.
7. Keep the boundary URL outside tracked artifacts.
8. Deliver a deterministic, parameter-free OCI project ZIP and checksum.
9. Require `--config` and `--app-name` at the root deployment entry point.
10. Mark mock and live OCI checks unverified where user-authorized validation is absent.

## Packaging

- Project: `HABITAT_WEB.project.zip`
- Root task: `TASK_RUN_HABITAT_WEB`
- Release: `1.0.0`
- Immutable artifact promotion: use the same ZIP checksum for TEST and PROD.

