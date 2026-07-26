# Web Airflow behavior contract

Evidence: `cargaArchivoExterno.kjb` plus seven Web KTR files in the supplied source tree.

1. `Archivo Sesion (CL_BI_01)` is mapped to a retrying Airflow task.
2. It calls the source-derived seven dataset boundaries, in the OCI proof-of-concept order, and writes ISO-8859-1 `~|` CSV contracts.
3. Successful completion selects `Exito cargaArchivoExterno`; any terminal failure selects `Error cargaArchivoExterno` through `ONE_FAILED`.
4. All field ordering and formatting remain in `implementation/web_transformations.py`, independently testable from Airflow.

Source-to-target mapping: `cargaArchivoExterno.kjb` → `dags/habitat_web.py`; each `transf_*_TDS.ktr` → an entry in `DATASET_CONTRACTS` and `ROUTES`.
