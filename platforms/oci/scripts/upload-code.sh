#!/usr/bin/env bash
set -euo pipefail

: "${OCI_NAMESPACE:?Missing OCI_NAMESPACE}"
: "${OCI_BUCKET:?Missing OCI_BUCKET}"

oci os object put \
  --namespace-name "${OCI_NAMESPACE}" \
  --bucket-name "${OCI_BUCKET}" \
  --name scripts/customer_transform.py \
  --file src/pyspark/customer_transform.py \
  --force

oci os object put \
  --namespace-name "${OCI_NAMESPACE}" \
  --bucket-name "${OCI_BUCKET}" \
  --name scripts/validate_output.py \
  --file src/pyspark/validate_output.py \
  --force

oci os object put \
  --namespace-name "${OCI_NAMESPACE}" \
  --bucket-name "${OCI_BUCKET}" \
  --name scripts/customer-java-probe.jar \
  --file target/customer-java-probe.jar \
  --force

oci os object put \
  --namespace-name "${OCI_NAMESPACE}" \
  --bucket-name "${OCI_BUCKET}" \
  --name scripts/customer-scala-probe.jar \
  --file target/customer-scala-probe-scala.jar \
  --force

oci os object put \
  --namespace-name "${OCI_NAMESPACE}" \
  --bucket-name "${OCI_BUCKET}" \
  --name scripts/customer_transform.sql \
  --file src/sql/customer_transform.sql \
  --force
