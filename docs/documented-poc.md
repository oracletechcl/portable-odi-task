# OCI Data Integration CI/CD PoC inventory

## Execution scope

- Region: `us-sanjose-1`
- Compartment: `ocid1.compartment.oc1..aaaaaaaal7vn7wsy3qgizklrlfgo2vllfta3wkqlnfkvykoroite3lzxbnna`
- Object Storage namespace: `idi1o0a010nx`
- GitHub repository simulates Bitbucket source control and CI/CD.
- IAM was pre-existing by agreement. This PoC does not create or modify IAM policies.

## Existing dependency

| Type | Name | OCID | State |
|---|---|---|---|
| Data Integration workspace | Supplied workspace | `ocid1.disworkspace.oc1.us-sanjose-1.anzwuljr2ow634yazkdp5uah7vgzz24pn2hbipwtukv72ap6hrbikm4nggca` | ACTIVE |

## Created assets

| Type | Name | OCID | State | Notes |
|---|---|---|---|---|
| Object Storage bucket | `odi-portability-demo` | `ocid1.bucket.oc1.us-sanjose-1.aaaaaaaa75myy2fixmjaswfx2xp56dhi6u3r3bauey23x3v62guc7tnpumka` | Created | Private (`NoPublicAccess`) |
| Data Integration project | `PORTABILITY_DEMO` | No OCID exposed by this service object; key: `9a43adfb-70d9-4097-889e-df7cae272c52` | Created | In the supplied workspace |
| Data Flow application | `DF_APP_CUSTOMER_DEMO` | `ocid1.dataflowapplication.oc1.us-sanjose-1.anzwuljrfioir7iajlysl73h5h74zpq7z5oklekfwcrkqrqtwqql5y5dupia` | ACTIVE | PySpark transform, Spark 3.5.0, 1 executor |
| Data Flow application | `DF_APP_VALIDATE_CUSTOMERS` | `ocid1.dataflowapplication.oc1.us-sanjose-1.anzwuljrfioir7iaru5rvozwywgcitfswwxp2i5fhtwuwbq57wdxzih3cq5q` | ACTIVE | PySpark validation, Spark 3.5.0, 1 executor |
| Data Flow application | `DF_APP_JAVA_LANGUAGE_PROBE` | `ocid1.dataflowapplication.oc1.us-sanjose-1.anzwuljrfioir7iaxyac2znt4bpdkuuwyk2sllrvuzw52j5l3csjtx343c5a` | ACTIVE | Java, Spark 3.5.0; class `com.oracle.poc.CustomerJavaProbe` |
| Data Flow application | `DF_APP_SCALA_LANGUAGE_PROBE` | `ocid1.dataflowapplication.oc1.us-sanjose-1.anzwuljrfioir7iaq5eegoxndpbi3qxuqddvqkae2j225ewbnthzhkp3dnea` | ACTIVE | Scala, Spark 3.5.0; class `com.oracle.poc.CustomerScalaProbe` |
| Data Flow application | `DF_APP_SQL_LANGUAGE_PROBE` | `ocid1.dataflowapplication.oc1.us-sanjose-1.anzwuljrfioir7iaunk3igjoswslwt43juczcne4hm6mmpkoifsinxuykl6q` | ACTIVE | Spark SQL; warehouse `oci://odi-portability-demo@idi1o0a010nx/warehouse/` |
| Data Flow run | `RUN_CUSTOMER_TRANSFORM_SUCCESS` | `ocid1.dataflowrun.oc1.us-sanjose-1.anzwuljrfioir7iaitwrzp4hqv4vtl3e2gcynvo4u5z37wc475dfpars76sq` | SUCCEEDED | Direct verification of transformation application |
| Data Flow run | `RUN_CUSTOMER_VALIDATE_SUCCESS` | `ocid1.dataflowrun.oc1.us-sanjose-1.anzwuljrfioir7ia3gdtprpbiqnnlaf2kusog4jk2zd3iuycrjynt7bqkqoa` | SUCCEEDED | Direct verification of validation application |
| Data Flow run | `RUN_CUSTOMER_VALIDATE_EXPECTED_FAILURE` | `ocid1.dataflowrun.oc1.us-sanjose-1.anzwuljrfioir7iavx5o2slttnnj5chjs36cgy2rkuetijhfch3jvivwoztq` | FAILED (expected) | `RuntimeError` raised with `--minimum-records 100` |
| Data Flow run | `RUN_JAVA_LANGUAGE_PROBE` | `ocid1.dataflowrun.oc1.us-sanjose-1.anzwuljrfioir7iajhlvz6vyuusne3iobu3xiklwbwodduks2jhrgudcsnla` | FAILED (diagnostic) | Spark driver failed because the original JAR targeted Java 17 and the run received no required arguments |
| Data Flow run | `RUN_SCALA_LANGUAGE_PROBE` | `ocid1.dataflowrun.oc1.us-sanjose-1.anzwuljrfioir7iatui4xzo7xk4wlpkjgqt6rsrfhs3mk4rupjx36ydkj6jq` | FAILED (diagnostic) | Spark driver failed because the original run received no required arguments |
| Data Flow run | `RUN_SQL_LANGUAGE_PROBE` | `ocid1.dataflowrun.oc1.us-sanjose-1.anzwuljrfioir7iafh3qfeapb4r2q564bsqsiqhvduhlwf2fqf74hn73yiza` | FAILED (diagnostic) | SQL parameter paths were not declared on the application |
| Data Flow run | `RUN_JAVA_LANGUAGE_PROBE_RERUN` | `ocid1.dataflowrun.oc1.us-sanjose-1.anzwuljrfioir7iakicmlegqau4uq2e5gsqnlmm5z556grzngcw4hgsrgpzq` | SUCCEEDED | Java 8-compatible JAR with explicit input, output, and tax-rate arguments |
| Data Flow run | `RUN_SCALA_LANGUAGE_PROBE_RERUN` | `ocid1.dataflowrun.oc1.us-sanjose-1.anzwuljrfioir7ia5ajodklhlpj5zaf5mi2j7lf62vxqjwyy65dlmgsv2oza` | SUCCEEDED | Explicit input, output, and tax-rate arguments |
| Data Flow run | `RUN_SQL_LANGUAGE_PROBE_RERUN` | `ocid1.dataflowrun.oc1.us-sanjose-1.anzwuljrfioir7iawzienxwkltcros2lyq7bfcydnrjegjff6uxsmxgrfqeq` | SUCCEEDED | Declared SQL parameters and explicit Object Storage warehouse |
| Data Integration task | `TASK_CUSTOMER_TRANSFORM` | No OCID exposed; key: `816bf5d7-83ce-430d-9ada-7c94580afdc3` | Created | References the transformation Data Flow application |
| Data Integration task | `TASK_VALIDATE_CUSTOMERS` | No OCID exposed; key: `611236f4-c350-4411-937b-97c4b9028ca1` | Created | References the validation Data Flow application |
| Data Integration pipeline | `PL_CUSTOMER_PORTABILITY_DEMO` | No OCID exposed; key: `11abd998-ed40-4b4a-90eb-b244bd600039` | Created | Four-node sequential FlowNode graph: START → transform → validate → END |
| Data Integration pipeline task | `TASK_RUN_CUSTOMER_PIPELINE` | No OCID exposed; key: `fc64b80c-7628-4576-aff7-0bda6fdd3786` | Published | Wraps the pipeline for runtime execution |
| Data Integration application | `APP_PORTABILITY_DEMO` | No OCID exposed; key: `99f4f30b-cf4c-4720-ae8e-ecc3ce9716a5` | Created | Hosts the published pipeline task |
| Data Integration publication patch | `PUBLISH_CUSTOMER_PIPELINE` | No OCID exposed; key: `4269d85e-96f5-4b48-991f-013df31200b4` | Published | Published `TASK_RUN_CUSTOMER_PIPELINE` |
| Data Integration task run | `RUN_CUSTOMER_PIPELINE_SUCCESS` | No OCID exposed; key: `cfda1c74-89ad-47ec-ae73-273d20f3fff4` | ERROR | Workspace principal was not authorized to create the child Data Flow run |
| Data Integration export request | `customer-portability-demo-1.0.0.pipeline.zip` | No OCID exposed; key: `22777c57-6ed9-4f80-a2cf-6fb15b3d34e1` | SUCCESSFUL | Exported five design objects to `releases/` |

## IAM prerequisite (documented only)

The Data Integration workspace principal needs least-privilege permissions to manage the two Data Flow applications and their runs in this compartment, plus read access to the scripts and input objects and write access to output and logs. Scope policies to the supplied workspace OCID and compartment; do not use broad production policies.

## Supported movable platforms

| Platform | Runtime and orchestration model | PoC status |
|---|---|---|
| OCI Data Flow | OCI Data Flow with OCI Data Integration orchestration | OCI applications and direct runs were created and verified |
| Databricks | Databricks Runtime with Lakeflow Jobs | Source-controlled deployment mapping only; no external resource was provisioned |
| Amazon EMR | Amazon EMR on EC2 or EMR Serverless with EMR Steps | Source-controlled deployment mapping only; no external resource was provisioned |
| Microsoft Fabric | Fabric Spark with a Fabric Data Factory pipeline | Source-controlled deployment mapping only; no external resource was provisioned |
| Google Dataproc | Dataproc Serverless for Spark with a workflow template | Source-controlled deployment mapping only; no external resource was provisioned |

The portable repository includes Java, Python, Spark SQL, and Scala source flavors. The external-platform mappings describe deployment handoff only: this PoC did not create, connect to, or execute workloads in those external platforms.

## Export integrity

- Object: `releases/customer-portability-demo-1.0.0.pipeline.zip`
- SHA-256: `997106253998b950b7424a25410c1a9e0c06f71e053ae3023c83a0aa62818fa3`

## Verification record

- The direct Data Flow transform run succeeded.
- The direct Data Flow validation run succeeded.
- The Data Integration pipeline design, pipeline task, application, publication patch, and export succeeded.
- The Data Integration end-to-end run failed before the transform began. Its workspace principal received `NotAuthorizedOrNotFound` from the Data Flow `CreateRun` API. No IAM changes were made by this PoC.
- The controlled direct Data Flow failure completed as expected with `RuntimeError` at `--minimum-records 100`.
- The direct Java, Scala, and SQL language-probe reruns all succeeded. The first three language-probe runs are retained above as diagnostic evidence; their corrected reruns use explicit arguments, declared SQL parameters, and Java 8-compatible bytecode.
- The pipeline-level success and failure-propagation criteria remain blocked until the workspace principal is granted the documented least-privilege Data Flow application/run permissions.
- The live Data Integration pipeline currently invokes the applications with their configured default arguments. Map `P_INPUT_PATH`, `P_OUTPUT_PATH`, `P_TAX_RATE`, and `P_MINIMUM_RECORDS`, then rerun the success and controlled-failure paths after the workspace principal is authorized.
