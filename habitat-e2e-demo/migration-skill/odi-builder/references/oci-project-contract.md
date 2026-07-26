# OCI Project Contract

Treat the user-supplied canonical OCI export as the authority for current model
shape and model versions. Apply these invariants unless a newly exported canonical
artifact proves a platform change.

## Archive envelope

Deliver exactly:

```text
PROJECT-NAME.project.zip
└── PROJECT-NAME.project/
    ├── manifest.json
    └── Objects/
        └── MODEL_TYPE_IDENTIFIER_KEY.json
```

The ZIP must include explicit directory entries for both `PROJECT-NAME.project/`
and `PROJECT-NAME.project/Objects/`. Missing the top-level `.project` envelope or
the explicit `Objects/` entry can produce a successful import request with zero
imported objects.

Use deterministic JSON ordering, object ordering, UUIDv5 keys, ZIP timestamps,
permissions, ownership, and compression inputs. Build twice and byte-compare. Emit
`PROJECT-NAME.project.zip.sha256`.

`manifest.objects` must list `USER_PROJECT` first. Every object filename must be
exactly `MODEL_TYPE_IDENTIFIER_KEY.json`, including its identifier. Otherwise OCI
may interpret a `PIPELINE` as a direct workspace object and reject the import.

## Manifest

Require:

- `version: V1`;
- `exportedWorkspaceOcid: ""`;
- `/Objects/...` paths for every first-class object;
- `objectKeysProvidedForExport` containing only the `USER_PROJECT` key;
- an accurate `referencedObjectsList`, empty for a self-contained export;
- a `modelVersionMap` derived from the supplied/current canonical export.

Do not copy the canonical sample's project identities, object keys, workspace
metadata, task types, or endpoints.

### Live-import compatibility gate

Offline structural validation is necessary but not sufficient. Before claiming an
archive importable, derive the manifest shape from a known-good canonical export:

- `modelVersionMap` keys are OCI numeric model-type IDs (for example `257`,
  `788`, and `17230268181`), not symbolic names such as `PIPELINE`.
- `objectKeysProvidedForExport` is a one-item list containing the exact
  `USER_PROJECT` key.
- Every child object uses the canonical registry envelope, including
  `metadata.aggregatorKey` and an `aggregator` object describing the
  `USER_PROJECT`.
- The REST task must use the complete canonical `executeRestCallConfig`:
  `requestURL.stringValue`, `requestPayload.refValue.modelType=JSON_TEXT`, and
  the nested `dataParam.stringValue` body.
- Every pipeline `nodes` entry is a `FLOW_NODE`. A raw `TASK_OPERATOR` in the
  pipeline's top-level `nodes` list is not an abbreviated equivalent; OCI rejects
  that archive as an unknown or tampered object format.

Perform a real OCI import-request gate before application creation. If OCI says
`Unable to read archive contents for file 'manifest.json'`, stop: rebuild from
the canonical manifest/object schema rather than retrying the same ZIP.
If the same message names a `PIPELINE_*.json` file, inspect that pipeline first.
Reject flat operators, missing START/END nodes, incomplete task stubs, broken
parent references, and nonreciprocal links before rebuilding the ZIP.

## Registry envelope

- First-class exported objects use `objectStatus: 8`.
- Embedded reference stubs use `objectStatus: 1`.
- `USER_PROJECT.metadata` contains `registryVersion: 1`.
- Every first-class child uses `metadata.aggregator`,
  `metadata.aggregatorKey`, and `metadata.registryVersion`.
- The child aggregator key equals the exported project key.
- Do not add top-level `parentRef` or `registryMetadata` to first-class children.
- Keys are unique and deterministic; filenames end with the object's exact key.

Validate current model versions against the supplied canonical artifact. Values
observed in one proven export included USER_PROJECT `20200901`, PIPELINE `20220124`,
FLOW_NODE and links `20211031`, start/end operator `20220523`, task operator
`20210408`, and REST_TASK/PIPELINE_TASK `20230421`; these are evidence, not eternal
defaults.

## Runnable topology

Preserve the Pentaho success and failure graph:

- wrap every START, TASK, and END operator in a `FLOW_NODE`; never place an
  operator directly in the pipeline's `nodes` list;
- require the first flow node to contain `START_OPERATOR`, the last to contain
  `END_OPERATOR`, and intermediate task nodes to contain `TASK_OPERATOR`;
- each `OUTPUT_LINK` lists its destination input key;
- each `INPUT_LINK` has a matching `fromLink`;
- link and operator `parentRef` values point to the owning node/link as required by
  the canonical model;
- every processing failure branch has its own notification task and uses the
  canonical all-failed trigger semantics;
- the pipeline, pipeline task, REST tasks, and imported task stubs are
  parameter-free (`parameters: []`);
- task operators and the pipeline task use an empty `configProviderDelegate`;
- the pipeline task embeds a reference pipeline stub with `nodes: []` and
  `objectStatus: 1`.

Imported declared parameters have been observed to normalize to unnamed/null
parameters and fail publication. Use deployment-time materialization instead.

## REST task shape

A proven publishable mock REST task uses:

- `modelType: REST_TASK`;
- `apiCallMode: SYNCHRONOUS` and
  `executeRestCallConfig.methodType: POST`;
- `isConcurrentAllowed: false`;
- `inputPorts: []`, `outputPorts: []`, and `objectVersion: 1`;
- `parameters: []`, `typedExpressions: []`, and
  `configProviderDelegate: {}`;
- no authentication for a private demo mock;
- `Content-Type: application/json`;
- tracked URL `http://mock-backend.invalid/<route>`;
- `executeRestCallConfig.configValues.parentRef` pointing to the task key;
- payload in `requestPayload.refValue` with `modelType: JSON_TEXT`, whose
  `dataParam.stringValue` contains compact JSON.

A plain request string may import but arrive at the backend as an empty body.
Avoid unproven parameterized URL expressions, response-status expressions, and
operation configuration values. Materialize the private URL and run inputs after
import, before publication.
