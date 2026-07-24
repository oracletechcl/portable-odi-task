# {{PROJECT_NAME}} Migrated Demo

The one-stop script prepares the supplied Compute VM mock, imports the immutable OCI
Data Integration project, publishes the runnable task, and reports `READY`.

## 1. Configure

Copy the blank deployment example to an ignored file. Fill every value. Keep OCI
identifiers, IPs, SSH key paths, bucket details, and endpoints out of version
control.

## 2. Preview

Run the generic deploy script with the explicit config path and `--dry-run`. Review
the resolved project, application, task, VM, network, archive, and run date.

## 3. Deploy

Run the same command without `--dry-run`. The script:

1. validates required inputs and checksums;
2. installs and health-checks the mock on the supplied Compute VM;
3. restricts the mock port to the workspace subnet;
4. uploads and imports `PROJECT-NAME.project.zip` with replacement;
5. materializes private mock URLs and run inputs into parameter-free REST tasks;
6. creates or reuses the named application;
7. publishes the named pipeline task and verifies it is present.

## 4. Run

Open the exact OCI Data Integration application and filter Tasks by the reported
runnable task identifier. If it is not on the first page, check the next page.
Choose **Run** without adding parameters and wait for a terminal run status.

## 5. Verify

Run the output validator. Compare the exact file set, row counts, byte format, and
SHA-256 values with the expected-output manifest.

## Troubleshooting

- Mock unavailable: inspect systemd status, localhost health, VCN routing, and the
  workspace-subnet firewall rule.
- Task absent: use filter/next page or CLI listing with all pages.
- Publication failed: inspect the terminal patch response and errors.
- Run failed: inspect the task-run response and mock service log.
