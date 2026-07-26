# Validation and Troubleshooting

## Failure map

| Symptom | Likely cause | Corrective action |
| --- | --- | --- |
| Import completes with zero objects | Wrong ZIP root or missing explicit directories | Add `PROJECT.project/` and `Objects/` entries; validate archive |
| Import fails reading `manifest.json` | Symbolic model-version map or non-canonical registry/REST envelope | Rebuild the manifest and objects from a known-good canonical export; run a real import-request gate |
| Imported parameters have null name/type | Runtime parameters normalized incorrectly | Make pipeline/task/REST objects parameter-free and materialize later |
| REST task fails publication | Parameterized URL, invalid expression, or unsupported config | Use concrete post-import URL and canonical/default operation config |
| Backend reports empty JSON body | Payload stored as a plain string | Wrap it as `requestPayload.refValue` model type `JSON_TEXT` |
| Runnable task absent in Console | Pagination | Check Page 2/filter and use CLI `--all` |
| Patch remains unsuccessful | Terminal patch failure ignored | Poll `get-patch`, print errors, and stop immediately on `FAILED` |
| Application create waiter raises client error | CLI waiter does not supply application key | Poll `application get` manually |
| Task run reports missing registry info | Wrong aggregator metadata | Use the published task key as task-run aggregator key |
| OCI cannot reach mock | Wrong address/routing/firewall | Use private IP, reachable VCN path, workspace CIDR rule, and health probe |
| Run succeeds but outputs differ | Incomplete semantic validation | Compare exact file set, schemas, rows, bytes, and golden manifest |

## Offline validation

Require:

- compile and unit/integration tests;
- source-to-target traceability with no unowned stage or branch;
- exact schema/field-order and byte-format checks;
- deterministic build comparison;
- ZIP and tar integrity;
- project validation;
- `bash -n` for all shell scripts;
- checksum verification;
- scan of files and nested archives for secrets, OCIDs, IPs, real endpoints,
  credentials, local config, and private key material.

Use `http://mock-backend.invalid` in tracked REST tasks. Store deploy configuration
outside version control with blank examples only.

## Live validation

Require:

1. expected imported object inventory and statuses;
2. exact project, pipeline, runnable task, and REST identifiers;
3. successful publication patch;
4. published runnable task visible via `list-published-objects --all`;
5. successful zero-parameter run;
6. validation endpoint success;
7. exact expected output count derived from the specification;
8. golden manifest comparison.

Some completed case studies produced eight expected CSVs, but the reusable rule is
to derive cardinality from the approved behavior contract and manifest.

## Security and handoff

Never commit secrets, OCIDs, real IPs/endpoints, private keys, passwords, bucket
tenancy metadata, or local deployment configuration. Preserve the original source
unchanged. Promote the same checksummed immutable release to TEST and PROD; bind
each environment only after import.

The operator handoff must say exactly what the one-stop script does, where to find
the published task (including pagination), why the Run dialog takes no parameters,
where outputs land, and how to inspect service/run failures.
