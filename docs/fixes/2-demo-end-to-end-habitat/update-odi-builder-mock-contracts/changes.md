# Changes

- Added mandatory per-boundary mock decisions: `yes` or `no` with evidence.
- Added existing-mock audit and missing-mock creation gates.
- Added `validate_mock_backend.py` with `MISSING`, `READY`, and `NOT_REQUIRED`.
- Added mock and app-root deploy templates to the ODI builder scaffold.
- Required every migration to expose only `./deploy.sh` to the operator.
- Added the Web app one-stop Compute VM + OCI import/publish deployer.
- Added port-collision protection so unrelated VM mocks are not stopped.
- Added the Web mock contract, systemd template, concise runbook, and dry-run.
- Rebuilt the importable Web project ZIP with a runnable mock-backed pipeline.
- Made both project ZIP and mock release deterministic and checksummed.
