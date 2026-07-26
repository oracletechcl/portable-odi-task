# HABITAT_SUCURSALES_VIA_SKILL Mock Contract

## Decision

- `mock-required`: yes
- Evidence reviewed: source KJB/KTR boundaries, migration specification,
  accessible environments, and operator authorization.
- Decision rule: require a mock when a dependency is unavailable, inaccessible,
  unsafe to call, non-deterministic, or unsuitable for repeatable tests.

## Existing-mock audit

| Boundary | Mock required | Mock exists | Evidence inspected | Action |
| --- | --- | --- | --- | --- |
| Legacy database, shell-download, file and mail boundaries | yes | user-supplied port-8000 service | User instruction | external-reuse; no deploy probe |

Use `reuse` only when the existing mock satisfies this entire contract. Use
`create` for every missing or incomplete required mock. Use `not-required` only
when the decision evidence supports direct access.

## Boundary contracts

| Source step | Method/path | Request | Success response | Error response | Side effect | Fixture |
| --- | --- | --- | --- | --- | --- | --- |

## Required runnable assets

- deterministic runtime implementation and pure transformation modules;
- small synthetic fixtures with no customer data;
- `implementation/start-mock-backend.sh` with `set -euo pipefail`;
- side-effect-free `GET /health`;
- integration tests for every route, failure, and unknown route;
- operator README with start, health, deploy, run, and verification steps;
- Compute VM deployment and systemd assets when requested; and
- immutable mock release archive plus SHA-256 when packaging is requested.

## Validation evidence

Record the `validate_mock_backend.py` command, `READY` or `NOT_REQUIRED`
result, local integration result, release checksum result, and live Compute VM
health result when applicable.

The service is intentionally not recreated, packaged, or probed here. Deployment
only materializes its approved host into the tracked `.invalid` REST URL.
