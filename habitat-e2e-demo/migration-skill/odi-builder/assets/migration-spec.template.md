# {{PROJECT_NAME}} Migration Specification

## Scope

- Pentaho source root:
- Canonical OCI project sample:
- Target project name:
- Target project identifier:
- Target pipeline name:
- Target pipeline identifier:
- Runnable pipeline-task name:
- Runnable pipeline-task identifier:
- Release version:

## Source behavior

| Stage | Source artifact | Inputs | Transformation | Outputs | Success | Failure |
| --- | --- | --- | --- | --- | --- | --- |

## Data contracts

For every input and output, specify exact field names, types, order, null handling,
encoding, delimiter, quoting, line endings, filename pattern, and cardinality.

## Calendar and run-input rules

Document time zone, as-of date, current and previous periods, month/year edges,
empty-input behavior, and repeat-run behavior.

## External boundaries

| Boundary | Available? | Target integration | Mock fixture/route | Deployment binding |
| --- | --- | --- | --- | --- |

## Mock decision

| Boundary | Availability/access evidence | `mock-required` | Mock exists | Action (`reuse`, `create`, `not-required`) | Validation |
| --- | --- | --- | --- | --- | --- |

## Target topology

Describe the OCI pipeline order, success links, failure branches, notification task
per failure branch, and zero-parameter runnable task.

## Expected outputs

| Relative path | Schema | Rows/rule | Byte contract | Source evidence |
| --- | --- | --- | --- | --- |

## Acceptance criteria

- [ ] Every source stage and branch is traceable.
- [ ] Pure transformations pass without OCI.
- [ ] Mock routes pass integration tests.
- [ ] Deterministic project ZIP validates and imports.
- [ ] Runnable task publishes and runs with zero parameters.
- [ ] Output file set and golden manifest match.
- [ ] Every external boundary has an explicit `mock-required` decision.
- [ ] Every required mock exists or was created and validates as `READY`.
- [ ] Every non-required boundary validates as `NOT_REQUIRED`.
- [ ] No secrets, OCIDs, real endpoints, IPs, or private keys are tracked.

## Gaps and approved assumptions

| Gap | Evidence searched | Safe mock assumption | Approval/status |
| --- | --- | --- | --- |
