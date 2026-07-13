# Repository instructions

## Objective

Maintain a portable data integration proof of concept.

## Architecture rules

- Keep business transformations in PySpark, Python, SQL, YAML, or JSON.
- Do not place business logic exclusively in OCI Data Integration visual operators.
- Keep OCI deployment files under `platforms/oci`.
- Keep Databricks deployment files under `platforms/databricks`.
- Never commit secrets, OCIDs, private keys, passwords, or environment endpoints.
- Use `set -euo pipefail` in every shell script.
- Make transformation functions testable without OCI services.
- Promote the same immutable release artifact to TEST and PROD.

## Validation

Run `python -m compileall src`, `pytest -q`, and `mvn -q -DskipTests package`
before completion. When shell scripts change, run
`find platforms/oci/scripts -name "*.sh" -exec bash -n {} \;`.
