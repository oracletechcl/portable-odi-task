# HABITAT_SUCURSALES_VIA_SKILL Behavior Contract

- Source: `cargaArchivoExterno.kjb` plus five supplied KTR files.
- Calculate current and prior calendar periods; run Atenciones then Agendamientos
  for each period.
- Remove dots from `DNI_Ejecutivo`, derive `fechaCierre=YYYYMM01`, and expand
  paired comma-separated motivo lists with `$` parent/submotivo hierarchy.
- Preserve the evidenced failure route: failed processing -> notification -> abort.
