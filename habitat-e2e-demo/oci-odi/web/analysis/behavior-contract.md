# Habitat Web Behavior Contract

## Scope

One Web application flow set: `cargaArchivoExterno.kjb` and its seven evidenced
KTR transformations. Source-of-truth inputs remain read-only.

## Job control flow

| Order | Stage | Success | Failure | Evidence |
| --- | --- | --- | --- | --- |
| 1 | `START` | Unconditionally enters `Archivo Sesion (CL_BI_01)` | Not applicable | `cargaArchivoExterno.kjb` hop |
| 2 | `Archivo Sesion (CL_BI_01)` | `Exito cargaArchivoExterno` | `Error cargaArchivoExterno` abort | `cargaArchivoExterno.kjb` shell entry and evaluated hops |

The referenced `guardarArchivoAcceso.sh` is absent from source evidence. Its
production semantics are not invented. The target makes all seven evidenced data
stages observable and stops on the first failed boundary.

## Transformation contract

| Stage | Source step order | Output |
| --- | --- | --- |
| `CONFIGURACION_EQUIPO_MESA` | Excel input → text output | 9 ordered fields |
| `CONFIGURACION_EQUIPO_USUARIO` | text input → filename date extraction → session splits → null handling → date formatting → constants → text output | 10 ordered output fields |
| `OPC_OPCION` | table input → text output | 13 ordered fields |
| `SEC_SECCION` | table input → text output | 6 ordered fields |
| `SUB_SUBSECCION` | table input → text output | 5 ordered fields |
| `TB_LOG_SISTEMA` | missing-date query → log → parameterized source query → text output | 15 ordered fields |
| `TB_SUB_SISTEMA_SERVICIO` | table input → text output | 12 ordered fields |

All outputs use `~|`, ISO-8859-1, LF, no header, no footer, and `.csv`.
`implementation/habitat_web/transformations.py` is the executable contract.

