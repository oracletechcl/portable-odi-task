# Sucursales Migration Changes

## Root Cause Analysis

### Observed Failure

The Pentaho Sucursales workload cannot run in this repository because its
databases, vendor extractors, shared filesystems, and mail server are
unavailable.

### Underlying Cause

The original orchestration is environment-coupled. Runtime behavior depends on
external shell scripts, database connections, mutable job variables, and
environment-specific notification configuration.

### Why Existing Guardrails Allowed It

The repository previously contained only a separate customer portability proof
of concept. It had no executable Sucursales contract, mock boundary, expected
outputs, OCI import package, or tests capable of detecting behavioral drift.

## How It Was Fixed

Pending implementation. The approved design introduces pure transformations,
a fixture-backed HTTP mock service with one startup wrapper, an OCI private
Compute deployment, and an OCI Data Integration REST-task pipeline export.

## Summary

Tracking documentation created. Implementation changes have not started.

## Validation

No validation has run. Results will be recorded after each Red/Green/Refactor
iteration and again at the full regression gate.

