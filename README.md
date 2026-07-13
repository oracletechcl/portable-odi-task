# Portable OCI Data Integration PoC

This repository contains a portable data-integration proof of concept. It
keeps the customer transformation logic separate from deployment adapters,
uses GitHub as a simulation of Bitbucket CI/CD, and demonstrates execution in
OCI Data Flow with OCI Data Integration orchestration.

The PoC includes runnable Spark flavors in Python, Java, Scala, and SQL. It
also includes source-controlled deployment mappings for Databricks, Amazon
EMR, Microsoft Fabric, and Google Dataproc. Those external-platform mappings
are implementation guides only: no resources were provisioned or run outside
OCI.

## Executive readout

For the architecture diagram, component interactions, CI/CD flow, live OCI
asset inventory, validation evidence, current authorization limitation, and
recommended next steps, open the customer-facing
[PoC executive readout](docs/poc-readout.html).

## Key repository areas

- `src/` — portable transformation, validation, and language-flavor sources.
- `platforms/` — OCI deployment scripts and non-OCI deployment mappings.
- `specification/` and `environments/` — portable contract and environment
  configuration.
- `docs/documented-poc.md` — complete OCI asset inventory, including OCIDs.

The Data Integration pipeline design and export were completed. Direct OCI
Data Flow executions for the supported language probes succeeded. The
end-to-end Data Integration pipeline remains pending effective authorization
for its workspace principal to create Data Flow runs; IAM policies were not
modified by this PoC.
