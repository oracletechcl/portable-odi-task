#!/usr/bin/env bash
set -euo pipefail

: "${OCI_NAMESPACE:?Missing OCI_NAMESPACE}"
: "${OCI_BUCKET:?Missing OCI_BUCKET}"

oci os object put \
  --namespace-name "${OCI_NAMESPACE}" \
  --bucket-name "${OCI_BUCKET}" \
  --name input/customers.csv \
  --file test-data/customers.csv \
  --force
