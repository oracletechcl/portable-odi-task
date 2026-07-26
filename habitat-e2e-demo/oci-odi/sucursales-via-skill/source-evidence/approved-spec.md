# Feature Specification: Sucursales migration

🏠 [Delivery Home](../../README.md) | 📚 [Migration Spec Index](../INDEX.md) | 📝 [Plan](./plan.md) | ✅ [Tasks](./tasks.md) | 🧪 [TDD](./tdd.md) | 🔗 [Traceability](./traceability.md) | ☁️ [To-Be](../../cloud-native-architecture/canonical-app-to-be/Sucursales/to-be.md) | 🚚 [Migration Strategy](../../cloud-native-architecture/canonical-app-to-be/Sucursales/migration-strategy.md)

**Feature Branch**: `migration-Sucursales`
**Status**: Draft
**Input**: Introspector analysis for canonical app `Sucursales`

## User Scenarios & Testing

### User Story 1 - Preserve Sucursales behavior (Priority: P1)
Sucursales users need the migrated application to preserve the behavior documented in the app deep dive, especially Jobs: `cargaArchivoExterno.kjb`..

**Why this priority**: The deep-dive is the first-class analysis artifact for this app and captures the behavior that must not regress.

**Independent Test**: Run the migration contract tests generated from `app-by-app-analysis/Sucursales/deep-dive.md` and verify the same inputs, processing, and outputs.

**Acceptance Scenarios**:
1. **Given** the analyzed `Sucursales` behavior in deep-dive evidence, **When** the migrated app is exercised for `FR-Sucursales-01`, **Then** it satisfies Preserve the evidenced behavior described in deep-dive B9..

### Edge Cases
- Missing source evidence blocks implementation until the gap is resolved in the analysis output.
- Target architecture conflicts must be reconciled against the deep-dive behavior contract before coding.

## Requirements

### Functional Requirements
- **FR-Sucursales-01**: System MUST Preserve the evidenced behavior described in deep-dive B9. ([evidence](../../app-by-app-analysis/Sucursales/deep-dive.md#b7-functional-and-non-functional-requirements))

### Non-Functional Requirements
- No non-functional requirements were evidenced in [deep-dive B7](../../app-by-app-analysis/Sucursales/deep-dive.md#b7-functional-and-non-functional-requirements).

### Key Entities
- # Evidence Index: Sucursales
- ## Core Anchors
- Source: `<source-root>/Sucursales`
- Source files: 6
- Config files: 0
- ## Pattern Anchors
- Contract-service matches: 0 service classes, 0 WSDL files
- Application-server interface matches: 0 service interfaces

## Success Criteria

### Measurable Outcomes
1. **Given** the analyzed `Sucursales` behavior in deep-dive evidence, **When** the migrated app is exercised for `FR-Sucursales-01`, **Then** it satisfies Preserve the evidenced behavior described in deep-dive B9..

## Source Of Truth
- [Deep Dive](../../app-by-app-analysis/Sucursales/deep-dive.md)
- [Deep Dive B7](../../app-by-app-analysis/Sucursales/deep-dive.md#b7-functional-and-non-functional-requirements)
- [Deep Dive B9](../../app-by-app-analysis/Sucursales/deep-dive.md#b9-processing-logic)
- [To-Be Architecture](../../cloud-native-architecture/canonical-app-to-be/Sucursales/to-be.md)
- [Migration Strategy](../../cloud-native-architecture/canonical-app-to-be/Sucursales/migration-strategy.md)
- [Roadmap](../../modernization-roadmap/Sucursales/roadmap.md)
- [Evidence Index](../../app-by-app-analysis/Sucursales/evidence-index.md)

## Current Behavior Contract
- Jobs: `cargaArchivoExterno.kjb`.
- Primary transformations: `transf_AgendamientoZeroQ_TDS.ktr`, `transf_AtencionesZeroQ_TDS.ktr`, `transf_MotivoAgendamientoZeroQ_TDS.ktr`, `transf_MotivoAtencionZeroQ_TDS.ktr`, `transf_obtenerPeriodoExtraer.ktr`.
- Backup/variant transformations: Not evidenced.
- `cargaArchivoExterno` in `cargaArchivoExterno.kjb` starts the control flow and invokes Not evidenced.
- **cargaArchivoExterno** (`cargaArchivoExterno.kjb`):
- Obtiene Periodo Extraer -> Atenciones ZeroQ - Mes Anterior (success) — previous entry succeeded.
- Obtiene Periodo Extraer -> Aborta 01 - Proceso Carga Archivo Externo (failure) — previous entry failed or evaluated false.
- START -> Obtiene Periodo Extraer (unconditional) — always continue.
- Atenciones ZeroQ - Mes Anterior -> Atenciones ZeroQ - Mes Actual (success) — previous entry succeeded.
- Atenciones ZeroQ - Mes Anterior -> Notificacion Error (failure) — previous entry failed or evaluated false.
- Notificacion Error -> Aborta 01 - Proceso Carga Archivo Externo (unconditional) — always continue.
- Atenciones ZeroQ - Mes Actual -> Notificacion Error (failure) — previous entry failed or evaluated false.
- Atenciones ZeroQ - Mes Actual -> Agendamiento ZeroQ - Mes Anterior (success) — previous entry succeeded.
- Agendamiento ZeroQ - Mes Anterior -> Agendamiento ZeroQ - Mes Actual (success) — previous entry succeeded.
- Agendamiento ZeroQ - Mes Actual -> Archivo Externo "Atencion Sucursal", Exitoso (success) — previous entry succeeded.
- Agendamiento ZeroQ - Mes Anterior -> Notificacion Error (failure) — previous entry failed or evaluated false.
- Agendamiento ZeroQ - Mes Actual -> Notificacion Error (failure) — previous entry failed or evaluated false.
- **transf_AgendamientoZeroQ_TDS** (`transf_AgendamientoZeroQ_TDS.ktr`): Archivo_AgendamientoZeroQ -> Replace puntos en el rutEjecutivo (flow); Replace puntos en el rutEjecutivo -> Extrae Fecha Archivo (flow); Extrae Fecha Archivo -> Obtiene Fecha Cierre (flow); Obtiene Fecha Cierre -> Campos que continuan (flow); Campos que continuan -> AgendamientoZeroQ (flow).
- **transf_AtencionesZeroQ_TDS** (`transf_AtencionesZeroQ_TDS.ktr`): Campos que continuan -> AtencionesZeroQ (flow); Extrae Fecha Archivo -> Obtiene Fecha Cierre (flow); Replace puntos en el rutEjecutivo -> Extrae Fecha Archivo (flow); Obtiene Fecha Cierre -> Campos que continuan (flow); Archivo_AtencionZeroQ -> Replace puntos en el rutEjecutivo (flow).
- **transf_MotivoAgendamientoZeroQ_TDS** (`transf_MotivoAgendamientoZeroQ_TDS.ktr`): Archivo_AgendamientoZeroQ -> dummy (flow); dummy -> split IDMotivos (flow); dummy -> split desc Motivos (flow); split IDMotivos -> Split fields ID Mot (flow); split desc Motivos -> Split fields Desc Mov (flow); Split fields ID Mot -> Blocking step (flow); Split fields Desc Mov -> Select values (flow); Blocking step -> Stream lookup (flow); Select values -> Stream lookup (flow); Stream lookup -> Select values motivos (flow); Select values motivos -> Extrae Fecha Archivo (flow); Extrae Fecha Archivo -> Obtiene Fecha Cierre (flow); Obtiene Fecha Cierre -> Crea Archivo motivosAgendamientoZeroq (flow).
- **transf_MotivoAtencionZeroQ_TDS** (`transf_MotivoAtencionZeroQ_TDS.ktr`): Dummy (do nothing) -> split IDMotivos (flow); split IDMotivos -> Split fields ID Mot (flow); Dummy (do nothing) -> split desc Motivos (flow); split desc Motivos -> Split fields Desc Mov (flow); Split fields Desc Mov -> Select values (flow); Select values -> Stream lookup (flow); Stream lookup -> Select values motivos (flow); Split fields ID Mot -> Blocking step (flow); Blocking step -> Stream lookup (flow); Archivo_AtencionZeroQ -> Dummy (do nothing) (flow); Select values motivos -> Extrae Fecha Archivo (flow); Extrae Fecha Archivo -> Obtiene Fecha Cierre (flow); Obtiene Fecha Cierre -> Crea Archivo motivosAtencionZeroq (flow).
- **transf_obtenerPeriodoExtraer** (`transf_obtenerPeriodoExtraer.ktr`): Obtener Listado Fechas -> Asigna Variables (flow).
- transf_AgendamientoZeroQ_TDS.ktr: database connection name=AgileBI; type=MONETDB; access=Native; server=localhost; database=pentaho-instaview; port=50000; username=monetdb
- transf_AgendamientoZeroQ_TDS.ktr: database connection name=Bonobo; type=MYSQL; access=Native; server=localhost; database=bonobo; port=3306; username=root
- transf_AgendamientoZeroQ_TDS.ktr: database connection name=cnTower; type=MSSQL; access=Native; server=PDTOWH1; database=WMP_HABITAT; port=1433; username=DATAWAREHOUSE
- transf_AgendamientoZeroQ_TDS.ktr: database connection name=FUGA; type=ORACLE; access=Native; server=lnxdbplan12c.afphabitat.cl; database=PRODWINV; port=1521; username=fdelcamp[FUGA]
- transf_AgendamientoZeroQ_TDS.ktr: database connection name=Kettle; type=ORACLE; access=Native; server=192.168.10.63; database=expl10g2; port=1521; username=kettle
- transf_AgendamientoZeroQ_TDS.ktr: database connection name=MsSQLServer_JNDI@TotalPack(Datawarehouse); type=ORACLE; access=JNDI; database=TotalPack; port=1521
- transf_AgendamientoZeroQ_TDS.ktr: database connection name=MySQL5; type=MYSQL; access=Native; server=localhost; database=testPentaho; port=3306; username=root
- transf_AgendamientoZeroQ_TDS.ktr: database connection name=MySQL_JNDI@SGC(Datawarehouse); type=MYSQL; access=JNDI; server=192.168.200.130; database=SGC; port=3306
- transf_AgendamientoZeroQ_TDS.ktr: database connection name=Oracle_JDBC@DESA_RTP(Datawarehouse); type=ORACLE; access=Native; database=(DESCRIPTION=(FAILOVER=on)(LOAD_BALANCE=yes)(ADDRESS_LIST=(ADDRESS=(PROTOCOL=TCP)(HOST=dbdete10g-rac1.afphabitat.cl)(PORT=1532)))(CONNECT_DATA=(FAILOVER_MODE=(TYPE=select)(METHOD=basic))(SERVER=dedicated)(SERVICE_NAME=DESARTP))); port=-1; username=CZAVALET
- transf_AgendamientoZeroQ_TDS.ktr: database connection name=Oracle_JDBC@DESA_RTP(IPINCHEI); type=ORACLE; access=Native; database=(DESCRIPTION=(FAILOVER=on)(LOAD_BALANCE=yes)(ADDRESS_LIST=(ADDRESS=(PROTOCOL=TCP)(HOST=dbdete10g-rac1.afphabitat.cl)(PORT=1532)))(CONNECT_DATA=(FAILOVER_MODE=(TYPE=select)(METHOD=basic))(SERVER=dedicated)(SERVICE_NAME=DESARTP))); port=-1; username=ipinchei[exp_enfermoterminal]
- transf_AgendamientoZeroQ_TDS.ktr: database connection name=Oracle_JNDI@DESA_RTP(IPINCHEI); type=ORACLE; access=Native; database=(DESCRIPTION=(FAILOVER=on)(LOAD_BALANCE=yes)(ADDRESS_LIST=(ADDRESS=(PROTOCOL=TCP)(HOST=dbdete10g-rac1.afphabitat.cl)(PORT=1532)))(CONNECT_DATA=(FAILOVER_MODE=(TYPE=select)(METHOD=basic))(SERVER=dedicated)(SERVICE_NAME=DESARTP))); port=-1; username=ipinchei[exp_enfermoterminal]
- transf_AgendamientoZeroQ_TDS.ktr: database connection name=Oracle_JNDI@DOCUWARE(Datawarehouse); type=ORACLE; access=JNDI; database=DOCUWARE; port=1521
- transf_AgendamientoZeroQ_TDS.ktr: database connection name=Oracle_JNDI@EXPL10G2(Datawarehouse); type=ORACLE; access=JNDI; server=192.168.10.63; database=EXPL10G2; port=1521
- transf_AgendamientoZeroQ_TDS.ktr: database connection name=Oracle_JNDI@FINPRD(Datawarehouse); type=ORACLE; access=JNDI; database=FINPRD; port=1521
- transf_AgendamientoZeroQ_TDS.ktr: database connection name=Oracle_JNDI@HABITAT(Cierre_Mes); type=ORACLE; access=JNDI; server=${ServidorCierreMes}; database=CIERRE_MES; port=${puerto.base.Oracle}
- transf_AgendamientoZeroQ_TDS.ktr: database connection name=Oracle_JNDI@PRDINV(Datawarehouse); type=ORACLE; access=JNDI; database=PRDINV; port=1521
- transf_AgendamientoZeroQ_TDS.ktr: database connection name=Oracle_JNDI@PROD11G(Datawarehouse); type=ORACLE; access=JNDI; database=PROD11G; port=-1
- transf_AgendamientoZeroQ_TDS.ktr: database connection name=Oracle_JNDI@PRODAFP(Datawarehouse); type=ORACLE; access=JNDI; database=PRODAFP; port=1521
- transf_AgendamientoZeroQ_TDS.ktr: database connection name=Oracle_JNDI@PRODWINV(Datawarehouse); type=ORACLE; access=JNDI; server=lnxdbplan12c.afphabitat.cl; database=PRODWINV; port=1521
- transf_AgendamientoZeroQ_TDS.ktr: database connection name=Oracle_JNDI@RTCHabitat(Datawarehouse); type=ORACLE; access=JNDI; server=qa-rac2-vip.afphabitat.cl; database=RTCHabitat; port=1521
- transf_AgendamientoZeroQ_TDS.ktr: database connection name=OracleJDBC@CERTRTC(Datawarehouse); type=ORACLE; access=Native; database=(DESCRIPTION=(FAILOVER=on)(LOAD_BALANCE=yes)(ADDRESS_LIST=(ADDRESS=(PROTOCOL=TCP)(HOST=dbcert10g-rac1-vip)(PORT=1531))(ADDRESS=(PROTOCOL=TCP)(HOST=dbcert10g-rac2-vip)(PORT=1531)))(CONNECT_DATA=(FAILOVER_MODE=(TYPE=select)(METHOD=basic))(SER; port=-1; username=DATAWAREHOUSE
- transf_AgendamientoZeroQ_TDS.ktr: database connection name=OracleJDBC@CERTRTP(Datawarehouse); type=ORACLE; access=Native; database=(DESCRIPTION=(FAILOVER=on)(LOAD_BALANCE=yes)(ADDRESS_LIST=(ADDRESS=(PROTOCOL=TCP)(HOST=dbcert10g-rac1-vip)(PORT=1532)))(CONNECT_DATA=(FAILOVER_MODE=(TYPE=select)(METHOD=basic))(SERVER=dedicated)(SERVICE_NAME=CERTRTP))); port=-1; username=datawarehouse
- transf_AgendamientoZeroQ_TDS.ktr: database connection name=OracleJDBC@DESARTC(Datawarehouse); type=ORACLE; access=Native; database=(DESCRIPTION=(FAILOVER=on)(LOAD_BALANCE=yes)(ADDRESS_LIST=(ADDRESS=(PROTOCOL=TCP)(HOST=dbdete10g-rac1.afphabitat.cl)(PORT=1531)))(CONNECT_DATA=(FAILOVER_MODE=(TYPE=select)(METHOD=basic))(SERVER=dedicated)(SERVICE_NAME=DESARTC))); port=-1; username=CZAVALET
- transf_AgendamientoZeroQ_TDS.ktr: database connection name=OracleJDBC@DESARTP(Datawarehouse); type=ORACLE; access=Native; database=(DESCRIPTION=(FAILOVER=on)(LOAD_BALANCE=yes)(ADDRESS_LIST=(ADDRESS=(PROTOCOL=TCP)(HOST=dbdete10g-rac1.afphabitat.cl)(PORT=1532)))(CONNECT_DATA=(FAILOVER_MODE=(TYPE=select)(METHOD=basic))(SERVER=dedicated)(SERVICE_NAME=DESARTP))); port=-1; username=czavalet
- transf_AgendamientoZeroQ_TDS.ktr: database connection name=OracleJDBC@DESARTP(OWN_TRIBUTARIO); type=ORACLE; access=Native; database=(DESCRIPTION=(FAILOVER=on)(LOAD_BALANCE=yes)(ADDRESS_LIST=(ADDRESS=(PROTOCOL=TCP)(HOST=dbdete10g-rac1.afphabitat.cl)(PORT=1532)))(CONNECT_DATA=(FAILOVER_MODE=(TYPE=select)(METHOD=basic))(SERVER=dedicated)(SERVICE_NAME=DESARTP))); port=-1; username=czavalet
- transf_AgendamientoZeroQ_TDS.ktr: database connection name=OracleJDBC@PRODCAR(AHERMOSI); type=ORACLE; access=Native; database=(DESCRIPTION=(FAILOVER=on)(LOAD_BALANCE=yes)(ADDRESS_LIST=(ADDRESS=(PROTOCOL=TCP)(HOST=lnxdbprod11g-rac1-vip.afphabitat.cl)(PORT=1523))(ADDRESS=(PROTOCOL=TCP)(HOST=lnxdbprod11g-rac2-vip.afphabitat.cl)(PORT=1523)))(CONNECT_DATA=(FAILOVER_MOD; port=-1; username=AHERMOSI
- transf_AgendamientoZeroQ_TDS.ktr: database connection name=PostgreSQL_JNDI@JiraLEAN(bigdata); type=POSTGRESQL; access=JNDI; server=atlprdh1.afphabitat.cl; database=LEAN; port=45432
- transf_AgendamientoZeroQ_TDS.ktr: database connection name=SampleData; type=HYPERSONIC; access=Native; server=localhost; database=SampleData; port=9001; username=pentaho_user
- transf_AgendamientoZeroQ_TDS.ktr: database connection name=SybaseIQ_JDBC@habitat(DMGestion); type=SYBASEIQ; access=Native; server=192.168.10.247; database=habitat; port=2638; username=DMGestion
- transf_AgendamientoZeroQ_TDS.ktr: database connection name=SybaseIQ_JNDI@habitat(AFC); type=SYBASEIQ; access=JNDI; server=192.168.10.247; database=AFC; port=2638
- transf_AgendamientoZeroQ_TDS.ktr: database connection name=SybaseIQ_JNDI@habitat(Auditoria); type=SYBASEIQ; access=JNDI; database=Auditoria; port=1521
- transf_AgendamientoZeroQ_TDS.ktr: database connection name=SybaseIQ_JNDI@habitat(BonoCargoFiscal); type=SYBASEIQ; access=JNDI; database=BonoCargoFiscal; port=1521
- transf_AgendamientoZeroQ_TDS.ktr: database connection name=SybaseIQ_JNDI@habitat(Circular119); type=SYBASEIQ; access=JNDI; database=Circular119; port=1521
- transf_AgendamientoZeroQ_TDS.ktr: database connection name=SybaseIQ_JNDI@habitat(Circular1509); type=SYBASEIQ; access=JNDI; server=${ServidorSybaseIQ}; database=Circular1509; port=${puerto.SybaseIQ}
- transf_AgendamientoZeroQ_TDS.ktr: database connection name=SybaseIQ_JNDI@habitat(Circular1532); type=SYBASEIQ; access=JNDI; database=Circular1532; port=1521
- transf_AgendamientoZeroQ_TDS.ktr: database connection name=SybaseIQ_JNDI@habitat(Circular1536); type=SYBASEIQ; access=JNDI; server=${ServidorSybaseIQ}; database=Circular1536; port=${puerto.SybaseIQ}
- transf_AgendamientoZeroQ_TDS.ktr: database connection name=SybaseIQ_JNDI@habitat(Circular1661V1); type=SYBASEIQ; access=JNDI; server=${ServidorSybaseIQ}; database=Circular1661V1; port=${puerto.SybaseIQ}
- transf_AgendamientoZeroQ_TDS.ktr: database connection name=SybaseIQ_JNDI@habitat(ControlProcesos); type=SYBASEIQ; access=JNDI; database=ControlProcesos; port=1521
- transf_AgendamientoZeroQ_TDS.ktr: database connection name=SybaseIQ_JNDI@habitat(Datawarehouse); type=SYBASEIQ; access=JNDI; server=iqprod16; database=Datawarehouse; port=2638
- transf_AgendamientoZeroQ_TDS.ktr: database connection name=SybaseIQ_JNDI@habitat(DDS); type=GENERIC; access=JNDI; server=192.168.10.247; database=DDS; port=2638
- transf_AgendamientoZeroQ_TDS.ktr: database connection name=SybaseIQ_JNDI@habitat(DMGestion); type=SYBASEIQ; access=JNDI; server=iqprod16; database=DMGestion; port=2638
- transf_AgendamientoZeroQ_TDS.ktr: database connection name=SybaseIQ_JNDI@habitat(Interfaz); type=SYBASEIQ; access=JNDI; database=DMGestion; port=1521
- transf_AgendamientoZeroQ_TDS.ktr: database connection name=SybaseIQ_JNDI@habitat(LavadoActivos); type=SYBASEIQ; access=JNDI; database=LavadoActivos; port=1521
- transf_AgendamientoZeroQ_TDS.ktr: database connection name=SybaseIQ_JNDI@habitat(MAC); type=SYBASEIQ; access=JNDI; server=${ServidorSybaseIQ}; database=MAC; port=${puerto.SybaseIQ}
- transf_AgendamientoZeroQ_TDS.ktr: database connection name=SybaseIQ_JNDI@habitat(PAET); type=SYBASEIQ; access=JNDI; database=PAET; port=1521
- transf_AgendamientoZeroQ_TDS.ktr: database connection name=SybaseIQ_JNDI@habitat(PowerBI); type=SYBASEIQ; access=JNDI; database=PowerBI; port=1521
- transf_AgendamientoZeroQ_TDS.ktr: database connection name=SybaseIQ_JNDI@habitat(Retiro10); type=SYBASEIQ; access=JNDI; database=Retiro10; port=1521
- transf_AgendamientoZeroQ_TDS.ktr: database connection name=SybaseIQ_JNDI@habitat(SalesForce); type=SYBASEIQ; access=JNDI; database=DMGestion; port=1521
- transf_AgendamientoZeroQ_TDS.ktr: database connection name=SybaseIQ_JNDI@habitat(TDS); type=SYBASEIQ; access=JNDI; database=TDS; port=1521
- transf_AgendamientoZeroQ_TDS.ktr: database connection name=testOracle@HABITAT; type=ORACLE; access=Native; database=(DESCRIPTION=(FAILOVER=on)(LOAD_BALANCE=yes)(ADDRESS_LIST=(ADDRESS=(PROTOCOL=TCP)(HOST=habitatvip1.afphabitat.cl)(PORT=1521))(ADDRESS=(PROTOCOL=TCP)(HOST=habitatvip2.afphabitat.cl)(PORT=1521)))(CONNECT_DATA=(FAILOVER_MODE=(TYPE=select)(METH; port=-1; username=datawarehouse
- transf_AgendamientoZeroQ_TDS.ktr: database connection name=testOracle@PRODAFP; type=ORACLE; access=Native; database=(DESCRIPTION=(FAILOVER=on)(LOAD_BALANCE=on)(ADDRESS_LIST=(ADDRESS=(PROTOCOL=TCP)(HOST=prodafpvip1.afphabitat.cl)(PORT=1522))(ADDRESS=(PROTOCOL=TCP)(HOST=prodafpvip2.afphabitat.cl)(PORT=1522)))(CONNECT_DATA=(FAILOVER_MODE=(TYPE=select)(METHO; port=-1; username=czavalet
- transf_AgendamientoZeroQ_TDS.ktr: database connection name=testSybase@IQProd; type=SYBASEIQ; access=Native; server=192.168.10.247; database=habitat; port=2638; username=DMGestion
- transf_AgendamientoZeroQ_TDS.ktr: database connection name=testSybase@IQProd(16.1); type=SYBASEIQ; access=Native; server=192.168.10.32; database=iq_habitat; port=2638; username=DMGestion
- transf_AgendamientoZeroQ_TDS.ktr: database connection name=TotalPackV24; type=MSSQL; access=Native; server=NET-SQL01; database=modeltotalpack; port=1433; username=DATAWAREHOUSE
- transf_AtencionesZeroQ_TDS.ktr: database connection name=AgileBI; type=MONETDB; access=Native; server=localhost; database=pentaho-instaview; port=50000; username=monetdb
- transf_AtencionesZeroQ_TDS.ktr: database connection name=Bonobo; type=MYSQL; access=Native; server=localhost; database=bonobo; port=3306; username=root
- transf_AtencionesZeroQ_TDS.ktr: database connection name=cnTower; type=MSSQL; access=Native; server=PDTOWH1; database=WMP_HABITAT; port=1433; username=DATAWAREHOUSE
- transf_AtencionesZeroQ_TDS.ktr: database connection name=FUGA; type=ORACLE; access=Native; server=lnxdbplan12c.afphabitat.cl; database=PRODWINV; port=1521; username=fdelcamp[FUGA]
- transf_AtencionesZeroQ_TDS.ktr: database connection name=Kettle; type=ORACLE; access=Native; server=192.168.10.63; database=expl10g2; port=1521; username=kettle
- transf_AtencionesZeroQ_TDS.ktr: database connection name=MsSQLServer_JNDI@TotalPack(Datawarehouse); type=ORACLE; access=JNDI; database=TotalPack; port=1521
- transf_AtencionesZeroQ_TDS.ktr: database connection name=MySQL5; type=MYSQL; access=Native; server=localhost; database=testPentaho; port=3306; username=root
- transf_AtencionesZeroQ_TDS.ktr: database connection name=MySQL_JNDI@SGC(Datawarehouse); type=MYSQL; access=JNDI; server=192.168.200.130; database=SGC; port=3306
- transf_AtencionesZeroQ_TDS.ktr: database connection name=Oracle_JDBC@DESA_RTP(Datawarehouse); type=ORACLE; access=Native; database=(DESCRIPTION=(FAILOVER=on)(LOAD_BALANCE=yes)(ADDRESS_LIST=(ADDRESS=(PROTOCOL=TCP)(HOST=dbdete10g-rac1.afphabitat.cl)(PORT=1532)))(CONNECT_DATA=(FAILOVER_MODE=(TYPE=select)(METHOD=basic))(SERVER=dedicated)(SERVICE_NAME=DESARTP))); port=-1; username=CZAVALET
- transf_AtencionesZeroQ_TDS.ktr: database connection name=Oracle_JDBC@DESA_RTP(IPINCHEI); type=ORACLE; access=Native; database=(DESCRIPTION=(FAILOVER=on)(LOAD_BALANCE=yes)(ADDRESS_LIST=(ADDRESS=(PROTOCOL=TCP)(HOST=dbdete10g-rac1.afphabitat.cl)(PORT=1532)))(CONNECT_DATA=(FAILOVER_MODE=(TYPE=select)(METHOD=basic))(SERVER=dedicated)(SERVICE_NAME=DESARTP))); port=-1; username=ipinchei[exp_enfermoterminal]
- transf_AtencionesZeroQ_TDS.ktr: database connection name=Oracle_JNDI@DESA_RTP(IPINCHEI); type=ORACLE; access=Native; database=(DESCRIPTION=(FAILOVER=on)(LOAD_BALANCE=yes)(ADDRESS_LIST=(ADDRESS=(PROTOCOL=TCP)(HOST=dbdete10g-rac1.afphabitat.cl)(PORT=1532)))(CONNECT_DATA=(FAILOVER_MODE=(TYPE=select)(METHOD=basic))(SERVER=dedicated)(SERVICE_NAME=DESARTP))); port=-1; username=ipinchei[exp_enfermoterminal]
- transf_AtencionesZeroQ_TDS.ktr: database connection name=Oracle_JNDI@DOCUWARE(Datawarehouse); type=ORACLE; access=JNDI; database=DOCUWARE; port=1521
- transf_AtencionesZeroQ_TDS.ktr: database connection name=Oracle_JNDI@EXPL10G2(Datawarehouse); type=ORACLE; access=JNDI; server=192.168.10.63; database=EXPL10G2; port=1521
- transf_AtencionesZeroQ_TDS.ktr: database connection name=Oracle_JNDI@FINPRD(Datawarehouse); type=ORACLE; access=JNDI; database=FINPRD; port=1521
- transf_AtencionesZeroQ_TDS.ktr: database connection name=Oracle_JNDI@HABITAT(Cierre_Mes); type=ORACLE; access=JNDI; server=${ServidorCierreMes}; database=CIERRE_MES; port=${puerto.base.Oracle}
- transf_AtencionesZeroQ_TDS.ktr: database connection name=Oracle_JNDI@PRDINV(Datawarehouse); type=ORACLE; access=JNDI; database=PRDINV; port=1521
- transf_AtencionesZeroQ_TDS.ktr: database connection name=Oracle_JNDI@PROD11G(Datawarehouse); type=ORACLE; access=JNDI; database=PROD11G; port=-1
- transf_AtencionesZeroQ_TDS.ktr: database connection name=Oracle_JNDI@PRODAFP(Datawarehouse); type=ORACLE; access=JNDI; database=PRODAFP; port=1521
- transf_AtencionesZeroQ_TDS.ktr: database connection name=Oracle_JNDI@PRODWINV(Datawarehouse); type=ORACLE; access=JNDI; server=lnxdbplan12c.afphabitat.cl; database=PRODWINV; port=1521
- transf_AtencionesZeroQ_TDS.ktr: database connection name=Oracle_JNDI@RTCHabitat(Datawarehouse); type=ORACLE; access=JNDI; server=qa-rac2-vip.afphabitat.cl; database=RTCHabitat; port=1521
- transf_AtencionesZeroQ_TDS.ktr: database connection name=OracleJDBC@CERTRTC(Datawarehouse); type=ORACLE; access=Native; database=(DESCRIPTION=(FAILOVER=on)(LOAD_BALANCE=yes)(ADDRESS_LIST=(ADDRESS=(PROTOCOL=TCP)(HOST=dbcert10g-rac1-vip)(PORT=1531))(ADDRESS=(PROTOCOL=TCP)(HOST=dbcert10g-rac2-vip)(PORT=1531)))(CONNECT_DATA=(FAILOVER_MODE=(TYPE=select)(METHOD=basic))(SER; port=-1; username=DATAWAREHOUSE
- transf_AtencionesZeroQ_TDS.ktr: database connection name=OracleJDBC@CERTRTP(Datawarehouse); type=ORACLE; access=Native; database=(DESCRIPTION=(FAILOVER=on)(LOAD_BALANCE=yes)(ADDRESS_LIST=(ADDRESS=(PROTOCOL=TCP)(HOST=dbcert10g-rac1-vip)(PORT=1532)))(CONNECT_DATA=(FAILOVER_MODE=(TYPE=select)(METHOD=basic))(SERVER=dedicated)(SERVICE_NAME=CERTRTP))); port=-1; username=datawarehouse
- transf_AtencionesZeroQ_TDS.ktr: database connection name=OracleJDBC@DESARTC(Datawarehouse); type=ORACLE; access=Native; database=(DESCRIPTION=(FAILOVER=on)(LOAD_BALANCE=yes)(ADDRESS_LIST=(ADDRESS=(PROTOCOL=TCP)(HOST=dbdete10g-rac1.afphabitat.cl)(PORT=1531)))(CONNECT_DATA=(FAILOVER_MODE=(TYPE=select)(METHOD=basic))(SERVER=dedicated)(SERVICE_NAME=DESARTC))); port=-1; username=CZAVALET
- transf_AtencionesZeroQ_TDS.ktr: database connection name=OracleJDBC@DESARTP(Datawarehouse); type=ORACLE; access=Native; database=(DESCRIPTION=(FAILOVER=on)(LOAD_BALANCE=yes)(ADDRESS_LIST=(ADDRESS=(PROTOCOL=TCP)(HOST=dbdete10g-rac1.afphabitat.cl)(PORT=1532)))(CONNECT_DATA=(FAILOVER_MODE=(TYPE=select)(METHOD=basic))(SERVER=dedicated)(SERVICE_NAME=DESARTP))); port=-1; username=czavalet
- transf_AtencionesZeroQ_TDS.ktr: database connection name=OracleJDBC@DESARTP(OWN_TRIBUTARIO); type=ORACLE; access=Native; database=(DESCRIPTION=(FAILOVER=on)(LOAD_BALANCE=yes)(ADDRESS_LIST=(ADDRESS=(PROTOCOL=TCP)(HOST=dbdete10g-rac1.afphabitat.cl)(PORT=1532)))(CONNECT_DATA=(FAILOVER_MODE=(TYPE=select)(METHOD=basic))(SERVER=dedicated)(SERVICE_NAME=DESARTP))); port=-1; username=czavalet
- transf_AtencionesZeroQ_TDS.ktr: database connection name=OracleJDBC@PRODCAR(AHERMOSI); type=ORACLE; access=Native; database=(DESCRIPTION=(FAILOVER=on)(LOAD_BALANCE=yes)(ADDRESS_LIST=(ADDRESS=(PROTOCOL=TCP)(HOST=lnxdbprod11g-rac1-vip.afphabitat.cl)(PORT=1523))(ADDRESS=(PROTOCOL=TCP)(HOST=lnxdbprod11g-rac2-vip.afphabitat.cl)(PORT=1523)))(CONNECT_DATA=(FAILOVER_MOD; port=-1; username=AHERMOSI
- transf_AtencionesZeroQ_TDS.ktr: database connection name=PostgreSQL_JNDI@JiraLEAN(bigdata); type=POSTGRESQL; access=JNDI; server=atlprdh1.afphabitat.cl; database=LEAN; port=45432
- transf_AtencionesZeroQ_TDS.ktr: database connection name=SampleData; type=HYPERSONIC; access=Native; server=localhost; database=SampleData; port=9001; username=pentaho_user
- transf_AtencionesZeroQ_TDS.ktr: database connection name=SybaseIQ_JDBC@habitat(DMGestion); type=SYBASEIQ; access=Native; server=192.168.10.247; database=habitat; port=2638; username=DMGestion
- transf_AtencionesZeroQ_TDS.ktr: database connection name=SybaseIQ_JNDI@habitat(AFC); type=SYBASEIQ; access=JNDI; server=192.168.10.247; database=AFC; port=2638
- transf_AtencionesZeroQ_TDS.ktr: database connection name=SybaseIQ_JNDI@habitat(Auditoria); type=SYBASEIQ; access=JNDI; database=Auditoria; port=1521
- transf_AtencionesZeroQ_TDS.ktr: database connection name=SybaseIQ_JNDI@habitat(BonoCargoFiscal); type=SYBASEIQ; access=JNDI; database=BonoCargoFiscal; port=1521
- transf_AtencionesZeroQ_TDS.ktr: database connection name=SybaseIQ_JNDI@habitat(Circular119); type=SYBASEIQ; access=JNDI; database=Circular119; port=1521
- transf_AtencionesZeroQ_TDS.ktr: database connection name=SybaseIQ_JNDI@habitat(Circular1509); type=SYBASEIQ; access=JNDI; server=${ServidorSybaseIQ}; database=Circular1509; port=${puerto.SybaseIQ}
- transf_AtencionesZeroQ_TDS.ktr: database connection name=SybaseIQ_JNDI@habitat(Circular1532); type=SYBASEIQ; access=JNDI; database=Circular1532; port=1521
- transf_AtencionesZeroQ_TDS.ktr: database connection name=SybaseIQ_JNDI@habitat(Circular1536); type=SYBASEIQ; access=JNDI; server=${ServidorSybaseIQ}; database=Circular1536; port=${puerto.SybaseIQ}
- transf_AtencionesZeroQ_TDS.ktr: database connection name=SybaseIQ_JNDI@habitat(Circular1661V1); type=SYBASEIQ; access=JNDI; server=${ServidorSybaseIQ}; database=Circular1661V1; port=${puerto.SybaseIQ}
- transf_AtencionesZeroQ_TDS.ktr: database connection name=SybaseIQ_JNDI@habitat(ControlProcesos); type=SYBASEIQ; access=JNDI; database=ControlProcesos; port=1521
- transf_AtencionesZeroQ_TDS.ktr: database connection name=SybaseIQ_JNDI@habitat(Datawarehouse); type=SYBASEIQ; access=JNDI; server=iqprod16; database=Datawarehouse; port=2638
- transf_AtencionesZeroQ_TDS.ktr: database connection name=SybaseIQ_JNDI@habitat(DDS); type=GENERIC; access=JNDI; server=192.168.10.247; database=DDS; port=2638
- transf_AtencionesZeroQ_TDS.ktr: database connection name=SybaseIQ_JNDI@habitat(DMGestion); type=SYBASEIQ; access=JNDI; server=iqprod16; database=DMGestion; port=2638
- transf_AtencionesZeroQ_TDS.ktr: database connection name=SybaseIQ_JNDI@habitat(Interfaz); type=SYBASEIQ; access=JNDI; database=DMGestion; port=1521
- transf_AtencionesZeroQ_TDS.ktr: database connection name=SybaseIQ_JNDI@habitat(LavadoActivos); type=SYBASEIQ; access=JNDI; database=LavadoActivos; port=1521
- transf_AtencionesZeroQ_TDS.ktr: database connection name=SybaseIQ_JNDI@habitat(MAC); type=SYBASEIQ; access=JNDI; server=${ServidorSybaseIQ}; database=MAC; port=${puerto.SybaseIQ}
- transf_AtencionesZeroQ_TDS.ktr: database connection name=SybaseIQ_JNDI@habitat(PAET); type=SYBASEIQ; access=JNDI; database=PAET; port=1521
- transf_AtencionesZeroQ_TDS.ktr: database connection name=SybaseIQ_JNDI@habitat(PowerBI); type=SYBASEIQ; access=JNDI; database=PowerBI; port=1521
- transf_AtencionesZeroQ_TDS.ktr: database connection name=SybaseIQ_JNDI@habitat(Retiro10); type=SYBASEIQ; access=JNDI; database=Retiro10; port=1521
- transf_AtencionesZeroQ_TDS.ktr: database connection name=SybaseIQ_JNDI@habitat(SalesForce); type=SYBASEIQ; access=JNDI; database=DMGestion; port=1521
- transf_AtencionesZeroQ_TDS.ktr: database connection name=SybaseIQ_JNDI@habitat(TDS); type=SYBASEIQ; access=JNDI; database=TDS; port=1521
- transf_AtencionesZeroQ_TDS.ktr: database connection name=testOracle@HABITAT; type=ORACLE; access=Native; database=(DESCRIPTION=(FAILOVER=on)(LOAD_BALANCE=yes)(ADDRESS_LIST=(ADDRESS=(PROTOCOL=TCP)(HOST=habitatvip1.afphabitat.cl)(PORT=1521))(ADDRESS=(PROTOCOL=TCP)(HOST=habitatvip2.afphabitat.cl)(PORT=1521)))(CONNECT_DATA=(FAILOVER_MODE=(TYPE=select)(METH; port=-1; username=datawarehouse
- transf_AtencionesZeroQ_TDS.ktr: database connection name=testOracle@PRODAFP; type=ORACLE; access=Native; database=(DESCRIPTION=(FAILOVER=on)(LOAD_BALANCE=on)(ADDRESS_LIST=(ADDRESS=(PROTOCOL=TCP)(HOST=prodafpvip1.afphabitat.cl)(PORT=1522))(ADDRESS=(PROTOCOL=TCP)(HOST=prodafpvip2.afphabitat.cl)(PORT=1522)))(CONNECT_DATA=(FAILOVER_MODE=(TYPE=select)(METHO; port=-1; username=czavalet
- transf_AtencionesZeroQ_TDS.ktr: database connection name=testSybase@IQProd; type=SYBASEIQ; access=Native; server=192.168.10.247; database=habitat; port=2638; username=DMGestion
- transf_AtencionesZeroQ_TDS.ktr: database connection name=testSybase@IQProd(16.1); type=SYBASEIQ; access=Native; server=192.168.10.32; database=iq_habitat; port=2638; username=DMGestion
- transf_AtencionesZeroQ_TDS.ktr: database connection name=TotalPackV24; type=MSSQL; access=Native; server=NET-SQL01; database=modeltotalpack; port=1433; username=DATAWAREHOUSE
- transf_MotivoAgendamientoZeroQ_TDS.ktr: database connection name=AgileBI; type=MONETDB; access=Native; server=localhost; database=pentaho-instaview; port=50000; username=monetdb
- transf_MotivoAgendamientoZeroQ_TDS.ktr: database connection name=Bonobo; type=MYSQL; access=Native; server=localhost; database=bonobo; port=3306; username=root
- transf_MotivoAgendamientoZeroQ_TDS.ktr: database connection name=cnTower; type=MSSQL; access=Native; server=PDTOWH1; database=WMP_HABITAT; port=1433; username=DATAWAREHOUSE
- transf_MotivoAgendamientoZeroQ_TDS.ktr: database connection name=FUGA; type=ORACLE; access=Native; server=lnxdbplan12c.afphabitat.cl; database=PRODWINV; port=1521; username=fdelcamp[FUGA]
- transf_MotivoAgendamientoZeroQ_TDS.ktr: database connection name=Kettle; type=ORACLE; access=Native; server=192.168.10.63; database=expl10g2; port=1521; username=kettle
- transf_MotivoAgendamientoZeroQ_TDS.ktr: database connection name=MsSQLServer_JNDI@TotalPack(Datawarehouse); type=ORACLE; access=JNDI; database=TotalPack; port=1521
- transf_MotivoAgendamientoZeroQ_TDS.ktr: database connection name=MySQL5; type=MYSQL; access=Native; server=localhost; database=testPentaho; port=3306; username=root
- transf_MotivoAgendamientoZeroQ_TDS.ktr: database connection name=MySQL_JNDI@SGC(Datawarehouse); type=MYSQL; access=JNDI; server=192.168.200.130; database=SGC; port=3306
- transf_MotivoAgendamientoZeroQ_TDS.ktr: database connection name=Oracle_JDBC@DESA_RTP(Datawarehouse); type=ORACLE; access=Native; database=(DESCRIPTION=(FAILOVER=on)(LOAD_BALANCE=yes)(ADDRESS_LIST=(ADDRESS=(PROTOCOL=TCP)(HOST=dbdete10g-rac1.afphabitat.cl)(PORT=1532)))(CONNECT_DATA=(FAILOVER_MODE=(TYPE=select)(METHOD=basic))(SERVER=dedicated)(SERVICE_NAME=DESARTP))); port=-1; username=CZAVALET
- transf_MotivoAgendamientoZeroQ_TDS.ktr: database connection name=Oracle_JDBC@DESA_RTP(IPINCHEI); type=ORACLE; access=Native; database=(DESCRIPTION=(FAILOVER=on)(LOAD_BALANCE=yes)(ADDRESS_LIST=(ADDRESS=(PROTOCOL=TCP)(HOST=dbdete10g-rac1.afphabitat.cl)(PORT=1532)))(CONNECT_DATA=(FAILOVER_MODE=(TYPE=select)(METHOD=basic))(SERVER=dedicated)(SERVICE_NAME=DESARTP))); port=-1; username=ipinchei[exp_enfermoterminal]
- transf_MotivoAgendamientoZeroQ_TDS.ktr: database connection name=Oracle_JNDI@DESA_RTP(IPINCHEI); type=ORACLE; access=Native; database=(DESCRIPTION=(FAILOVER=on)(LOAD_BALANCE=yes)(ADDRESS_LIST=(ADDRESS=(PROTOCOL=TCP)(HOST=dbdete10g-rac1.afphabitat.cl)(PORT=1532)))(CONNECT_DATA=(FAILOVER_MODE=(TYPE=select)(METHOD=basic))(SERVER=dedicated)(SERVICE_NAME=DESARTP))); port=-1; username=ipinchei[exp_enfermoterminal]
- transf_MotivoAgendamientoZeroQ_TDS.ktr: database connection name=Oracle_JNDI@DOCUWARE(Datawarehouse); type=ORACLE; access=JNDI; database=DOCUWARE; port=1521
- transf_MotivoAgendamientoZeroQ_TDS.ktr: database connection name=Oracle_JNDI@EXPL10G2(Datawarehouse); type=ORACLE; access=JNDI; server=192.168.10.63; database=EXPL10G2; port=1521
- transf_MotivoAgendamientoZeroQ_TDS.ktr: database connection name=Oracle_JNDI@FINPRD(Datawarehouse); type=ORACLE; access=JNDI; database=FINPRD; port=1521
- transf_MotivoAgendamientoZeroQ_TDS.ktr: database connection name=Oracle_JNDI@HABITAT(Cierre_Mes); type=ORACLE; access=JNDI; server=${ServidorCierreMes}; database=CIERRE_MES; port=${puerto.base.Oracle}
- transf_MotivoAgendamientoZeroQ_TDS.ktr: database connection name=Oracle_JNDI@PRDINV(Datawarehouse); type=ORACLE; access=JNDI; database=PRDINV; port=1521
- transf_MotivoAgendamientoZeroQ_TDS.ktr: database connection name=Oracle_JNDI@PROD11G(Datawarehouse); type=ORACLE; access=JNDI; database=PROD11G; port=-1
- transf_MotivoAgendamientoZeroQ_TDS.ktr: database connection name=Oracle_JNDI@PRODAFP(Datawarehouse); type=ORACLE; access=JNDI; database=PRODAFP; port=1521
- transf_MotivoAgendamientoZeroQ_TDS.ktr: database connection name=Oracle_JNDI@PRODWINV(Datawarehouse); type=ORACLE; access=JNDI; server=lnxdbplan12c.afphabitat.cl; database=PRODWINV; port=1521
- transf_MotivoAgendamientoZeroQ_TDS.ktr: database connection name=Oracle_JNDI@RTCHabitat(Datawarehouse); type=ORACLE; access=JNDI; server=qa-rac2-vip.afphabitat.cl; database=RTCHabitat; port=1521
- transf_MotivoAgendamientoZeroQ_TDS.ktr: database connection name=OracleJDBC@CERTRTC(Datawarehouse); type=ORACLE; access=Native; database=(DESCRIPTION=(FAILOVER=on)(LOAD_BALANCE=yes)(ADDRESS_LIST=(ADDRESS=(PROTOCOL=TCP)(HOST=dbcert10g-rac1-vip)(PORT=1531))(ADDRESS=(PROTOCOL=TCP)(HOST=dbcert10g-rac2-vip)(PORT=1531)))(CONNECT_DATA=(FAILOVER_MODE=(TYPE=select)(METHOD=basic))(SER; port=-1; username=DATAWAREHOUSE
- transf_MotivoAgendamientoZeroQ_TDS.ktr: database connection name=OracleJDBC@CERTRTP(Datawarehouse); type=ORACLE; access=Native; database=(DESCRIPTION=(FAILOVER=on)(LOAD_BALANCE=yes)(ADDRESS_LIST=(ADDRESS=(PROTOCOL=TCP)(HOST=dbcert10g-rac1-vip)(PORT=1532)))(CONNECT_DATA=(FAILOVER_MODE=(TYPE=select)(METHOD=basic))(SERVER=dedicated)(SERVICE_NAME=CERTRTP))); port=-1; username=datawarehouse
- transf_MotivoAgendamientoZeroQ_TDS.ktr: database connection name=OracleJDBC@DESARTC(Datawarehouse); type=ORACLE; access=Native; database=(DESCRIPTION=(FAILOVER=on)(LOAD_BALANCE=yes)(ADDRESS_LIST=(ADDRESS=(PROTOCOL=TCP)(HOST=dbdete10g-rac1.afphabitat.cl)(PORT=1531)))(CONNECT_DATA=(FAILOVER_MODE=(TYPE=select)(METHOD=basic))(SERVER=dedicated)(SERVICE_NAME=DESARTC))); port=-1; username=CZAVALET
- transf_MotivoAgendamientoZeroQ_TDS.ktr: database connection name=OracleJDBC@DESARTP(Datawarehouse); type=ORACLE; access=Native; database=(DESCRIPTION=(FAILOVER=on)(LOAD_BALANCE=yes)(ADDRESS_LIST=(ADDRESS=(PROTOCOL=TCP)(HOST=dbdete10g-rac1.afphabitat.cl)(PORT=1532)))(CONNECT_DATA=(FAILOVER_MODE=(TYPE=select)(METHOD=basic))(SERVER=dedicated)(SERVICE_NAME=DESARTP))); port=-1; username=czavalet
- transf_MotivoAgendamientoZeroQ_TDS.ktr: database connection name=OracleJDBC@DESARTP(OWN_TRIBUTARIO); type=ORACLE; access=Native; database=(DESCRIPTION=(FAILOVER=on)(LOAD_BALANCE=yes)(ADDRESS_LIST=(ADDRESS=(PROTOCOL=TCP)(HOST=dbdete10g-rac1.afphabitat.cl)(PORT=1532)))(CONNECT_DATA=(FAILOVER_MODE=(TYPE=select)(METHOD=basic))(SERVER=dedicated)(SERVICE_NAME=DESARTP))); port=-1; username=czavalet
- transf_MotivoAgendamientoZeroQ_TDS.ktr: database connection name=OracleJDBC@PRODCAR(AHERMOSI); type=ORACLE; access=Native; database=(DESCRIPTION=(FAILOVER=on)(LOAD_BALANCE=yes)(ADDRESS_LIST=(ADDRESS=(PROTOCOL=TCP)(HOST=lnxdbprod11g-rac1-vip.afphabitat.cl)(PORT=1523))(ADDRESS=(PROTOCOL=TCP)(HOST=lnxdbprod11g-rac2-vip.afphabitat.cl)(PORT=1523)))(CONNECT_DATA=(FAILOVER_MOD; port=-1; username=AHERMOSI
- transf_MotivoAgendamientoZeroQ_TDS.ktr: database connection name=PostgreSQL_JNDI@JiraLEAN(bigdata); type=POSTGRESQL; access=JNDI; server=atlprdh1.afphabitat.cl; database=LEAN; port=45432
- transf_MotivoAgendamientoZeroQ_TDS.ktr: database connection name=SampleData; type=HYPERSONIC; access=Native; server=localhost; database=SampleData; port=9001; username=pentaho_user
- transf_MotivoAgendamientoZeroQ_TDS.ktr: database connection name=SybaseIQ_JDBC@habitat(DMGestion); type=SYBASEIQ; access=Native; server=192.168.10.247; database=habitat; port=2638; username=DMGestion
- transf_MotivoAgendamientoZeroQ_TDS.ktr: database connection name=SybaseIQ_JNDI@habitat(AFC); type=SYBASEIQ; access=JNDI; server=192.168.10.247; database=AFC; port=2638
- transf_MotivoAgendamientoZeroQ_TDS.ktr: database connection name=SybaseIQ_JNDI@habitat(Auditoria); type=SYBASEIQ; access=JNDI; database=Auditoria; port=1521
- transf_MotivoAgendamientoZeroQ_TDS.ktr: database connection name=SybaseIQ_JNDI@habitat(BonoCargoFiscal); type=SYBASEIQ; access=JNDI; database=BonoCargoFiscal; port=1521
- transf_MotivoAgendamientoZeroQ_TDS.ktr: database connection name=SybaseIQ_JNDI@habitat(Circular119); type=SYBASEIQ; access=JNDI; database=Circular119; port=1521
- transf_MotivoAgendamientoZeroQ_TDS.ktr: database connection name=SybaseIQ_JNDI@habitat(Circular1509); type=SYBASEIQ; access=JNDI; server=${ServidorSybaseIQ}; database=Circular1509; port=${puerto.SybaseIQ}
- transf_MotivoAgendamientoZeroQ_TDS.ktr: database connection name=SybaseIQ_JNDI@habitat(Circular1532); type=SYBASEIQ; access=JNDI; database=Circular1532; port=1521
- transf_MotivoAgendamientoZeroQ_TDS.ktr: database connection name=SybaseIQ_JNDI@habitat(Circular1536); type=SYBASEIQ; access=JNDI; server=${ServidorSybaseIQ}; database=Circular1536; port=${puerto.SybaseIQ}
- transf_MotivoAgendamientoZeroQ_TDS.ktr: database connection name=SybaseIQ_JNDI@habitat(Circular1661V1); type=SYBASEIQ; access=JNDI; server=${ServidorSybaseIQ}; database=Circular1661V1; port=${puerto.SybaseIQ}
- transf_MotivoAgendamientoZeroQ_TDS.ktr: database connection name=SybaseIQ_JNDI@habitat(ControlProcesos); type=SYBASEIQ; access=JNDI; database=ControlProcesos; port=1521
- transf_MotivoAgendamientoZeroQ_TDS.ktr: database connection name=SybaseIQ_JNDI@habitat(Datawarehouse); type=SYBASEIQ; access=JNDI; server=iqprod16; database=Datawarehouse; port=2638
- transf_MotivoAgendamientoZeroQ_TDS.ktr: database connection name=SybaseIQ_JNDI@habitat(DDS); type=GENERIC; access=JNDI; server=192.168.10.247; database=DDS; port=2638
- transf_MotivoAgendamientoZeroQ_TDS.ktr: database connection name=SybaseIQ_JNDI@habitat(DMGestion); type=SYBASEIQ; access=JNDI; server=iqprod16; database=DMGestion; port=2638
- transf_MotivoAgendamientoZeroQ_TDS.ktr: database connection name=SybaseIQ_JNDI@habitat(Interfaz); type=SYBASEIQ; access=JNDI; database=DMGestion; port=1521
- transf_MotivoAgendamientoZeroQ_TDS.ktr: database connection name=SybaseIQ_JNDI@habitat(LavadoActivos); type=SYBASEIQ; access=JNDI; database=LavadoActivos; port=1521
- transf_MotivoAgendamientoZeroQ_TDS.ktr: database connection name=SybaseIQ_JNDI@habitat(MAC); type=SYBASEIQ; access=JNDI; server=${ServidorSybaseIQ}; database=MAC; port=${puerto.SybaseIQ}
- transf_MotivoAgendamientoZeroQ_TDS.ktr: database connection name=SybaseIQ_JNDI@habitat(PAET); type=SYBASEIQ; access=JNDI; database=PAET; port=1521
- transf_MotivoAgendamientoZeroQ_TDS.ktr: database connection name=SybaseIQ_JNDI@habitat(PowerBI); type=SYBASEIQ; access=JNDI; database=PowerBI; port=1521
- transf_MotivoAgendamientoZeroQ_TDS.ktr: database connection name=SybaseIQ_JNDI@habitat(Retiro10); type=SYBASEIQ; access=JNDI; database=Retiro10; port=1521
- transf_MotivoAgendamientoZeroQ_TDS.ktr: database connection name=SybaseIQ_JNDI@habitat(SalesForce); type=SYBASEIQ; access=JNDI; database=DMGestion; port=1521
- transf_MotivoAgendamientoZeroQ_TDS.ktr: database connection name=SybaseIQ_JNDI@habitat(TDS); type=SYBASEIQ; access=JNDI; database=TDS; port=1521
- transf_MotivoAgendamientoZeroQ_TDS.ktr: database connection name=testOracle@HABITAT; type=ORACLE; access=Native; database=(DESCRIPTION=(FAILOVER=on)(LOAD_BALANCE=yes)(ADDRESS_LIST=(ADDRESS=(PROTOCOL=TCP)(HOST=habitatvip1.afphabitat.cl)(PORT=1521))(ADDRESS=(PROTOCOL=TCP)(HOST=habitatvip2.afphabitat.cl)(PORT=1521)))(CONNECT_DATA=(FAILOVER_MODE=(TYPE=select)(METH; port=-1; username=datawarehouse
- transf_MotivoAgendamientoZeroQ_TDS.ktr: database connection name=testOracle@PRODAFP; type=ORACLE; access=Native; database=(DESCRIPTION=(FAILOVER=on)(LOAD_BALANCE=on)(ADDRESS_LIST=(ADDRESS=(PROTOCOL=TCP)(HOST=prodafpvip1.afphabitat.cl)(PORT=1522))(ADDRESS=(PROTOCOL=TCP)(HOST=prodafpvip2.afphabitat.cl)(PORT=1522)))(CONNECT_DATA=(FAILOVER_MODE=(TYPE=select)(METHO; port=-1; username=czavalet
- transf_MotivoAgendamientoZeroQ_TDS.ktr: database connection name=testSybase@IQProd; type=SYBASEIQ; access=Native; server=192.168.10.247; database=habitat; port=2638; username=DMGestion
- transf_MotivoAgendamientoZeroQ_TDS.ktr: database connection name=testSybase@IQProd(16.1); type=SYBASEIQ; access=Native; server=192.168.10.32; database=iq_habitat; port=2638; username=DMGestion
- transf_MotivoAgendamientoZeroQ_TDS.ktr: database connection name=TotalPackV24; type=MSSQL; access=Native; server=NET-SQL01; database=modeltotalpack; port=1433; username=DATAWAREHOUSE
- transf_MotivoAtencionZeroQ_TDS.ktr: database connection name=AgileBI; type=MONETDB; access=Native; server=localhost; database=pentaho-instaview; port=50000; username=monetdb
- transf_MotivoAtencionZeroQ_TDS.ktr: database connection name=Bonobo; type=MYSQL; access=Native; server=localhost; database=bonobo; port=3306; username=root
- transf_MotivoAtencionZeroQ_TDS.ktr: database connection name=cnTower; type=MSSQL; access=Native; server=PDTOWH1; database=WMP_HABITAT; port=1433; username=DATAWAREHOUSE
- transf_MotivoAtencionZeroQ_TDS.ktr: database connection name=FUGA; type=ORACLE; access=Native; server=lnxdbplan12c.afphabitat.cl; database=PRODWINV; port=1521; username=fdelcamp[FUGA]
- transf_MotivoAtencionZeroQ_TDS.ktr: database connection name=Kettle; type=ORACLE; access=Native; server=192.168.10.63; database=expl10g2; port=1521; username=kettle
- transf_MotivoAtencionZeroQ_TDS.ktr: database connection name=MsSQLServer_JNDI@TotalPack(Datawarehouse); type=ORACLE; access=JNDI; database=TotalPack; port=1521
- transf_MotivoAtencionZeroQ_TDS.ktr: database connection name=MySQL5; type=MYSQL; access=Native; server=localhost; database=testPentaho; port=3306; username=root
- transf_MotivoAtencionZeroQ_TDS.ktr: database connection name=MySQL_JNDI@SGC(Datawarehouse); type=MYSQL; access=JNDI; server=192.168.200.130; database=SGC; port=3306
- transf_MotivoAtencionZeroQ_TDS.ktr: database connection name=Oracle_JDBC@DESA_RTP(Datawarehouse); type=ORACLE; access=Native; database=(DESCRIPTION=(FAILOVER=on)(LOAD_BALANCE=yes)(ADDRESS_LIST=(ADDRESS=(PROTOCOL=TCP)(HOST=dbdete10g-rac1.afphabitat.cl)(PORT=1532)))(CONNECT_DATA=(FAILOVER_MODE=(TYPE=select)(METHOD=basic))(SERVER=dedicated)(SERVICE_NAME=DESARTP))); port=-1; username=CZAVALET
- transf_MotivoAtencionZeroQ_TDS.ktr: database connection name=Oracle_JDBC@DESA_RTP(IPINCHEI); type=ORACLE; access=Native; database=(DESCRIPTION=(FAILOVER=on)(LOAD_BALANCE=yes)(ADDRESS_LIST=(ADDRESS=(PROTOCOL=TCP)(HOST=dbdete10g-rac1.afphabitat.cl)(PORT=1532)))(CONNECT_DATA=(FAILOVER_MODE=(TYPE=select)(METHOD=basic))(SERVER=dedicated)(SERVICE_NAME=DESARTP))); port=-1; username=ipinchei[exp_enfermoterminal]
- transf_MotivoAtencionZeroQ_TDS.ktr: database connection name=Oracle_JNDI@DESA_RTP(IPINCHEI); type=ORACLE; access=Native; database=(DESCRIPTION=(FAILOVER=on)(LOAD_BALANCE=yes)(ADDRESS_LIST=(ADDRESS=(PROTOCOL=TCP)(HOST=dbdete10g-rac1.afphabitat.cl)(PORT=1532)))(CONNECT_DATA=(FAILOVER_MODE=(TYPE=select)(METHOD=basic))(SERVER=dedicated)(SERVICE_NAME=DESARTP))); port=-1; username=ipinchei[exp_enfermoterminal]
- transf_MotivoAtencionZeroQ_TDS.ktr: database connection name=Oracle_JNDI@DOCUWARE(Datawarehouse); type=ORACLE; access=JNDI; database=DOCUWARE; port=1521
- transf_MotivoAtencionZeroQ_TDS.ktr: database connection name=Oracle_JNDI@EXPL10G2(Datawarehouse); type=ORACLE; access=JNDI; server=192.168.10.63; database=EXPL10G2; port=1521
- transf_MotivoAtencionZeroQ_TDS.ktr: database connection name=Oracle_JNDI@FINPRD(Datawarehouse); type=ORACLE; access=JNDI; database=FINPRD; port=1521
- transf_MotivoAtencionZeroQ_TDS.ktr: database connection name=Oracle_JNDI@HABITAT(Cierre_Mes); type=ORACLE; access=JNDI; server=${ServidorCierreMes}; database=CIERRE_MES; port=${puerto.base.Oracle}
- transf_MotivoAtencionZeroQ_TDS.ktr: database connection name=Oracle_JNDI@PRDINV(Datawarehouse); type=ORACLE; access=JNDI; database=PRDINV; port=1521
- transf_MotivoAtencionZeroQ_TDS.ktr: database connection name=Oracle_JNDI@PROD11G(Datawarehouse); type=ORACLE; access=JNDI; database=PROD11G; port=-1
- transf_MotivoAtencionZeroQ_TDS.ktr: database connection name=Oracle_JNDI@PRODAFP(Datawarehouse); type=ORACLE; access=JNDI; database=PRODAFP; port=1521
- transf_MotivoAtencionZeroQ_TDS.ktr: database connection name=Oracle_JNDI@PRODWINV(Datawarehouse); type=ORACLE; access=JNDI; server=lnxdbplan12c.afphabitat.cl; database=PRODWINV; port=1521
- transf_MotivoAtencionZeroQ_TDS.ktr: database connection name=Oracle_JNDI@RTCHabitat(Datawarehouse); type=ORACLE; access=JNDI; server=qa-rac2-vip.afphabitat.cl; database=RTCHabitat; port=1521
- transf_MotivoAtencionZeroQ_TDS.ktr: database connection name=OracleJDBC@CERTRTC(Datawarehouse); type=ORACLE; access=Native; database=(DESCRIPTION=(FAILOVER=on)(LOAD_BALANCE=yes)(ADDRESS_LIST=(ADDRESS=(PROTOCOL=TCP)(HOST=dbcert10g-rac1-vip)(PORT=1531))(ADDRESS=(PROTOCOL=TCP)(HOST=dbcert10g-rac2-vip)(PORT=1531)))(CONNECT_DATA=(FAILOVER_MODE=(TYPE=select)(METHOD=basic))(SER; port=-1; username=DATAWAREHOUSE
- transf_MotivoAtencionZeroQ_TDS.ktr: database connection name=OracleJDBC@CERTRTP(Datawarehouse); type=ORACLE; access=Native; database=(DESCRIPTION=(FAILOVER=on)(LOAD_BALANCE=yes)(ADDRESS_LIST=(ADDRESS=(PROTOCOL=TCP)(HOST=dbcert10g-rac1-vip)(PORT=1532)))(CONNECT_DATA=(FAILOVER_MODE=(TYPE=select)(METHOD=basic))(SERVER=dedicated)(SERVICE_NAME=CERTRTP))); port=-1; username=datawarehouse
- transf_MotivoAtencionZeroQ_TDS.ktr: database connection name=OracleJDBC@DESARTC(Datawarehouse); type=ORACLE; access=Native; database=(DESCRIPTION=(FAILOVER=on)(LOAD_BALANCE=yes)(ADDRESS_LIST=(ADDRESS=(PROTOCOL=TCP)(HOST=dbdete10g-rac1.afphabitat.cl)(PORT=1531)))(CONNECT_DATA=(FAILOVER_MODE=(TYPE=select)(METHOD=basic))(SERVER=dedicated)(SERVICE_NAME=DESARTC))); port=-1; username=CZAVALET
- transf_MotivoAtencionZeroQ_TDS.ktr: database connection name=OracleJDBC@DESARTP(Datawarehouse); type=ORACLE; access=Native; database=(DESCRIPTION=(FAILOVER=on)(LOAD_BALANCE=yes)(ADDRESS_LIST=(ADDRESS=(PROTOCOL=TCP)(HOST=dbdete10g-rac1.afphabitat.cl)(PORT=1532)))(CONNECT_DATA=(FAILOVER_MODE=(TYPE=select)(METHOD=basic))(SERVER=dedicated)(SERVICE_NAME=DESARTP))); port=-1; username=czavalet
- transf_MotivoAtencionZeroQ_TDS.ktr: database connection name=OracleJDBC@DESARTP(OWN_TRIBUTARIO); type=ORACLE; access=Native; database=(DESCRIPTION=(FAILOVER=on)(LOAD_BALANCE=yes)(ADDRESS_LIST=(ADDRESS=(PROTOCOL=TCP)(HOST=dbdete10g-rac1.afphabitat.cl)(PORT=1532)))(CONNECT_DATA=(FAILOVER_MODE=(TYPE=select)(METHOD=basic))(SERVER=dedicated)(SERVICE_NAME=DESARTP))); port=-1; username=czavalet
- transf_MotivoAtencionZeroQ_TDS.ktr: database connection name=OracleJDBC@PRODCAR(AHERMOSI); type=ORACLE; access=Native; database=(DESCRIPTION=(FAILOVER=on)(LOAD_BALANCE=yes)(ADDRESS_LIST=(ADDRESS=(PROTOCOL=TCP)(HOST=lnxdbprod11g-rac1-vip.afphabitat.cl)(PORT=1523))(ADDRESS=(PROTOCOL=TCP)(HOST=lnxdbprod11g-rac2-vip.afphabitat.cl)(PORT=1523)))(CONNECT_DATA=(FAILOVER_MOD; port=-1; username=AHERMOSI
- transf_MotivoAtencionZeroQ_TDS.ktr: database connection name=PostgreSQL_JNDI@JiraLEAN(bigdata); type=POSTGRESQL; access=JNDI; server=atlprdh1.afphabitat.cl; database=LEAN; port=45432
- transf_MotivoAtencionZeroQ_TDS.ktr: database connection name=SampleData; type=HYPERSONIC; access=Native; server=localhost; database=SampleData; port=9001; username=pentaho_user
- transf_MotivoAtencionZeroQ_TDS.ktr: database connection name=SybaseIQ_JDBC@habitat(DMGestion); type=SYBASEIQ; access=Native; server=192.168.10.247; database=habitat; port=2638; username=DMGestion
- transf_MotivoAtencionZeroQ_TDS.ktr: database connection name=SybaseIQ_JNDI@habitat(AFC); type=SYBASEIQ; access=JNDI; server=192.168.10.247; database=AFC; port=2638
- transf_MotivoAtencionZeroQ_TDS.ktr: database connection name=SybaseIQ_JNDI@habitat(Auditoria); type=SYBASEIQ; access=JNDI; database=Auditoria; port=1521
- transf_MotivoAtencionZeroQ_TDS.ktr: database connection name=SybaseIQ_JNDI@habitat(BonoCargoFiscal); type=SYBASEIQ; access=JNDI; database=BonoCargoFiscal; port=1521
- transf_MotivoAtencionZeroQ_TDS.ktr: database connection name=SybaseIQ_JNDI@habitat(Circular119); type=SYBASEIQ; access=JNDI; database=Circular119; port=1521
- transf_MotivoAtencionZeroQ_TDS.ktr: database connection name=SybaseIQ_JNDI@habitat(Circular1509); type=SYBASEIQ; access=JNDI; server=${ServidorSybaseIQ}; database=Circular1509; port=${puerto.SybaseIQ}
- transf_MotivoAtencionZeroQ_TDS.ktr: database connection name=SybaseIQ_JNDI@habitat(Circular1532); type=SYBASEIQ; access=JNDI; database=Circular1532; port=1521
- transf_MotivoAtencionZeroQ_TDS.ktr: database connection name=SybaseIQ_JNDI@habitat(Circular1536); type=SYBASEIQ; access=JNDI; server=${ServidorSybaseIQ}; database=Circular1536; port=${puerto.SybaseIQ}
- transf_MotivoAtencionZeroQ_TDS.ktr: database connection name=SybaseIQ_JNDI@habitat(Circular1661V1); type=SYBASEIQ; access=JNDI; server=${ServidorSybaseIQ}; database=Circular1661V1; port=${puerto.SybaseIQ}
- transf_MotivoAtencionZeroQ_TDS.ktr: database connection name=SybaseIQ_JNDI@habitat(ControlProcesos); type=SYBASEIQ; access=JNDI; database=ControlProcesos; port=1521
- transf_MotivoAtencionZeroQ_TDS.ktr: database connection name=SybaseIQ_JNDI@habitat(Datawarehouse); type=SYBASEIQ; access=JNDI; server=iqprod16; database=Datawarehouse; port=2638
- transf_MotivoAtencionZeroQ_TDS.ktr: database connection name=SybaseIQ_JNDI@habitat(DDS); type=GENERIC; access=JNDI; server=192.168.10.247; database=DDS; port=2638
- transf_MotivoAtencionZeroQ_TDS.ktr: database connection name=SybaseIQ_JNDI@habitat(DMGestion); type=SYBASEIQ; access=JNDI; server=iqprod16; database=DMGestion; port=2638
- transf_MotivoAtencionZeroQ_TDS.ktr: database connection name=SybaseIQ_JNDI@habitat(Interfaz); type=SYBASEIQ; access=JNDI; database=DMGestion; port=1521
- transf_MotivoAtencionZeroQ_TDS.ktr: database connection name=SybaseIQ_JNDI@habitat(LavadoActivos); type=SYBASEIQ; access=JNDI; database=LavadoActivos; port=1521
- transf_MotivoAtencionZeroQ_TDS.ktr: database connection name=SybaseIQ_JNDI@habitat(MAC); type=SYBASEIQ; access=JNDI; server=${ServidorSybaseIQ}; database=MAC; port=${puerto.SybaseIQ}
- transf_MotivoAtencionZeroQ_TDS.ktr: database connection name=SybaseIQ_JNDI@habitat(PAET); type=SYBASEIQ; access=JNDI; database=PAET; port=1521
- transf_MotivoAtencionZeroQ_TDS.ktr: database connection name=SybaseIQ_JNDI@habitat(PowerBI); type=SYBASEIQ; access=JNDI; database=PowerBI; port=1521
- transf_MotivoAtencionZeroQ_TDS.ktr: database connection name=SybaseIQ_JNDI@habitat(Retiro10); type=SYBASEIQ; access=JNDI; database=Retiro10; port=1521
- transf_MotivoAtencionZeroQ_TDS.ktr: database connection name=SybaseIQ_JNDI@habitat(SalesForce); type=SYBASEIQ; access=JNDI; database=DMGestion; port=1521
- transf_MotivoAtencionZeroQ_TDS.ktr: database connection name=SybaseIQ_JNDI@habitat(TDS); type=SYBASEIQ; access=JNDI; database=TDS; port=1521
- transf_MotivoAtencionZeroQ_TDS.ktr: database connection name=testOracle@HABITAT; type=ORACLE; access=Native; database=(DESCRIPTION=(FAILOVER=on)(LOAD_BALANCE=yes)(ADDRESS_LIST=(ADDRESS=(PROTOCOL=TCP)(HOST=habitatvip1.afphabitat.cl)(PORT=1521))(ADDRESS=(PROTOCOL=TCP)(HOST=habitatvip2.afphabitat.cl)(PORT=1521)))(CONNECT_DATA=(FAILOVER_MODE=(TYPE=select)(METH; port=-1; username=datawarehouse
- transf_MotivoAtencionZeroQ_TDS.ktr: database connection name=testOracle@PRODAFP; type=ORACLE; access=Native; database=(DESCRIPTION=(FAILOVER=on)(LOAD_BALANCE=on)(ADDRESS_LIST=(ADDRESS=(PROTOCOL=TCP)(HOST=prodafpvip1.afphabitat.cl)(PORT=1522))(ADDRESS=(PROTOCOL=TCP)(HOST=prodafpvip2.afphabitat.cl)(PORT=1522)))(CONNECT_DATA=(FAILOVER_MODE=(TYPE=select)(METHO; port=-1; username=czavalet
- transf_MotivoAtencionZeroQ_TDS.ktr: database connection name=testSybase@IQProd; type=SYBASEIQ; access=Native; server=192.168.10.247; database=habitat; port=2638; username=DMGestion
- transf_MotivoAtencionZeroQ_TDS.ktr: database connection name=testSybase@IQProd(16.1); type=SYBASEIQ; access=Native; server=192.168.10.32; database=iq_habitat; port=2638; username=DMGestion
- transf_MotivoAtencionZeroQ_TDS.ktr: database connection name=TotalPackV24; type=MSSQL; access=Native; server=NET-SQL01; database=modeltotalpack; port=1433; username=DATAWAREHOUSE
- transf_obtenerPeriodoExtraer.ktr: database connection name=AgileBI; type=MONETDB; access=Native; server=localhost; database=pentaho-instaview; port=50000; username=monetdb
- transf_obtenerPeriodoExtraer.ktr: database connection name=Bonobo; type=MYSQL; access=Native; server=localhost; database=bonobo; port=3306; username=root
- transf_obtenerPeriodoExtraer.ktr: database connection name=cnTower; type=MSSQL; access=Native; server=PDTOWH1; database=WMP_HABITAT; port=1433; username=DATAWAREHOUSE
- transf_obtenerPeriodoExtraer.ktr: database connection name=FUGA; type=ORACLE; access=Native; server=lnxdbplan12c.afphabitat.cl; database=PRODWINV; port=1521; username=fdelcamp[FUGA]
- transf_obtenerPeriodoExtraer.ktr: database connection name=Kettle; type=ORACLE; access=Native; server=192.168.10.63; database=expl10g2; port=1521; username=kettle
- transf_obtenerPeriodoExtraer.ktr: database connection name=MsSQLServer_JNDI@TotalPack(Datawarehouse); type=ORACLE; access=JNDI; database=TotalPack; port=1521
- transf_obtenerPeriodoExtraer.ktr: database connection name=MySQL5; type=MYSQL; access=Native; server=localhost; database=testPentaho; port=3306; username=root
- transf_obtenerPeriodoExtraer.ktr: database connection name=MySQL_JNDI@SGC(Datawarehouse); type=MYSQL; access=JNDI; server=192.168.200.130; database=SGC; port=3306
- transf_obtenerPeriodoExtraer.ktr: database connection name=Oracle_JDBC@DESA_RTP(Datawarehouse); type=ORACLE; access=Native; database=(DESCRIPTION=(FAILOVER=on)(LOAD_BALANCE=yes)(ADDRESS_LIST=(ADDRESS=(PROTOCOL=TCP)(HOST=dbdete10g-rac1.afphabitat.cl)(PORT=1532)))(CONNECT_DATA=(FAILOVER_MODE=(TYPE=select)(METHOD=basic))(SERVER=dedicated)(SERVICE_NAME=DESARTP))); port=-1; username=CZAVALET
- transf_obtenerPeriodoExtraer.ktr: database connection name=Oracle_JDBC@DESA_RTP(IPINCHEI); type=ORACLE; access=Native; database=(DESCRIPTION=(FAILOVER=on)(LOAD_BALANCE=yes)(ADDRESS_LIST=(ADDRESS=(PROTOCOL=TCP)(HOST=dbdete10g-rac1.afphabitat.cl)(PORT=1532)))(CONNECT_DATA=(FAILOVER_MODE=(TYPE=select)(METHOD=basic))(SERVER=dedicated)(SERVICE_NAME=DESARTP))); port=-1; username=ipinchei[exp_enfermoterminal]
- transf_obtenerPeriodoExtraer.ktr: database connection name=Oracle_JNDI@DESA_RTP(IPINCHEI); type=ORACLE; access=Native; database=(DESCRIPTION=(FAILOVER=on)(LOAD_BALANCE=yes)(ADDRESS_LIST=(ADDRESS=(PROTOCOL=TCP)(HOST=dbdete10g-rac1.afphabitat.cl)(PORT=1532)))(CONNECT_DATA=(FAILOVER_MODE=(TYPE=select)(METHOD=basic))(SERVER=dedicated)(SERVICE_NAME=DESARTP))); port=-1; username=ipinchei[exp_enfermoterminal]
- transf_obtenerPeriodoExtraer.ktr: database connection name=Oracle_JNDI@DOCUWARE(Datawarehouse); type=ORACLE; access=JNDI; database=DOCUWARE; port=1521
- transf_obtenerPeriodoExtraer.ktr: database connection name=Oracle_JNDI@EXPL10G2(Datawarehouse); type=ORACLE; access=JNDI; server=192.168.10.63; database=EXPL10G2; port=1521
- transf_obtenerPeriodoExtraer.ktr: database connection name=Oracle_JNDI@FINPRD(Datawarehouse); type=ORACLE; access=JNDI; database=FINPRD; port=1521
- transf_obtenerPeriodoExtraer.ktr: database connection name=Oracle_JNDI@HABITAT(Cierre_Mes); type=ORACLE; access=JNDI; server=${ServidorCierreMes}; database=CIERRE_MES; port=${puerto.base.Oracle}
- transf_obtenerPeriodoExtraer.ktr: database connection name=Oracle_JNDI@PRDINV(Datawarehouse); type=ORACLE; access=JNDI; database=PRDINV; port=1521
- transf_obtenerPeriodoExtraer.ktr: database connection name=Oracle_JNDI@PROD11G(Datawarehouse); type=ORACLE; access=JNDI; database=PROD11G; port=-1
- transf_obtenerPeriodoExtraer.ktr: database connection name=Oracle_JNDI@PRODAFP(Datawarehouse); type=ORACLE; access=JNDI; database=PRODAFP; port=1521
- transf_obtenerPeriodoExtraer.ktr: database connection name=Oracle_JNDI@PRODWINV(Datawarehouse); type=ORACLE; access=JNDI; server=lnxdbplan12c.afphabitat.cl; database=PRODWINV; port=1521
- transf_obtenerPeriodoExtraer.ktr: database connection name=Oracle_JNDI@RTCHabitat(Datawarehouse); type=ORACLE; access=JNDI; server=qa-rac2-vip.afphabitat.cl; database=RTCHabitat; port=1521
- transf_obtenerPeriodoExtraer.ktr: database connection name=OracleJDBC@CERTRTC(Datawarehouse); type=ORACLE; access=Native; database=(DESCRIPTION=(FAILOVER=on)(LOAD_BALANCE=yes)(ADDRESS_LIST=(ADDRESS=(PROTOCOL=TCP)(HOST=dbcert10g-rac1-vip)(PORT=1531))(ADDRESS=(PROTOCOL=TCP)(HOST=dbcert10g-rac2-vip)(PORT=1531)))(CONNECT_DATA=(FAILOVER_MODE=(TYPE=select)(METHOD=basic))(SER; port=-1; username=DATAWAREHOUSE
- transf_obtenerPeriodoExtraer.ktr: database connection name=OracleJDBC@CERTRTP(Datawarehouse); type=ORACLE; access=Native; database=(DESCRIPTION=(FAILOVER=on)(LOAD_BALANCE=yes)(ADDRESS_LIST=(ADDRESS=(PROTOCOL=TCP)(HOST=dbcert10g-rac1-vip)(PORT=1532)))(CONNECT_DATA=(FAILOVER_MODE=(TYPE=select)(METHOD=basic))(SERVER=dedicated)(SERVICE_NAME=CERTRTP))); port=-1; username=datawarehouse
- transf_obtenerPeriodoExtraer.ktr: database connection name=OracleJDBC@DESARTC(Datawarehouse); type=ORACLE; access=Native; database=(DESCRIPTION=(FAILOVER=on)(LOAD_BALANCE=yes)(ADDRESS_LIST=(ADDRESS=(PROTOCOL=TCP)(HOST=dbdete10g-rac1.afphabitat.cl)(PORT=1531)))(CONNECT_DATA=(FAILOVER_MODE=(TYPE=select)(METHOD=basic))(SERVER=dedicated)(SERVICE_NAME=DESARTC))); port=-1; username=CZAVALET
- transf_obtenerPeriodoExtraer.ktr: database connection name=OracleJDBC@DESARTP(Datawarehouse); type=ORACLE; access=Native; database=(DESCRIPTION=(FAILOVER=on)(LOAD_BALANCE=yes)(ADDRESS_LIST=(ADDRESS=(PROTOCOL=TCP)(HOST=dbdete10g-rac1.afphabitat.cl)(PORT=1532)))(CONNECT_DATA=(FAILOVER_MODE=(TYPE=select)(METHOD=basic))(SERVER=dedicated)(SERVICE_NAME=DESARTP))); port=-1; username=czavalet
- transf_obtenerPeriodoExtraer.ktr: database connection name=OracleJDBC@DESARTP(OWN_TRIBUTARIO); type=ORACLE; access=Native; database=(DESCRIPTION=(FAILOVER=on)(LOAD_BALANCE=yes)(ADDRESS_LIST=(ADDRESS=(PROTOCOL=TCP)(HOST=dbdete10g-rac1.afphabitat.cl)(PORT=1532)))(CONNECT_DATA=(FAILOVER_MODE=(TYPE=select)(METHOD=basic))(SERVER=dedicated)(SERVICE_NAME=DESARTP))); port=-1; username=czavalet
- transf_obtenerPeriodoExtraer.ktr: database connection name=OracleJDBC@PRODCAR(AHERMOSI); type=ORACLE; access=Native; database=(DESCRIPTION=(FAILOVER=on)(LOAD_BALANCE=yes)(ADDRESS_LIST=(ADDRESS=(PROTOCOL=TCP)(HOST=lnxdbprod11g-rac1-vip.afphabitat.cl)(PORT=1523))(ADDRESS=(PROTOCOL=TCP)(HOST=lnxdbprod11g-rac2-vip.afphabitat.cl)(PORT=1523)))(CONNECT_DATA=(FAILOVER_MOD; port=-1; username=AHERMOSI
- transf_obtenerPeriodoExtraer.ktr: database connection name=PostgreSQL_JNDI@JiraLEAN(bigdata); type=POSTGRESQL; access=JNDI; server=atlprdh1.afphabitat.cl; database=LEAN; port=45432
- transf_obtenerPeriodoExtraer.ktr: database connection name=SampleData; type=HYPERSONIC; access=Native; server=localhost; database=SampleData; port=9001; username=pentaho_user
- transf_obtenerPeriodoExtraer.ktr: database connection name=SybaseIQ_JDBC@habitat(DMGestion); type=SYBASEIQ; access=Native; server=192.168.10.247; database=habitat; port=2638; username=DMGestion
- transf_obtenerPeriodoExtraer.ktr: database connection name=SybaseIQ_JNDI@habitat(AFC); type=SYBASEIQ; access=JNDI; server=192.168.10.247; database=AFC; port=2638
- transf_obtenerPeriodoExtraer.ktr: database connection name=SybaseIQ_JNDI@habitat(Auditoria); type=SYBASEIQ; access=JNDI; database=Auditoria; port=1521
- transf_obtenerPeriodoExtraer.ktr: database connection name=SybaseIQ_JNDI@habitat(BonoCargoFiscal); type=SYBASEIQ; access=JNDI; database=BonoCargoFiscal; port=1521
- transf_obtenerPeriodoExtraer.ktr: database connection name=SybaseIQ_JNDI@habitat(Circular119); type=SYBASEIQ; access=JNDI; database=Circular119; port=1521
- transf_obtenerPeriodoExtraer.ktr: database connection name=SybaseIQ_JNDI@habitat(Circular1509); type=SYBASEIQ; access=JNDI; server=${ServidorSybaseIQ}; database=Circular1509; port=${puerto.SybaseIQ}
- transf_obtenerPeriodoExtraer.ktr: database connection name=SybaseIQ_JNDI@habitat(Circular1532); type=SYBASEIQ; access=JNDI; database=Circular1532; port=1521
- transf_obtenerPeriodoExtraer.ktr: database connection name=SybaseIQ_JNDI@habitat(Circular1536); type=SYBASEIQ; access=JNDI; server=${ServidorSybaseIQ}; database=Circular1536; port=${puerto.SybaseIQ}
- transf_obtenerPeriodoExtraer.ktr: database connection name=SybaseIQ_JNDI@habitat(Circular1661V1); type=SYBASEIQ; access=JNDI; server=${ServidorSybaseIQ}; database=Circular1661V1; port=${puerto.SybaseIQ}
- transf_obtenerPeriodoExtraer.ktr: database connection name=SybaseIQ_JNDI@habitat(ControlProcesos); type=SYBASEIQ; access=JNDI; database=ControlProcesos; port=1521
- transf_obtenerPeriodoExtraer.ktr: database connection name=SybaseIQ_JNDI@habitat(Datawarehouse); type=SYBASEIQ; access=JNDI; server=iqprod16; database=Datawarehouse; port=2638
- transf_obtenerPeriodoExtraer.ktr: database connection name=SybaseIQ_JNDI@habitat(DDS); type=GENERIC; access=JNDI; server=192.168.10.247; database=DDS; port=2638
- transf_obtenerPeriodoExtraer.ktr: database connection name=SybaseIQ_JNDI@habitat(DMGestion); type=SYBASEIQ; access=JNDI; server=iqprod16; database=DMGestion; port=2638
- transf_obtenerPeriodoExtraer.ktr: database connection name=SybaseIQ_JNDI@habitat(Interfaz); type=SYBASEIQ; access=JNDI; database=DMGestion; port=1521
- transf_obtenerPeriodoExtraer.ktr: database connection name=SybaseIQ_JNDI@habitat(LavadoActivos); type=SYBASEIQ; access=JNDI; database=LavadoActivos; port=1521
- transf_obtenerPeriodoExtraer.ktr: database connection name=SybaseIQ_JNDI@habitat(MAC); type=SYBASEIQ; access=JNDI; server=${ServidorSybaseIQ}; database=MAC; port=${puerto.SybaseIQ}
- transf_obtenerPeriodoExtraer.ktr: database connection name=SybaseIQ_JNDI@habitat(PAET); type=SYBASEIQ; access=JNDI; database=PAET; port=1521
- transf_obtenerPeriodoExtraer.ktr: database connection name=SybaseIQ_JNDI@habitat(PowerBI); type=SYBASEIQ; access=JNDI; database=PowerBI; port=1521
- transf_obtenerPeriodoExtraer.ktr: database connection name=SybaseIQ_JNDI@habitat(Retiro10); type=SYBASEIQ; access=JNDI; database=Retiro10; port=1521
- transf_obtenerPeriodoExtraer.ktr: database connection name=SybaseIQ_JNDI@habitat(SalesForce); type=SYBASEIQ; access=JNDI; database=DMGestion; port=1521
- transf_obtenerPeriodoExtraer.ktr: database connection name=SybaseIQ_JNDI@habitat(TDS); type=SYBASEIQ; access=JNDI; database=TDS; port=1521
- transf_obtenerPeriodoExtraer.ktr: database connection name=testOracle@HABITAT; type=ORACLE; access=Native; database=(DESCRIPTION=(FAILOVER=on)(LOAD_BALANCE=yes)(ADDRESS_LIST=(ADDRESS=(PROTOCOL=TCP)(HOST=habitatvip1.afphabitat.cl)(PORT=1521))(ADDRESS=(PROTOCOL=TCP)(HOST=habitatvip2.afphabitat.cl)(PORT=1521)))(CONNECT_DATA=(FAILOVER_MODE=(TYPE=select)(METH; port=-1; username=datawarehouse
- transf_obtenerPeriodoExtraer.ktr: database connection name=testOracle@PRODAFP; type=ORACLE; access=Native; database=(DESCRIPTION=(FAILOVER=on)(LOAD_BALANCE=on)(ADDRESS_LIST=(ADDRESS=(PROTOCOL=TCP)(HOST=prodafpvip1.afphabitat.cl)(PORT=1522))(ADDRESS=(PROTOCOL=TCP)(HOST=prodafpvip2.afphabitat.cl)(PORT=1522)))(CONNECT_DATA=(FAILOVER_MODE=(TYPE=select)(METHO; port=-1; username=czavalet
- transf_obtenerPeriodoExtraer.ktr: database connection name=testSybase@IQProd; type=SYBASEIQ; access=Native; server=192.168.10.247; database=habitat; port=2638; username=DMGestion
- transf_obtenerPeriodoExtraer.ktr: database connection name=testSybase@IQProd(16.1); type=SYBASEIQ; access=Native; server=192.168.10.32; database=iq_habitat; port=2638; username=DMGestion
- transf_obtenerPeriodoExtraer.ktr: database connection name=TotalPackV24; type=MSSQL; access=Native; server=NET-SQL01; database=modeltotalpack; port=1433; username=DATAWAREHOUSE
- transf_obtenerPeriodoExtraer.ktr / Obtener Listado Fechas: embedded sql delegated to plsql analyzer
- Migrate job cargaArchivoExterno (cargaArchivoExterno.kjb) as ODI load plan / package; 9 nodes, 12 hops, 0 delegated code fragments
- Migrate transformation transf_AgendamientoZeroQ_TDS (transf_AgendamientoZeroQ_TDS.ktr) as ODI mapping / procedure; 6 nodes, 5 hops, 0 delegated code fragments
- Migrate transformation transf_AtencionesZeroQ_TDS (transf_AtencionesZeroQ_TDS.ktr) as ODI mapping / procedure; 6 nodes, 5 hops, 0 delegated code fragments
- Migrate transformation transf_MotivoAgendamientoZeroQ_TDS (transf_MotivoAgendamientoZeroQ_TDS.ktr) as ODI mapping / procedure; 13 nodes, 13 hops, 0 delegated code fragments
- Migrate transformation transf_MotivoAtencionZeroQ_TDS (transf_MotivoAtencionZeroQ_TDS.ktr) as ODI mapping / procedure; 13 nodes, 13 hops, 0 delegated code fragments
- Migrate transformation transf_obtenerPeriodoExtraer (transf_obtenerPeriodoExtraer.ktr) as ODI mapping / procedure; 2 nodes, 1 hops, 1 delegated code fragments
- TextFileInput: ${atensucu.ruta.archivo} (transf_AgendamientoZeroQ_TDS.ktr)
- transf_AgendamientoZeroQ_TDS.ktr: database connection name=AgileBI; type=MONETDB; access=Native; server=localhost; database=pentaho-instaview; port=50000; username=monetdb
- transf_AgendamientoZeroQ_TDS.ktr: database connection name=Bonobo; type=MYSQL; access=Native; server=localhost; database=bonobo; port=3306; username=root
- transf_AgendamientoZeroQ_TDS.ktr: database connection name=cnTower; type=MSSQL; access=Native; server=PDTOWH1; database=WMP_HABITAT; port=1433; username=DATAWAREHOUSE
- transf_AgendamientoZeroQ_TDS.ktr: database connection name=FUGA; type=ORACLE; access=Native; server=lnxdbplan12c.afphabitat.cl; database=PRODWINV; port=1521; username=fdelcamp[FUGA]
- transf_AgendamientoZeroQ_TDS.ktr: database connection name=Kettle; type=ORACLE; access=Native; server=192.168.10.63; database=expl10g2; port=1521; username=kettle
- transf_AgendamientoZeroQ_TDS.ktr: database connection name=MsSQLServer_JNDI@TotalPack(Datawarehouse); type=ORACLE; access=JNDI; database=TotalPack; port=1521
- transf_AgendamientoZeroQ_TDS.ktr: database connection name=MySQL5; type=MYSQL; access=Native; server=localhost; database=testPentaho; port=3306; username=root
- transf_AgendamientoZeroQ_TDS.ktr: database connection name=MySQL_JNDI@SGC(Datawarehouse); type=MYSQL; access=JNDI; server=192.168.200.130; database=SGC; port=3306
- transf_AgendamientoZeroQ_TDS.ktr: database connection name=Oracle_JDBC@DESA_RTP(Datawarehouse); type=ORACLE; access=Native; database=(DESCRIPTION=(FAILOVER=on)(LOAD_BALANCE=yes)(ADDRESS_LIST=(ADDRESS=(PROTOCOL=TCP)(HOST=dbdete10g-rac1.afphabitat.cl)(PORT=1532)))(CONNECT_DATA=(FAILOVER_MODE=(TYPE=select)(METHOD=basic))(SERVER=dedicated)(SERVICE_NAME=DESARTP))); port=-1; username=CZAVALET
- transf_AgendamientoZeroQ_TDS.ktr: database connection name=Oracle_JDBC@DESA_RTP(IPINCHEI); type=ORACLE; access=Native; database=(DESCRIPTION=(FAILOVER=on)(LOAD_BALANCE=yes)(ADDRESS_LIST=(ADDRESS=(PROTOCOL=TCP)(HOST=dbdete10g-rac1.afphabitat.cl)(PORT=1532)))(CONNECT_DATA=(FAILOVER_MODE=(TYPE=select)(METHOD=basic))(SERVER=dedicated)(SERVICE_NAME=DESARTP))); port=-1; username=ipinchei[exp_enfermoterminal]
- transf_AgendamientoZeroQ_TDS.ktr: database connection name=Oracle_JNDI@DESA_RTP(IPINCHEI); type=ORACLE; access=Native; database=(DESCRIPTION=(FAILOVER=on)(LOAD_BALANCE=yes)(ADDRESS_LIST=(ADDRESS=(PROTOCOL=TCP)(HOST=dbdete10g-rac1.afphabitat.cl)(PORT=1532)))(CONNECT_DATA=(FAILOVER_MODE=(TYPE=select)(METHOD=basic))(SERVER=dedicated)(SERVICE_NAME=DESARTP))); port=-1; username=ipinchei[exp_enfermoterminal]
- transf_AgendamientoZeroQ_TDS.ktr: database connection name=Oracle_JNDI@DOCUWARE(Datawarehouse); type=ORACLE; access=JNDI; database=DOCUWARE; port=1521
- transf_AgendamientoZeroQ_TDS.ktr: database connection name=Oracle_JNDI@EXPL10G2(Datawarehouse); type=ORACLE; access=JNDI; server=192.168.10.63; database=EXPL10G2; port=1521
- transf_AgendamientoZeroQ_TDS.ktr: database connection name=Oracle_JNDI@FINPRD(Datawarehouse); type=ORACLE; access=JNDI; database=FINPRD; port=1521
- transf_AgendamientoZeroQ_TDS.ktr: database connection name=Oracle_JNDI@HABITAT(Cierre_Mes); type=ORACLE; access=JNDI; server=${ServidorCierreMes}; database=CIERRE_MES; port=${puerto.base.Oracle}
- transf_AgendamientoZeroQ_TDS.ktr: database connection name=Oracle_JNDI@PRDINV(Datawarehouse); type=ORACLE; access=JNDI; database=PRDINV; port=1521
- transf_AgendamientoZeroQ_TDS.ktr: database connection name=Oracle_JNDI@PROD11G(Datawarehouse); type=ORACLE; access=JNDI; database=PROD11G; port=-1
- transf_AgendamientoZeroQ_TDS.ktr: database connection name=Oracle_JNDI@PRODAFP(Datawarehouse); type=ORACLE; access=JNDI; database=PRODAFP; port=1521
- transf_AgendamientoZeroQ_TDS.ktr: database connection name=Oracle_JNDI@PRODWINV(Datawarehouse); type=ORACLE; access=JNDI; server=lnxdbplan12c.afphabitat.cl; database=PRODWINV; port=1521
- transf_AgendamientoZeroQ_TDS.ktr: database connection name=Oracle_JNDI@RTCHabitat(Datawarehouse); type=ORACLE; access=JNDI; server=qa-rac2-vip.afphabitat.cl; database=RTCHabitat; port=1521
- transf_AgendamientoZeroQ_TDS.ktr: database connection name=OracleJDBC@CERTRTC(Datawarehouse); type=ORACLE; access=Native; database=(DESCRIPTION=(FAILOVER=on)(LOAD_BALANCE=yes)(ADDRESS_LIST=(ADDRESS=(PROTOCOL=TCP)(HOST=dbcert10g-rac1-vip)(PORT=1531))(ADDRESS=(PROTOCOL=TCP)(HOST=dbcert10g-rac2-vip)(PORT=1531)))(CONNECT_DATA=(FAILOVER_MODE=(TYPE=select)(METHOD=basic))(SER; port=-1; username=DATAWAREHOUSE
- transf_AgendamientoZeroQ_TDS.ktr: database connection name=OracleJDBC@CERTRTP(Datawarehouse); type=ORACLE; access=Native; database=(DESCRIPTION=(FAILOVER=on)(LOAD_BALANCE=yes)(ADDRESS_LIST=(ADDRESS=(PROTOCOL=TCP)(HOST=dbcert10g-rac1-vip)(PORT=1532)))(CONNECT_DATA=(FAILOVER_MODE=(TYPE=select)(METHOD=basic))(SERVER=dedicated)(SERVICE_NAME=CERTRTP))); port=-1; username=datawarehouse
- transf_AgendamientoZeroQ_TDS.ktr: database connection name=OracleJDBC@DESARTC(Datawarehouse); type=ORACLE; access=Native; database=(DESCRIPTION=(FAILOVER=on)(LOAD_BALANCE=yes)(ADDRESS_LIST=(ADDRESS=(PROTOCOL=TCP)(HOST=dbdete10g-rac1.afphabitat.cl)(PORT=1531)))(CONNECT_DATA=(FAILOVER_MODE=(TYPE=select)(METHOD=basic))(SERVER=dedicated)(SERVICE_NAME=DESARTC))); port=-1; username=CZAVALET
- transf_AgendamientoZeroQ_TDS.ktr: database connection name=OracleJDBC@DESARTP(Datawarehouse); type=ORACLE; access=Native; database=(DESCRIPTION=(FAILOVER=on)(LOAD_BALANCE=yes)(ADDRESS_LIST=(ADDRESS=(PROTOCOL=TCP)(HOST=dbdete10g-rac1.afphabitat.cl)(PORT=1532)))(CONNECT_DATA=(FAILOVER_MODE=(TYPE=select)(METHOD=basic))(SERVER=dedicated)(SERVICE_NAME=DESARTP))); port=-1; username=czavalet
- transf_AgendamientoZeroQ_TDS.ktr: database connection name=OracleJDBC@DESARTP(OWN_TRIBUTARIO); type=ORACLE; access=Native; database=(DESCRIPTION=(FAILOVER=on)(LOAD_BALANCE=yes)(ADDRESS_LIST=(ADDRESS=(PROTOCOL=TCP)(HOST=dbdete10g-rac1.afphabitat.cl)(PORT=1532)))(CONNECT_DATA=(FAILOVER_MODE=(TYPE=select)(METHOD=basic))(SERVER=dedicated)(SERVICE_NAME=DESARTP))); port=-1; username=czavalet
- transf_AgendamientoZeroQ_TDS.ktr: database connection name=OracleJDBC@PRODCAR(AHERMOSI); type=ORACLE; access=Native; database=(DESCRIPTION=(FAILOVER=on)(LOAD_BALANCE=yes)(ADDRESS_LIST=(ADDRESS=(PROTOCOL=TCP)(HOST=lnxdbprod11g-rac1-vip.afphabitat.cl)(PORT=1523))(ADDRESS=(PROTOCOL=TCP)(HOST=lnxdbprod11g-rac2-vip.afphabitat.cl)(PORT=1523)))(CONNECT_DATA=(FAILOVER_MOD; port=-1; username=AHERMOSI
- transf_AgendamientoZeroQ_TDS.ktr: database connection name=PostgreSQL_JNDI@JiraLEAN(bigdata); type=POSTGRESQL; access=JNDI; server=atlprdh1.afphabitat.cl; database=LEAN; port=45432
- transf_AgendamientoZeroQ_TDS.ktr: database connection name=SampleData; type=HYPERSONIC; access=Native; server=localhost; database=SampleData; port=9001; username=pentaho_user
- transf_AgendamientoZeroQ_TDS.ktr: database connection name=SybaseIQ_JDBC@habitat(DMGestion); type=SYBASEIQ; access=Native; server=192.168.10.247; database=habitat; port=2638; username=DMGestion
- transf_AgendamientoZeroQ_TDS.ktr: database connection name=SybaseIQ_JNDI@habitat(AFC); type=SYBASEIQ; access=JNDI; server=192.168.10.247; database=AFC; port=2638
- transf_AgendamientoZeroQ_TDS.ktr: database connection name=SybaseIQ_JNDI@habitat(Auditoria); type=SYBASEIQ; access=JNDI; database=Auditoria; port=1521
- transf_AgendamientoZeroQ_TDS.ktr: database connection name=SybaseIQ_JNDI@habitat(BonoCargoFiscal); type=SYBASEIQ; access=JNDI; database=BonoCargoFiscal; port=1521
- transf_AgendamientoZeroQ_TDS.ktr: database connection name=SybaseIQ_JNDI@habitat(Circular119); type=SYBASEIQ; access=JNDI; database=Circular119; port=1521
- transf_AgendamientoZeroQ_TDS.ktr: database connection name=SybaseIQ_JNDI@habitat(Circular1509); type=SYBASEIQ; access=JNDI; server=${ServidorSybaseIQ}; database=Circular1509; port=${puerto.SybaseIQ}
- transf_AgendamientoZeroQ_TDS.ktr: database connection name=SybaseIQ_JNDI@habitat(Circular1532); type=SYBASEIQ; access=JNDI; database=Circular1532; port=1521
- transf_AgendamientoZeroQ_TDS.ktr: database connection name=SybaseIQ_JNDI@habitat(Circular1536); type=SYBASEIQ; access=JNDI; server=${ServidorSybaseIQ}; database=Circular1536; port=${puerto.SybaseIQ}
- transf_AgendamientoZeroQ_TDS.ktr: database connection name=SybaseIQ_JNDI@habitat(Circular1661V1); type=SYBASEIQ; access=JNDI; server=${ServidorSybaseIQ}; database=Circular1661V1; port=${puerto.SybaseIQ}
- transf_AgendamientoZeroQ_TDS.ktr: database connection name=SybaseIQ_JNDI@habitat(ControlProcesos); type=SYBASEIQ; access=JNDI; database=ControlProcesos; port=1521
- transf_AgendamientoZeroQ_TDS.ktr: database connection name=SybaseIQ_JNDI@habitat(Datawarehouse); type=SYBASEIQ; access=JNDI; server=iqprod16; database=Datawarehouse; port=2638
- TextFileOutput: ${ruta.tds.archivo.csv}AgendamientoZeroQ (transf_AgendamientoZeroQ_TDS.ktr)
- TextFileOutput: ${ruta.tds.archivo.csv}AtencionesZeroQ (transf_AtencionesZeroQ_TDS.ktr)
- TextFileOutput: ${ruta.tds.archivo.csv}MotivoAgendamientoZeroQ (transf_MotivoAgendamientoZeroQ_TDS.ktr)
- TextFileOutput: ${ruta.tds.archivo.csv}MotivoAtencionZeroQ (transf_MotivoAtencionZeroQ_TDS.ktr)
- SetVariable: Asigna Variables (transf_obtenerPeriodoExtraer.ktr)
- Named fields recovered from step logic: `fechaCierre`, `ID_Reserva`, `ID_Llamada`, `ID_Oficina`, `Codigo_de_Oficina`, `Oficina`, `ID_Serie`, `Serie`, `ID_Linea`, `Fila`, `Modulo`, `DNI_Ejecutivo`, `Nombre_Ejecutivo`, `Fecha_Reserva`, `Hora_Reserva`, `Prefijo_Fila`, `Terminal_Reserva`, `DNI_Cliente`, `ID_Tipo_Cliente`, `Tipo_Cliente`, `Nombre_Cliente`, `Email_Cliente`, `Fecha_Creacion_Reserva`, `Hora_Creacion_Reserva`, `Fecha_Atencion`, `Hora_Atencion`, `Hora_Termino_Atencion`, `Tiempo_Espera`, `Tiempo_Atencion`, `Cancelado`.
- SQL/script bodies remain tied to their source workflow and step; validate dialect, parameters, defaults, and error behavior before porting.
- Static XML proves configured topology and logic, not production schedules, row volumes, credentials, runtime parameter values, or actual SLA performance.
- Confirm which `respaldo` and test transformations are production-active before sizing migration scope.
- Capture representative input/output samples and reconciliation totals without adding secrets or personal data to analysis artifacts.

## Target Contract
- Target runtime: `target runtime`.
- Target architecture source: [cloud-native-architecture/canonical-app-to-be/Sucursales/to-be.md](../../cloud-native-architecture/canonical-app-to-be/Sucursales/to-be.md).

## Non-Goals
- Do not contradict [cloud-native-architecture/canonical-app-to-be/Sucursales/migration-strategy.md](../../cloud-native-architecture/canonical-app-to-be/Sucursales/migration-strategy.md).

## Assumptions & Open Questions
- Confidence: `Unknown`.
