#!/usr/bin/env bash
set -euo pipefail

# Replace this scaffold during the Deploy phase. It must never be handed off.
# Required behavior: --config/--app-name/--dry-run parsing; checksum validation;
# OCI Object Storage upload; import polling; REST endpoint materialization;
# exact Application create/reuse; publish polling; published-root verification.
# For external-reuse mocks, materialize the URL only: no curl, health probe,
# systemd, SSH, archive transfer, firewall, start, stop, or replacement action.

echo "ERROR: deploy-internal.sh is a scaffold. Implement and dry-run validate the migration deployment engine." >&2
exit 2
