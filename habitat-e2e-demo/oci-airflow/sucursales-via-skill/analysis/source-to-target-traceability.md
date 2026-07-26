# Source-to-target traceability

| Source evidence | Airflow target | Test/evidence |
| --- | --- | --- |
| `transf_obtenerPeriodoExtraer.ktr` | `obtener_periodos` | period rollover test |
| Atenciones previous/current shell entries | `atenciones` task chain | DAG task order |
| Agendamientos previous/current shell entries | `agendamientos` task chain | DAG task order |
| Mail failure hops | `notificar_error` tasks, `ALL_FAILED` | DAG structural review |
| ReplaceString / Formula / motive split KTR steps | pure transformations | focused tests |
