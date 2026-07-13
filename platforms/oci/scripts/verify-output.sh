#!/usr/bin/env bash
set -euo pipefail

: "${OCI_NAMESPACE:?Missing OCI_NAMESPACE}"
: "${OCI_BUCKET:?Missing OCI_BUCKET}"

count="$(
  oci os object list \
    --namespace-name "${OCI_NAMESPACE}" \
    --bucket-name "${OCI_BUCKET}" \
    --prefix output/customers/ \
    --query 'length(data)' \
    --raw-output
)"

if [ "${count}" -lt 1 ]; then
  echo "No output objects found" >&2
  exit 1
fi

echo "Output objects found: ${count}"
