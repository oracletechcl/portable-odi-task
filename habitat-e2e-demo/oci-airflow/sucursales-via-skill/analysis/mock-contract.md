# Mock contract

All legacy database, shell-download, file, and mail boundaries are
`external-reuse`: the user supplies the port-8000 mock on the Airflow host.
Deployment materializes `sucursales_mock_base_url` in Airflow Variables only.
It never probes, packages, starts, stops, or modifies that mock. Route validation
occurs during the authorized Airflow DAG run.
