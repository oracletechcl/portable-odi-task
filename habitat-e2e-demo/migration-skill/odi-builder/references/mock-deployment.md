# Mock Deployment

Build one deterministic mock service for unavailable backend boundaries. It must be
useful for OCI integration proof while remaining safe to run without production
systems.

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

## Generic one-stop deployment

The deploy wrapper requires all environment and target inputs—application,
workspace, region, bucket/object, run date, VM addresses, SSH identity, mock port,
service paths, project archive, checksum, task identifier, and timeouts. It may
load an ignored config file only when that config path is itself explicit.

Support `--dry-run`. In dry-run, validate and print the plan but perform no OCI,
SSH, SCP, firewall, systemd, or filesystem mutations.
