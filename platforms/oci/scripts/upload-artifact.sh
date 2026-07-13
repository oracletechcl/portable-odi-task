#!/usr/bin/env bash
set -euo pipefail

: "${OCI_NAMESPACE:?Missing OCI_NAMESPACE}"
: "${OCI_BUCKET:?Missing OCI_BUCKET}"
: "${ARTIFACT_FILE:?Missing ARTIFACT_FILE}"
: "${ARTIFACT_OBJECT_NAME:?Missing ARTIFACT_OBJECT_NAME}"

if [ ! -f "${ARTIFACT_FILE}" ]; then
  echo "Artifact file does not exist: ${ARTIFACT_FILE}" >&2
  exit 1
fi

oci os object put \
  --namespace-name "${OCI_NAMESPACE}" \
  --bucket-name "${OCI_BUCKET}" \
  --name "${ARTIFACT_OBJECT_NAME}" \
  --file "${ARTIFACT_FILE}" \
  --force
