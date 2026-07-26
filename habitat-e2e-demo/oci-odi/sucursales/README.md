# Habitat Sucursales Demo

One script prepares the VM mock and publishes the OCI Data Integration task.
After it finishes, open the application and click Run.

## How the POC works

```mermaid
flowchart TB
    OP["Operator"] -->|"Runs one-stop script with app name and run date"| DEPLOY["Generic deployment script"]

    DEPLOY -->|"Uploads HABITAT_SUCURSALES.project.zip"| OS["OCI Object Storage"]
    OS -->|"Imports project"| PROJECT["OCI Data Integration project<br/>HABITAT_SUCURSALES"]
    PROJECT -->|"Publishes task and dependencies"| APP["OCI Data Integration Application<br/>user-supplied name"]
    APP -->|"Run"| RUN["TASK_RUN_HABITAT_SUCURSALES"]
    RUN --> PIPE["PL_HABITAT_SUCURSALES"]

    DEPLOY -->|"Installs service, fixtures, firewall, and health check"| API

    subgraph ODI["OCI Data Integration execution"]
        PIPE --> PERIODS["REST_PERIODS<br/>POST /v1/periods"]
        PERIODS -->|success| AP["REST_ATENCIONES_PREVIOUS<br/>POST /v1/process/atenciones"]
        AP -->|success| AC["REST_ATENCIONES_CURRENT<br/>POST /v1/process/atenciones"]
        AC -->|success| GP["REST_AGENDAMIENTOS_PREVIOUS<br/>POST /v1/process/agendamientos"]
        GP -->|success| GC["REST_AGENDAMIENTOS_CURRENT<br/>POST /v1/process/agendamientos"]
        GC -->|success| VALIDATE["REST_VALIDATE<br/>POST /v1/validate"]
        VALIDATE -->|success| END["Succeeded"]

        AP -. failure .-> NAP["REST_NOTIFY_ATENCIONES_PREVIOUS"]
        AC -. failure .-> NAC["REST_NOTIFY_ATENCIONES_CURRENT"]
        GP -. failure .-> NGP["REST_NOTIFY_AGENDAMIENTOS_PREVIOUS"]
        GC -. failure .-> NGC["REST_NOTIFY_AGENDAMIENTOS_CURRENT"]
    end

    subgraph VM["Compute VM mock backend on the private VCN"]
        API["Mock HTTP service"]
        FIX["CSV fixtures<br/>previous and current periods"] --> API
        API -->|"process routes"| TRANSFORM["Pure Python transformations<br/>testable without OCI"]
        TRANSFORM --> OUT["Eight CSV outputs<br/>Atenciones, MotivoAtencion,<br/>Agendamiento, MotivoAgendamiento<br/>for previous and current periods"]
        OUT --> CHECK["Output validation"]
        API -->|"validate route"| CHECK
        API -->|"notification route"| FAILLOG["Mock failure-notification log"]
    end

    PERIODS -->|"/v1/periods"| API
    AP -->|"/v1/process/atenciones"| API
    AC -->|"/v1/process/atenciones"| API
    GP -->|"/v1/process/agendamientos"| API
    GC -->|"/v1/process/agendamientos"| API
    VALIDATE -->|"POST /v1/validate"| API
    NAP -->|"POST /v1/notify-error"| API
    NAC -->|"POST /v1/notify-error"| API
    NGP -->|"POST /v1/notify-error"| API
    NGC -->|"POST /v1/notify-error"| API
```

## 1. Deploy everything

Run once from the repository root:

```bash
./platforms/oci/scripts/deploy-habitat-sucursales-demo.sh \
  --app-name HABITAT_SUCURSALES_DEMO \
  --as-of-date 2026-07-15
```

Wait for `READY`.

The script reads the local, untracked configuration from:

```text
habitat-e2e-demo/oci-odi/sucursales/.demo-deploy.env
```

## What the script does

- verifies the release checksum;
- uses the application name you pass; there is no default application;
- installs and starts the mock on the Compute VM;
- registers and enables `habitat-sucursales-mock.service`;
- restricts TCP 8080 to the Data Integration workspace subnet;
- performs the `/health` check;
- uploads the project ZIP to the configured Object Storage bucket;
- imports or replaces the OCI Data Integration project;
- puts the VM private URL and `AS_OF_DATE` into the REST tasks;
- creates the application name you pass when missing;
- finds the imported task `TASK_RUN_HABITAT_SUCURSALES`; and
- publishes the task and stops immediately if OCI rejects the patch.

Run it again with another `--app-name` to reuse the same deployment in another
application.

## 2. Open the application

In the OCI Console:

1. Open **Data Integration** → **Workspaces** → the target workspace.
2. Open **Applications** → `HABITAT_SUCURSALES_DEMO`.
3. Open **Tasks**. Page 1 contains the ten REST dependencies.
4. Click **Page 2**, or use **Filter by name** for
   `TASK_RUN_HABITAT_SUCURSALES`.
5. Open `TASK_RUN_HABITAT_SUCURSALES`.

## 3. Click Run

Choose **Run**. Do not enter parameters: the script already materialized the
mock URL and run date. Start the run and wait for **Succeeded** under **Runs**.

The eight result CSVs are written on the VM under:

```text
/var/lib/habitat-sucursales/output
```
