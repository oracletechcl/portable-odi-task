# Mock Deployment

Build one deterministic mock service for unavailable backend boundaries. It must be
useful for OCI integration proof while remaining safe to run without production
systems.

## Decision gate

## Externally managed mock

If the user states that a mock is already supplied outside the migration or
agent sandbox, classify it as `external-reuse`. The deployment script must only
materialize its approved URL. It must not run `/health`, install a service,
transfer an archive, alter firewall rules, or otherwise manage that mock.
Route validation belongs to the OCI task run or a user-authorized environment.
Static method/path parity is mandatory: the OCI REST task, deployment URL
materialization, and documented route must all be identical; all three must be
identical. For a managed mock,
the service launch port, deployment port, and firewall port must all be identical.

Decide separately for every external boundary.

| Evidence | `mock-required` |
| --- | --- |
| Backend is unavailable, inaccessible, unauthorized, unsafe, or nondeterministic | `yes` |
| Backend is available, authorized, safe, stable, and repeatable for the proof | `no` |
| Access evidence is incomplete and the migration must run without the dependency | `yes`, with the assumption recorded |

Record the decision and evidence in `analysis/mock-contract.md`. Never infer
`not-required` merely because no mock directory exists.

## Existing-mock audit

When `mock-required` is `yes`, validate the migration root before creating
anything:

```bash
python3 scripts/validate_mock_backend.py \
  --migration-root MIGRATION_ROOT \
  --required yes \
  --compute-vm \
  --release
```

Audit behavioral completeness, not only filenames:

- every required method, route, request schema, response schema, success response,
  and error response;
- deterministic synthetic fixture data;
- side-effect-free `GET /health`;
- route and failure tests;
- a foreground `start-mock-backend.sh` using `set -euo pipefail`;
- operator instructions for start, health, logs, and expected output;
- Compute VM service assets and immutable release checksums when those targets are
  in scope.

Static method/path parity is mandatory even when the operator explicitly waives
live health or route probes. Derive the expected set from the generated OCI REST
tasks and compare it with the mock handler's registered route table. Fail if the
sets differ. Separately compare the deployment URL port, systemd launch port, and
workspace-scoped firewall port; all three must be identical.

`NOT_REQUIRED` is valid only after an explicit `mock-required: no` decision.

## Missing-mock creation contract

If the audit returns `MISSING`, create or complete the mock inside the migrated
application. Include pure transformation modules, synthetic fixtures, HTTP routes,
deterministic failures, route tests, the start wrapper, an immutable archive and
SHA-256, Compute VM deployment assets, and the operator runbook. Re-run the audit
until it returns `READY`; do not package or deploy while it returns `MISSING`.

## Service contract

Provide:

- `GET /health`, with no business side effects;
- one POST route per unavailable extraction, processing, validation, or
  notification boundary;
- JSON-object request validation and `application/json` enforcement;
- deterministic success and error JSON;
- `404` for unknown routes;
- fixture-backed results and a complete mock notification record;
- pure transformation functions importable and testable without the HTTP server.

Keep fixtures small, deterministic, and free of real customer data.

## Single start point

Provide one operator command:

```bash
./start-mock-backend.sh
```

The wrapper uses `set -euo pipefail`, accepts required configuration explicitly,
checks Python and fixtures, prepares writable output state, and starts the service
in the foreground. It must not embed an IP, port, user, key, date, or endpoint
default when the deployment contract requires that value from the operator.

For a Compute one-stop deployer managing its own mock, preserve the named mock
lifecycle safely. This section never applies to `external-reuse`:

1. If the named systemd service is active, install the immutable release and
   restart that service.
2. If it is inactive and the configured port is free, install and start it.
3. If it is inactive but another process owns the port, fail without killing the
   process; report the listener and require operator direction.
4. Do not manually kill a healthy mock process outside the service manager.
5. Poll local and VM-private `/health` to success before beginning OCI upload or
   import; a failed health gate must stop the script.

The one-stop engine, service template, runtime archive contract, and deployment
configuration example belong to the migrated application's own
`platforms/oci/` tree. Reuse behavior only through versioned code or artifacts
copied into that application; never invoke another app's deploy script.

## Immutable release

Package the runtime as a deterministic tar archive and checksum. A Compute install
should:

1. verify the checksum locally and remotely;
2. install into `/opt/<service>/releases/<release-hash>`;
3. atomically repoint `/opt/<service>/current`;
4. keep output under `/var/lib/<service>/output`;
5. run as a non-root service user when available;
6. restart on failure;
7. apply `NoNewPrivileges`, `ProtectHome`, `PrivateTmp`, and `UMask=0027`;
8. poll localhost `/health` before proceeding.

Python 3.11 is a conservative Compute runtime target unless the supplied machine
contract says otherwise.

## Network placement

Place the Compute VM and OCI Data Integration workspace on reachable VCN paths.

- Bind the mock to `0.0.0.0`.
- Use the VM public IP only for SSH/SCP administration.
- Materialize the VM private IP into OCI REST tasks.
- Resolve the workspace subnet CIDR through OCI metadata.
- Allow the mock TCP port only from that CIDR, never from the public internet.
- Use host-key pinning outside disposable demos. `accept-new` is only an explicitly
  documented demo compromise.

Terraform is outside scope unless the user asks for infrastructure provisioning.
The workflow configures a supplied machine; it does not create one.

## App-local one-stop contract

Every migrated application contains its own operator entry point:

```bash
./deploy.sh \
  --config PATH \
  --app-name NAME
```

The root wrapper must not live only in a repository-global or nested platform
scripts directory. It
requires all environment and target inputs—application, workspace, region,
bucket/object, run inputs, VM addresses, SSH identity, mock port, service paths,
project archive, checksum, task identifiers, and timeouts. It may load an ignored
config file only through the explicit `--config` argument. Provide no environment
defaults.

This is an invariant for every generated migration: the operator stays at the
migrated application root and invokes only `./deploy.sh`. Any OCI-specific helper
is an internal implementation detail and is not documented as an alternate entry
point.

Support `--dry-run`. In dry-run, validate and print the plan but perform no OCI,
SSH, SCP, firewall, systemd, or filesystem mutations.

The real run is one-stop and idempotent for migration-managed mocks:

1. validate inputs, tools, artifacts, and SHA-256 files;
2. resolve the OCI Data Integration workspace subnet;
3. install only the selected mock service on the supplied Compute VM;
4. restrict the mock port to the workspace CIDR and validate `GET /health`;
5. upload the `.project.zip` and call `import-request create` with replacement;
6. materialize the VM private endpoint and run inputs into imported REST tasks;
7. create or reuse the named application;
8. publish the root task with `application create-patch`;
9. wait for import and patch success, failing immediately on `FAILED`;
10. verify the root task with `application list-published-objects`;
11. print `READY` only after project import is successful and the runnable root
    task is published; include mock health only for a migration-managed mock.

Do not trigger the task unless the user explicitly includes execution in scope.

## Operator documentation contract

The app README includes:

- a Mermaid “How the POC works” diagram showing operator, app-local deployer,
  Compute mock, Object Storage, imported project, Application, root task, pipeline,
  routes, and outputs;
- the exact one-stop command;
- a numbered “What the one-stop script does” section;
- the OCI Console path to the published root task and its Run action;
- localhost and VCN health checks, expected outputs, and service logs;
- whether a mock is required, whether it existed, whether it was reused or
  created, and its final validator status.
