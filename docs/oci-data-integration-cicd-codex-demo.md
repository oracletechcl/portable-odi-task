# POC: OCI Data Integration + OCI Data Flow + Bitbucket CI/CD usando Codex

## Objetivo

Construir una demostración mínima que pruebe lo siguiente:

1. La lógica de transformación se mantiene en **PySpark**, versionada en Git.
2. OCI Data Integration actúa como **orquestador**.
3. OCI Data Flow ejecuta el código PySpark.
4. Bitbucket Pipelines valida y despliega el código y los artefactos.
5. La lógica PySpark puede reutilizarse posteriormente en Databricks u otro runtime Spark.
6. El Pipeline visual de OCI se trata como un adaptador específico de plataforma, no como la fuente principal de la lógica.

---

## Arquitectura de la POC

```text
Bitbucket
├── Código PySpark portable
├── Datos de prueba
├── Pruebas unitarias
├── Configuración por ambiente
├── Scripts OCI CLI
└── bitbucket-pipelines.yml
        │
        ▼
OCI Object Storage
├── input/customers.csv
├── scripts/customer_transform.py
├── scripts/validate_output.py
├── output/
└── releases/
        │
        ▼
OCI Data Flow Applications
├── DF_APP_CUSTOMER_DEMO
└── DF_APP_VALIDATE_CUSTOMERS
        │
        ▼
OCI Data Integration
├── TASK_CUSTOMER_TRANSFORM
├── TASK_VALIDATE_CUSTOMERS
├── PL_CUSTOMER_PORTABILITY_DEMO
└── TASK_RUN_CUSTOMER_PIPELINE
```

---

# 1. Prerrequisitos

Debes tener:

- Un workspace de OCI Data Integration.
- Un compartimiento OCI para la POC.
- Permiso para crear y ejecutar aplicaciones OCI Data Flow.
- Permiso para crear y administrar objetos en OCI Object Storage.
- OCI CLI configurado localmente.
- Un repositorio Bitbucket.
- Acceso a Codex sobre el repositorio local.
- Python 3.11 o 3.12.
- Git.
- Opcionalmente Docker para ejecutar pruebas Spark de manera aislada.

Verifica OCI CLI:

```bash
oci --version
oci os ns get
```

Verifica Git:

```bash
git --version
```

---

# 2. Crear el repositorio

Crea un repositorio Bitbucket llamado:

```text
oci-portability-demo
```

Clónalo:

```bash
git clone git@bitbucket.org:<workspace-bitbucket>/oci-portability-demo.git
cd oci-portability-demo
```

Crea la estructura inicial:

```bash
mkdir -p src/pyspark
mkdir -p tests
mkdir -p test-data
mkdir -p specification
mkdir -p environments
mkdir -p platforms/oci/scripts
mkdir -p platforms/oci/artifacts
mkdir -p platforms/databricks/resources
mkdir -p build
```

Estructura esperada:

```text
oci-portability-demo/
├── README.md
├── AGENTS.md
├── bitbucket-pipelines.yml
├── requirements-dev.txt
├── specification/
│   └── pipeline.yaml
├── environments/
│   ├── dev.yaml
│   ├── test.yaml
│   └── prod.yaml
├── src/
│   └── pyspark/
│       ├── customer_transform.py
│       └── validate_output.py
├── test-data/
│   └── customers.csv
├── tests/
│   └── test_customer_transform.py
└── platforms/
    ├── oci/
    │   ├── artifacts/
    │   └── scripts/
    │       ├── configure-oci.sh
    │       ├── upload-code.sh
    │       ├── upload-input.sh
    │       ├── upload-artifact.sh
    │       └── verify-output.sh
    └── databricks/
        └── resources/
            └── customer-job.yml
```

---

# 3. Configurar Codex para el repositorio

Crea `AGENTS.md` en la raíz:

```markdown
# Repository instructions

## Objective

Maintain a portable data integration proof of concept.

## Architecture rules

- Business transformation logic must remain in PySpark, Python, SQL, YAML, or JSON.
- Do not place business logic exclusively in OCI Data Integration visual operators.
- OCI-specific deployment files must remain under `platforms/oci`.
- Databricks-specific deployment files must remain under `platforms/databricks`.
- Secrets, OCIDs, private keys, passwords, and environment-specific endpoints must not be committed.
- All scripts must use `set -euo pipefail`.
- Python code must include type hints where practical.
- Transformation functions must be testable without invoking OCI services.
- TEST and PROD must receive the same immutable release artifact.

## Validation

Before completing a change, run:

```bash
python -m compileall src
pytest -q
```

When shell scripts change, also run:

```bash
find platforms/oci/scripts -name "*.sh" -exec bash -n {} \;
```
```

## Prompts recomendados para Codex

### Crear la estructura

```text
Revisa AGENTS.md y crea la estructura de archivos para una POC portable:
CSV en OCI Object Storage, transformación PySpark en OCI Data Flow,
orquestación en OCI Data Integration y CI/CD mediante Bitbucket Pipelines.
No incluyas secretos ni OCIDs reales.
```

### Revisar código

```text
Revisa el repositorio completo. Ejecuta las pruebas y corrige errores,
pero conserva la separación entre lógica portable y adaptadores OCI.
```

### Preparar un commit

```text
Ejecuta las validaciones descritas en AGENTS.md, resume los cambios,
identifica riesgos y prepara un mensaje de commit convencional.
No hagas push.
```

---

# 4. Crear los datos dummy

Crea `test-data/customers.csv`:

```csv
customer_id,customer_name,status,country,amount
1,Ana Lopez,ACTIVE,PE,150.50
2,John Smith,INACTIVE,US,80.00
3,Maria Perez,ACTIVE,PE,275.25
4,Carlos Diaz,ACTIVE,CL,90.00
5,Ana Lopez,ACTIVE,PE,125.00
```

Resultado esperado:

```csv
customer_id,customer_name,status,country,amount,amount_tax
1,ANA LOPEZ,ACTIVE,PE,150.5,177.59
3,MARIA PEREZ,ACTIVE,PE,275.25,324.8
4,CARLOS DIAZ,ACTIVE,CL,90.0,106.2
5,ANA LOPEZ,ACTIVE,PE,125.0,147.5
```

---

# 5. Crear la transformación PySpark portable

Crea `src/pyspark/customer_transform.py`:

```python
import argparse

from pyspark.sql import DataFrame, SparkSession
from pyspark.sql import functions as F


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--tax-rate", type=float, default=0.18)
    return parser.parse_args()


def transform_customers(
    dataframe: DataFrame,
    tax_rate: float,
) -> DataFrame:
    return (
        dataframe
        .filter(F.col("status") == "ACTIVE")
        .withColumn(
            "customer_name",
            F.upper(F.trim(F.col("customer_name"))),
        )
        .withColumn("amount", F.col("amount").cast("double"))
        .withColumn(
            "amount_tax",
            F.round(F.col("amount") * F.lit(1 + tax_rate), 2),
        )
        .select(
            "customer_id",
            "customer_name",
            "status",
            "country",
            "amount",
            "amount_tax",
        )
    )


def main() -> None:
    args = parse_arguments()

    spark = (
        SparkSession.builder
        .appName("customer-portability-demo")
        .getOrCreate()
    )

    source = (
        spark.read
        .option("header", "true")
        .option("inferSchema", "true")
        .csv(args.input)
    )

    result = transform_customers(source, args.tax_rate)

    (
        result.coalesce(1)
        .write
        .mode("overwrite")
        .option("header", "true")
        .csv(args.output)
    )

    print(f"Input records: {source.count()}")
    print(f"Output records: {result.count()}")
    print(f"Output path: {args.output}")

    spark.stop()


if __name__ == "__main__":
    main()
```

---

# 6. Crear la validación PySpark

Crea `src/pyspark/validate_output.py`:

```python
import argparse

from pyspark.sql import SparkSession
from pyspark.sql import functions as F


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--minimum-records", type=int, default=1)
    return parser.parse_args()


def main() -> None:
    args = parse_arguments()

    spark = (
        SparkSession.builder
        .appName("customer-output-validation")
        .getOrCreate()
    )

    dataframe = (
        spark.read
        .option("header", "true")
        .csv(args.input)
    )

    record_count = dataframe.count()
    null_customer_ids = dataframe.filter(
        F.col("customer_id").isNull()
    ).count()

    print(f"Record count: {record_count}")
    print(f"Null customer IDs: {null_customer_ids}")

    if record_count < args.minimum_records:
        raise RuntimeError(
            f"Expected at least {args.minimum_records} records; "
            f"found {record_count}"
        )

    if null_customer_ids > 0:
        raise RuntimeError(
            f"Found {null_customer_ids} null customer IDs"
        )

    spark.stop()


if __name__ == "__main__":
    main()
```

---

# 7. Crear pruebas unitarias

Crea `requirements-dev.txt`:

```text
pyspark
pytest
pyyaml
```

Crea `tests/test_customer_transform.py`:

```python
from datetime import datetime

import pytest
from pyspark.sql import SparkSession

from src.pyspark.customer_transform import transform_customers


@pytest.fixture(scope="session")
def spark() -> SparkSession:
    session = (
        SparkSession.builder
        .master("local[1]")
        .appName("customer-transform-tests")
        .getOrCreate()
    )
    yield session
    session.stop()


def test_transform_filters_and_calculates_tax(
    spark: SparkSession,
) -> None:
    source = spark.createDataFrame(
        [
            (1, " Ana Lopez ", "ACTIVE", "PE", 100.0),
            (2, "John Smith", "INACTIVE", "US", 50.0),
        ],
        [
            "customer_id",
            "customer_name",
            "status",
            "country",
            "amount",
        ],
    )

    result = transform_customers(source, tax_rate=0.18).collect()

    assert len(result) == 1
    assert result[0]["customer_name"] == "ANA LOPEZ"
    assert result[0]["amount_tax"] == 118.0
```

Ejecuta:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
python -m compileall src
pytest -q
```

---

# 8. Crear la especificación neutral

Crea `specification/pipeline.yaml`:

```yaml
name: customer-portability-demo
version: 1.0.0

description: >
  Filters active customers, normalizes names,
  calculates tax, and validates output quality.

parameters:
  input_path:
    type: string
    required: true

  output_path:
    type: string
    required: true

  tax_rate:
    type: decimal
    default: 0.18

  minimum_records:
    type: integer
    default: 1

tasks:
  - key: transform_customers
    language: pyspark
    source: src/pyspark/customer_transform.py

  - key: validate_customers
    language: pyspark
    source: src/pyspark/validate_output.py
    depends_on:
      - transform_customers

platforms:
  oci:
    runtime: OCI Data Flow
    orchestrator: OCI Data Integration

  databricks:
    runtime: Databricks Runtime
    orchestrator: Lakeflow Jobs
```

Este archivo será la descripción portable de la orquestación.

---

# 9. Crear el bucket de Object Storage

Define variables locales:

```bash
export OCI_REGION="<region>"
export OCI_COMPARTMENT_OCID="<compartment-ocid>"
export OCI_BUCKET="odi-portability-demo"
export OCI_NAMESPACE="$(oci os ns get --query data --raw-output)"
```

Crea el bucket:

```bash
oci os bucket create \
  --compartment-id "${OCI_COMPARTMENT_OCID}" \
  --name "${OCI_BUCKET}" \
  --namespace-name "${OCI_NAMESPACE}"
```

Prefijos utilizados:

```text
input/
output/
scripts/
logs/
releases/
```

Object Storage no requiere crear carpetas físicas; los prefijos aparecen al subir objetos.

---

# 10. Subir datos y código manualmente

Sube el CSV:

```bash
oci os object put \
  --namespace-name "${OCI_NAMESPACE}" \
  --bucket-name "${OCI_BUCKET}" \
  --name input/customers.csv \
  --file test-data/customers.csv \
  --force
```

Sube la transformación:

```bash
oci os object put \
  --namespace-name "${OCI_NAMESPACE}" \
  --bucket-name "${OCI_BUCKET}" \
  --name scripts/customer_transform.py \
  --file src/pyspark/customer_transform.py \
  --force
```

Sube la validación:

```bash
oci os object put \
  --namespace-name "${OCI_NAMESPACE}" \
  --bucket-name "${OCI_BUCKET}" \
  --name scripts/validate_output.py \
  --file src/pyspark/validate_output.py \
  --force
```

Rutas resultantes:

```text
oci://odi-portability-demo@<namespace>/input/customers.csv
oci://odi-portability-demo@<namespace>/scripts/customer_transform.py
oci://odi-portability-demo@<namespace>/scripts/validate_output.py
oci://odi-portability-demo@<namespace>/output/customers/
oci://odi-portability-demo@<namespace>/logs/
```

---

# 11. Crear la primera aplicación OCI Data Flow

En OCI Console:

```text
Analytics & AI
→ Data Flow
→ Applications
→ Create application
```

Configura:

| Campo | Valor |
|---|---|
| Name | `DF_APP_CUSTOMER_DEMO` |
| Language | Python |
| Main application file | `oci://odi-portability-demo@<namespace>/scripts/customer_transform.py` |
| Number of executors | `1` |
| Logs location | `oci://odi-portability-demo@<namespace>/logs/` |

Argumentos:

```text
--input
oci://odi-portability-demo@<namespace>/input/customers.csv
--output
oci://odi-portability-demo@<namespace>/output/customers/
--tax-rate
0.18
```

Selecciona las formas más pequeñas permitidas para la POC.

Ejecuta la aplicación directamente y confirma:

```text
Run status: Succeeded
```

Revisa el output:

```bash
oci os object list \
  --namespace-name "${OCI_NAMESPACE}" \
  --bucket-name "${OCI_BUCKET}" \
  --prefix output/customers/
```

---

# 12. Crear la segunda aplicación OCI Data Flow

Crea otra aplicación:

| Campo | Valor |
|---|---|
| Name | `DF_APP_VALIDATE_CUSTOMERS` |
| Language | Python |
| Main application file | `oci://odi-portability-demo@<namespace>/scripts/validate_output.py` |
| Number of executors | `1` |
| Logs location | `oci://odi-portability-demo@<namespace>/logs/` |

Argumentos:

```text
--input
oci://odi-portability-demo@<namespace>/output/customers/
--minimum-records
1
```

Ejecuta directamente y confirma:

```text
Run status: Succeeded
```

---

# 13. Configurar IAM

El workspace de OCI Data Integration necesita autorización para consultar aplicaciones OCI Data Flow y crear runs.

Usa políticas equivalentes a las siguientes, adaptadas a tu modelo IAM:

```text
allow any-user to manage dataflow-application
in compartment <COMPARTMENT_NAME>
where all {
  request.principal.type = 'disworkspace',
  request.principal.id = '<WORKSPACE_OCID>'
}
```

```text
allow any-user to manage dataflow-run
in compartment <COMPARTMENT_NAME>
where all {
  request.principal.type = 'disworkspace',
  request.principal.id = '<WORKSPACE_OCID>'
}
```

También se requieren permisos apropiados sobre Object Storage para leer scripts, entrada y escribir salida y logs.

No uses políticas amplias en producción. Limita compartimiento, workspace y recursos.

---

# 14. Crear el proyecto en OCI Data Integration

En el workspace:

```text
Projects
→ Create project
```

Valores:

```text
Name: PORTABILITY_DEMO
Identifier: PORTABILITY_DEMO
Description: Portable PySpark CI/CD proof of concept
```

---

# 15. Crear la tarea de transformación

Dentro del proyecto:

```text
Tasks
→ Create task
→ OCI Data Flow task
```

Valores:

```text
Name: TASK_CUSTOMER_TRANSFORM
Identifier: TASK_CUSTOMER_TRANSFORM
Application: DF_APP_CUSTOMER_DEMO
```

Configura inicialmente los argumentos fijos:

```text
--input
oci://odi-portability-demo@<namespace>/input/customers.csv

--output
oci://odi-portability-demo@<namespace>/output/customers/

--tax-rate
0.18
```

Guarda y valida.

---

# 16. Crear la tarea de validación

Crea otra OCI Data Flow Task:

```text
Name: TASK_VALIDATE_CUSTOMERS
Identifier: TASK_VALIDATE_CUSTOMERS
Application: DF_APP_VALIDATE_CUSTOMERS
```

Argumentos:

```text
--input
oci://odi-portability-demo@<namespace>/output/customers/

--minimum-records
1
```

Guarda y valida.

---

# 17. Crear el Pipeline de OCI Data Integration

Dentro del proyecto:

```text
Pipelines
→ Create pipeline
```

Valores:

```text
Name: PL_CUSTOMER_PORTABILITY_DEMO
Identifier: PL_CUSTOMER_PORTABILITY_DEMO
```

En el canvas crea:

```text
START
  ↓
TASK_CUSTOMER_TRANSFORM
  ↓
TASK_VALIDATE_CUSTOMERS
  ↓
END
```

Pasos:

1. Arrastra un operador de tarea.
2. Selecciona `TASK_CUSTOMER_TRANSFORM`.
3. Arrastra otro operador de tarea.
4. Selecciona `TASK_VALIDATE_CUSTOMERS`.
5. Conecta `START` con transformación.
6. Conecta transformación con validación.
7. Conecta validación con `END`.
8. Configura el operador `END` para reflejar fallo cuando alguna tarea falle.
9. Selecciona **Validate**.
10. Guarda.

---

# 18. Parametrizar el Pipeline

Crea estos parámetros:

```text
P_INPUT_PATH
P_OUTPUT_PATH
P_TAX_RATE
P_MINIMUM_RECORDS
```

Valores DEV:

```text
P_INPUT_PATH =
oci://odi-portability-demo@<namespace>/input/customers.csv

P_OUTPUT_PATH =
oci://odi-portability-demo@<namespace>/output/customers/

P_TAX_RATE =
0.18

P_MINIMUM_RECORDS =
1
```

Mapea la tarea de transformación:

```text
--input       → P_INPUT_PATH
--output      → P_OUTPUT_PATH
--tax-rate    → P_TAX_RATE
```

Mapea la tarea de validación:

```text
--input              → P_OUTPUT_PATH
--minimum-records    → P_MINIMUM_RECORDS
```

La lógica PySpark no contiene rutas de ambiente.

---

# 19. Crear la Pipeline Task

La definición del Pipeline es de diseño. Para ejecutarla:

```text
Tasks
→ Create task
→ Pipeline task
```

Configura:

```text
Name: TASK_RUN_CUSTOMER_PIPELINE
Identifier: TASK_RUN_CUSTOMER_PIPELINE
Pipeline: PL_CUSTOMER_PORTABILITY_DEMO
```

Guarda y valida.

---

# 20. Publicar y ejecutar

Crea o reutiliza una aplicación OCI Data Integration:

```text
Applications
→ Create application
```

Nombre:

```text
APP_PORTABILITY_DEMO
```

Publica:

```text
TASK_RUN_CUSTOMER_PIPELINE
→ Actions
→ Publish
→ APP_PORTABILITY_DEMO
```

Ejecuta con:

```text
P_INPUT_PATH =
oci://odi-portability-demo@<namespace>/input/customers.csv

P_OUTPUT_PATH =
oci://odi-portability-demo@<namespace>/output/customers/

P_TAX_RATE = 0.18
P_MINIMUM_RECORDS = 1
```

Resultado esperado:

```text
PL_CUSTOMER_PORTABILITY_DEMO: SUCCEEDED
├── TASK_CUSTOMER_TRANSFORM: SUCCEEDED
└── TASK_VALIDATE_CUSTOMERS: SUCCEEDED
```

---

# 21. Demostrar propagación de errores

Ejecuta nuevamente con:

```text
P_MINIMUM_RECORDS = 100
```

Resultado esperado:

```text
TASK_CUSTOMER_TRANSFORM: SUCCEEDED
TASK_VALIDATE_CUSTOMERS: FAILED
PL_CUSTOMER_PORTABILITY_DEMO: FAILED
```

Esto demuestra dependencias, validación y propagación del estado.

---

# 22. Exportar el artefacto OCI

Desde el proyecto:

```text
Pipelines
→ PL_CUSTOMER_PORTABILITY_DEMO
→ Actions
→ Export
```

Configura:

```text
Bucket: odi-portability-demo
File name: releases/customer-portability-demo-1.0.0
```

Resultado esperado:

```text
releases/customer-portability-demo-1.0.0.pipeline.zip
```

Para una unidad completa de despliegue, exporta preferentemente la carpeta o proyecto que contiene las tareas, el Pipeline y sus referencias.

Descarga el ZIP:

```bash
oci os object get \
  --namespace-name "${OCI_NAMESPACE}" \
  --bucket-name "${OCI_BUCKET}" \
  --name releases/customer-portability-demo-1.0.0.pipeline.zip \
  --file platforms/oci/artifacts/customer-portability-demo-1.0.0.pipeline.zip
```

Calcula el hash:

```bash
sha256sum \
  platforms/oci/artifacts/customer-portability-demo-1.0.0.pipeline.zip \
  > platforms/oci/artifacts/customer-portability-demo-1.0.0.pipeline.zip.sha256
```

No edites manualmente el contenido del ZIP.

---

# 23. Configuración por ambiente

Crea `environments/dev.yaml`:

```yaml
environment: dev
bucket: odi-portability-demo
input_path: oci://odi-portability-demo@REPLACE_NAMESPACE/input/customers.csv
output_path: oci://odi-portability-demo@REPLACE_NAMESPACE/output/dev/customers/
tax_rate: 0.18
minimum_records: 1
```

Crea `environments/test.yaml`:

```yaml
environment: test
bucket: odi-portability-demo-test
input_path: oci://odi-portability-demo-test@REPLACE_NAMESPACE/input/customers.csv
output_path: oci://odi-portability-demo-test@REPLACE_NAMESPACE/output/customers/
tax_rate: 0.18
minimum_records: 1
```

Crea `environments/prod.yaml`:

```yaml
environment: prod
bucket: odi-portability-demo-prod
input_path: oci://odi-portability-demo-prod@REPLACE_NAMESPACE/input/customers.csv
output_path: oci://odi-portability-demo-prod@REPLACE_NAMESPACE/output/customers/
tax_rate: 0.18
minimum_records: 1
```

No incluyas credenciales.

---

# 24. Crear scripts OCI para CI/CD

## `platforms/oci/scripts/configure-oci.sh`

```bash
#!/usr/bin/env bash
set -euo pipefail

required_variables=(
  OCI_TENANCY_OCID
  OCI_USER_OCID
  OCI_FINGERPRINT
  OCI_PRIVATE_KEY_BASE64
  OCI_REGION
)

for variable in "${required_variables[@]}"; do
  if [ -z "${!variable:-}" ]; then
    echo "Missing required variable: ${variable}" >&2
    exit 1
  fi
done

mkdir -p "${HOME}/.oci"

printf '%s' "${OCI_PRIVATE_KEY_BASE64}" \
  | base64 --decode \
  > "${HOME}/.oci/oci_api_key.pem"

chmod 600 "${HOME}/.oci/oci_api_key.pem"

cat > "${HOME}/.oci/config" <<EOF
[DEFAULT]
user=${OCI_USER_OCID}
fingerprint=${OCI_FINGERPRINT}
tenancy=${OCI_TENANCY_OCID}
region=${OCI_REGION}
key_file=${HOME}/.oci/oci_api_key.pem
EOF

oci os ns get >/dev/null
```

## `platforms/oci/scripts/upload-code.sh`

```bash
#!/usr/bin/env bash
set -euo pipefail

: "${OCI_NAMESPACE:?Missing OCI_NAMESPACE}"
: "${OCI_BUCKET:?Missing OCI_BUCKET}"

oci os object put \
  --namespace-name "${OCI_NAMESPACE}" \
  --bucket-name "${OCI_BUCKET}" \
  --name scripts/customer_transform.py \
  --file src/pyspark/customer_transform.py \
  --force

oci os object put \
  --namespace-name "${OCI_NAMESPACE}" \
  --bucket-name "${OCI_BUCKET}" \
  --name scripts/validate_output.py \
  --file src/pyspark/validate_output.py \
  --force
```

## `platforms/oci/scripts/upload-input.sh`

```bash
#!/usr/bin/env bash
set -euo pipefail

: "${OCI_NAMESPACE:?Missing OCI_NAMESPACE}"
: "${OCI_BUCKET:?Missing OCI_BUCKET}"

oci os object put \
  --namespace-name "${OCI_NAMESPACE}" \
  --bucket-name "${OCI_BUCKET}" \
  --name input/customers.csv \
  --file test-data/customers.csv \
  --force
```

## `platforms/oci/scripts/verify-output.sh`

```bash
#!/usr/bin/env bash
set -euo pipefail

: "${OCI_NAMESPACE:?Missing OCI_NAMESPACE}"
: "${OCI_BUCKET:?Missing OCI_BUCKET}"

count="$(
  oci os object list \
    --namespace-name "${OCI_NAMESPACE}" \
    --bucket-name "${OCI_BUCKET}" \
    --prefix output/customers/ \
    --query 'length(data)' \
    --raw-output
)"

if [ "${count}" -lt 1 ]; then
  echo "No output objects found" >&2
  exit 1
fi

echo "Output objects found: ${count}"
```

Hazlos ejecutables:

```bash
chmod +x platforms/oci/scripts/*.sh
```

---

# 25. Configurar variables de Bitbucket

En Bitbucket:

```text
Repository settings
→ Pipelines
→ Repository variables
```

Configura como variables protegidas:

```text
OCI_TENANCY_OCID
OCI_USER_OCID
OCI_FINGERPRINT
OCI_PRIVATE_KEY_BASE64
OCI_REGION
OCI_NAMESPACE
OCI_BUCKET
OCI_TEST_WORKSPACE_OCID
OCI_PROD_WORKSPACE_OCID
```

No imprimas secretos en logs.

Para la clave:

```bash
base64 -w 0 ~/.oci/oci_api_key.pem
```

En macOS:

```bash
base64 < ~/.oci/oci_api_key.pem | tr -d '\n'
```

---

# 26. Crear `bitbucket-pipelines.yml`

```yaml
image: python:3.12-slim

definitions:
  caches:
    pip: ~/.cache/pip

  steps:
    - step: &validate
        name: Validate portable code
        caches:
          - pip
        script:
          - apt-get update
          - apt-get install -y default-jre-headless
          - pip install -r requirements-dev.txt
          - python -m compileall src
          - pytest -q
          - find platforms/oci/scripts -name "*.sh" -exec bash -n {} \;

    - step: &upload-dev
        name: Upload demo code
        deployment: test
        caches:
          - pip
        script:
          - pip install oci-cli
          - ./platforms/oci/scripts/configure-oci.sh
          - ./platforms/oci/scripts/upload-code.sh
          - ./platforms/oci/scripts/upload-input.sh

    - step: &verify-output
        name: Verify OCI output
        caches:
          - pip
        script:
          - pip install oci-cli
          - ./platforms/oci/scripts/configure-oci.sh
          - ./platforms/oci/scripts/verify-output.sh

pipelines:
  pull-requests:
    "**":
      - step: *validate

  branches:
    main:
      - step: *validate
      - step: *upload-dev

  custom:
    verify-oci-output:
      - step: *verify-output
```

Este pipeline valida y publica el código PySpark. La automatización completa de importación/publicación/ejecución de OCI Data Integration debe añadirse después de confirmar los payloads CLI/API exactos de tu workspace y versión de servicio.

---

# 27. Primer commit

Ejecuta:

```bash
python -m compileall src
pytest -q
find platforms/oci/scripts -name "*.sh" -exec bash -n {} \;
```

Después:

```bash
git add .
git commit -m "feat: add portable OCI data integration demo"
git push origin main
```

Codex puede revisar el cambio con este prompt:

```text
Revisa el diff actual y AGENTS.md. Confirma que:
1. La lógica de negocio está en PySpark portable.
2. No hay secretos ni OCIDs reales.
3. Los scripts fallan de forma segura.
4. Las pruebas cubren filtro, normalización y cálculo.
5. El pipeline Bitbucket no intenta recrear el artefacto para cada ambiente.
Corrige cualquier incumplimiento y ejecuta las validaciones.
```

---

# 28. Demostrar portabilidad hacia Databricks

El archivo PySpark principal puede reutilizarse. Lo que debe reconstruirse es la orquestación.

Crea `platforms/databricks/resources/customer-job.yml`:

```yaml
resources:
  jobs:
    customer_portability_demo:
      name: customer-portability-demo

      parameters:
        - name: input_path
          default: ""
        - name: output_path
          default: ""
        - name: tax_rate
          default: "0.18"
        - name: minimum_records
          default: "1"

      tasks:
        - task_key: transform_customers
          spark_python_task:
            python_file: ../../../src/pyspark/customer_transform.py
            parameters:
              - --input
              - "{{job.parameters.input_path}}"
              - --output
              - "{{job.parameters.output_path}}"
              - --tax-rate
              - "{{job.parameters.tax_rate}}"

        - task_key: validate_customers
          depends_on:
            - task_key: transform_customers
          spark_python_task:
            python_file: ../../../src/pyspark/validate_output.py
            parameters:
              - --input
              - "{{job.parameters.output_path}}"
              - --minimum-records
              - "{{job.parameters.minimum_records}}"
```

La equivalencia es:

| OCI | Portable | Databricks |
|---|---|---|
| OCI Data Flow Application | Archivo PySpark | Spark Python task |
| OCI Data Flow Task | Parámetros de ejecución | Job task |
| OCI Data Integration Pipeline | `specification/pipeline.yaml` | Lakeflow Job |
| Pipeline parameters | YAML | Job parameters |
| Object Storage path | URI configurable | Cloud storage URI |
| OCI Application | Release | Bundle/Job deployment |

---

# 29. Guion de demostración

## Parte 1: código portable

Muestra:

```text
src/pyspark/customer_transform.py
src/pyspark/validate_output.py
tests/test_customer_transform.py
specification/pipeline.yaml
```

Explica:

- PySpark es la fuente de la lógica.
- Git conserva historial y diffs legibles.
- Las pruebas se ejecutan sin OCI Data Integration.
- La orquestación neutral está descrita en YAML.

## Parte 2: runtime OCI

Muestra:

1. CSV en Object Storage.
2. Aplicación `DF_APP_CUSTOMER_DEMO`.
3. Aplicación `DF_APP_VALIDATE_CUSTOMERS`.
4. Tareas OCI Data Integration.
5. Pipeline secuencial.
6. Ejecución exitosa.
7. Archivo de salida.

## Parte 3: fallo controlado

Ejecuta con:

```text
P_MINIMUM_RECORDS = 100
```

Muestra el fallo de validación y del Pipeline.

## Parte 4: CI/CD

Muestra:

- Pull request ejecutando pruebas.
- Merge a `main`.
- Bitbucket subiendo scripts.
- Secrets fuera de Git.
- Hash del ZIP OCI.

## Parte 5: portabilidad

Muestra:

- El ZIP OCI no se importa en Databricks.
- Los archivos PySpark sí se reutilizan.
- `customer-job.yml` reconstruye únicamente la orquestación.

---

# 30. Criterios de aceptación

La POC está completa cuando:

- [ ] El CSV está en Object Storage.
- [ ] La transformación OCI Data Flow termina correctamente.
- [ ] La validación termina correctamente.
- [ ] OCI Data Integration ejecuta ambas tareas en secuencia.
- [ ] El Pipeline falla cuando `minimum_records=100`.
- [ ] El código PySpark está versionado en Bitbucket.
- [ ] Las pruebas unitarias se ejecutan en Bitbucket Pipelines.
- [ ] No existen secretos en el repositorio.
- [ ] El Pipeline o proyecto OCI se exporta como ZIP.
- [ ] El ZIP tiene hash SHA-256.
- [ ] La misma lógica PySpark puede mapearse a un Job Databricks.
- [ ] La documentación distingue código portable de configuración OCI.

---

# 31. Qué es portable y qué no

## Portable

- PySpark.
- Python.
- SQL estándar.
- YAML y JSON.
- Contratos de datos.
- Parámetros funcionales.
- Reglas de calidad.
- Pruebas unitarias.
- Datos de prueba.
- Reconciliaciones.

## Específico de OCI

- OCI Data Integration Pipeline.
- OCI Data Flow Task.
- Publicación en Application.
- Data Assets.
- OCIDs.
- IAM.
- Rutas `oci://`.
- ZIP exportado por OCI Data Integration.
- Configuración de shapes y runtime.

---

# 32. Principio de diseño

> OCI Data Integration debe orquestar.  
> PySpark, SQL o Python deben contener la lógica que se quiera reutilizar.

No intentes convertir el ZIP OCI en un artefacto multi-cloud. Usa el ZIP para promoción DEV → TEST → PROD dentro de OCI y usa los archivos de código y la especificación neutral para reconstruir la orquestación en otras plataformas.

---

# 33. Referencias Oracle

- OCI Data Integration: creación de Pipelines  
  `https://docs.oracle.com/en-us/iaas/Content/data-integration/using/creating-a-pipeline.htm`

- OCI Data Integration: exportación e importación de Pipelines  
  `https://docs.oracle.com/en-us/iaas/Content/data-integration/using/pipeline-export-import.htm`

- OCI Data Integration: OCI Data Flow Tasks  
  `https://docs.oracle.com/en-us/iaas/Content/data-integration/using/oci-dataflow-tasks.htm`

- OCI Data Integration: exportación de tareas, Data Flows y Pipelines  
  `https://docs.oracle.com/en-us/iaas/Content/data-integration/using/export-folder-task-dataflow-pipeline.htm`
