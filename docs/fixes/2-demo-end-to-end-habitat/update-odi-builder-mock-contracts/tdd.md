# TDD Evidence

## Red

- Mock lifecycle contract: 6 failed, 11 passed.
- App-local one-stop contract: 4 failed, 16 passed.
- Web runnable artifact/reproducible release contract: 3 failed, 1 passed.
- Root deploy scaffold and dry-run contract: expected failures before assets and
  generation logic existed.

## Green

- Focused ODI builder and Web deployment suite: 23 passed.
- Mock validator: `READY` with Compute VM and release gates.
- OCI project validator: `VALID`.
- Skill package validator: valid.
- Repository suite: 110 passed.

## Refactor

- Kept the operator entry point at app-root `deploy.sh`.
- Kept OCI-specific execution under the app’s `platforms/oci` implementation.
- Removed the obsolete mock-only Web deploy script.
- Normalized the Web REST payload and pipeline topology to the proven Sucursales
  OCI object shapes.
