# TDD Evidence

## Red

Command: `cd implementation && python3 -m pytest -q`

Result: collection failed for three modules because `habitat_web` did not exist.
This proved the tests preceded implementation.

## Green

Added source-derived contracts, transformations, ordered pipeline, HTTP client,
CLI, and deterministic OCI exporter.

Result after golden-output and deployment contract slices: `18 passed`.

## Refactor

- Centralized field order and formatting in immutable dataset contracts.
- Injected time into Usuario transformation for deterministic tests.
- Kept endpoint and timeout explicit.
- Used UUIDv5, sorted compact JSON, fixed ZIP timestamps, and explicit directory entries.

## Remaining environment gates

- Existing mock route/health checks were waived by user instruction.
- OCI import, materialization, publication, and zero-parameter run require authorized config.
