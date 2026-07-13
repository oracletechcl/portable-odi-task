#!/usr/bin/env bash
set -euo pipefail

required_variables=(
  OCI_TENANCY_OCID
  OCI_USER_OCID
  OCI_FINGERPRINT
  OCI_PRIVATE_KEY_BASE64
  OCI_REGION
)

for variable in "${required_variables[@]}"; do
  if [ -z "${!variable:-}" ]; then
    echo "Missing required variable: ${variable}" >&2
    exit 1
  fi
done

mkdir -p "${HOME}/.oci"
printf '%s' "${OCI_PRIVATE_KEY_BASE64}" | base64 --decode > "${HOME}/.oci/oci_api_key.pem"
chmod 600 "${HOME}/.oci/oci_api_key.pem"

cat > "${HOME}/.oci/config" <<EOF
[DEFAULT]
user=${OCI_USER_OCID}
fingerprint=${OCI_FINGERPRINT}
tenancy=${OCI_TENANCY_OCID}
region=${OCI_REGION}
key_file=${HOME}/.oci/oci_api_key.pem
EOF

oci os ns get >/dev/null
