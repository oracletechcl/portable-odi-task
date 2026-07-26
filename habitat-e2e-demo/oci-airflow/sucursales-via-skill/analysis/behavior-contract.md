# Sucursales Airflow behavior contract

Evidence: `cargaArchivoExterno.kjb` and five KTR files.

1. Obtain current/prior period from the reused mock-backed period boundary.
2. Process Atenciones previous then current month.
3. Process Agendamientos previous then current month.
4. On any processing failure, send the corresponding error notification.
5. Preserve pure RUT normalization, closing-date derivation, and paired motivo
   split logic in `implementation/airflow_sucursales_transformations.py`.
