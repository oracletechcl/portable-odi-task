# TDD Log: Refurbish Demo Layout

## Red

The first focused run produced three failures because neither platform root
existed and active files still referenced the retired paths. The contract
requires:

- exactly `sucursales` and `web` under the Airflow root;
- the existing Airflow assets, now under `mocks/airflow`;
- an explicit Web Airflow migration placeholder;
- the OCI ODI migrations under `oci-odi/sucursales` and `oci-odi/web`;
- removal of the two retired generic directory names; and
- no active runtime references to the retired paths.

## Green

After moving the assets and repairing path assumptions:

```text
Airflow Sucursales: 9 passed
OCI ODI Sucursales: 70 passed
OCI ODI Web: 1 passed
Directory layout: 3 passed
Repository: 101 passed
```

The repository-wide run initially exposed that the Web test relied on an
operator-provided `PYTHONPATH`. A local `conftest.py` now adds the Web
implementation root, so plain `pytest -q` passes.
