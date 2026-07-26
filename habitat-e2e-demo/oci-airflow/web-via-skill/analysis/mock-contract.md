# Mock contract

Ownership: `external-reuse`. The user supplies the Web mock on port 8002.

The DAG posts `{"runDate":"YYYY-MM-DD"}` to each route in `/v1/web/{configuracion-equipo-mesa,configuracion-equipo-usuario,opc-opcion,sec-seccion,sub-subseccion,tb-log-sistema,tb-sub-sistema-servicio}`. Each response must expose a `records` list.

Deployment only stores `MOCK_BASE_URL` as the `habitat_web_mock_base_url` Airflow Variable. It never health-checks, starts, stops, packages, or mutates the mock.
