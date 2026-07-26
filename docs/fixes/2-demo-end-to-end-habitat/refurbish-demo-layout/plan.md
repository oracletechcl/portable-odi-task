# Plan: Refurbish Demo Layout

## Goal

Group migration assets by target platform and Pentaho flow:

```text
habitat-e2e-demo/
├── airflow/
│   ├── sucursales/
│   └── web/
└── oci-odi/
    ├── sucursales/
    └── web/
```

## Plan

- [x] Inventory current files, git ownership, and old path references.
- [x] Add a failing directory-contract test.
- [x] Move Airflow and both OCI ODI migration assets.
- [x] Update scripts, documentation, ignore rules, and tests.
- [x] Run focused and repository validation.

## Safety

- Preserve the running VM services; this is a local repository reorganization.
- Preserve the ignored local deployment environment and SSH-key references.
- Preserve the completed Web OCI migration while moving it under `oci-odi/web`.
- Do not change source-of-truth assets under `habitat-e2e-demo/sot`.
