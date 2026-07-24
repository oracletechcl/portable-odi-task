# Live OCI Operations

Use this sequence only after the user authorizes live deployment. All list
operations use `--all`; never assume the first console page or first CLI result is
complete.

## Preflight

Validate every required argument, OCI authentication, file/checksum, identifier,
ISO date, IP/port, SSH key mode, SSH reachability, workspace, subnet, and bucket
before mutation. Reject duplicate matching identities rather than selecting the
first one silently.

## Import and materialize

1. Upload the immutable `.project.zip` to Object Storage with overwrite explicitly
   enabled for the requested object.
2. Create an import request using conflict resolution `REPLACE`; exclude data-asset
   references unless the design explicitly needs them.
3. Poll import status to success, failure, or timeout. On failure, print the full
   request response and stop.
4. Inventory imported object counts, types, identifiers, keys, and
   `objectStatus: 8`; derive expected counts from the manifest.
5. List all imported REST tasks from the generated inventory.
6. For every REST task, read current key, object version, template URL, and
   `JSON_TEXT` payload. Replace the `.invalid` host and runtime placeholders with
   the VM private URL and explicit run inputs.
7. Reject unknown templates and any unresolved `${...}` token.
8. Update the same task key/version with `parameters: []` and force only after the
   complete replacement config is validated.

Tracked artifacts remain endpoint-free. Environment materialization does not
rebuild the immutable release.

## Application and publication

Find or create the exact application identifier. Creation requires model type
`INTEGRATION_APPLICATION`. Do not rely on a known-broken CLI creation waiter that
fails to pass `application_key`; poll `application get --application-key` and stop
on failure or timeout.

Find the runnable `PIPELINE_TASK` by the explicit generated identifier using
`--all`. Publish only that key with an application `PUBLISH` patch; dependencies
publish transitively.

Poll `get-patch`. If status becomes `FAILED`, print patch errors and exit
immediately. Do not keep polling a terminal failure. Verify publication with
`list-published-objects --identifier <task> --all`.

The Console typically paginates tasks. In a case study with ten REST dependencies,
the runnable pipeline task appeared on Page 2. Use **Filter by name** or the next
page rather than concluding the task is missing.

## Run

The published run uses zero parameters because endpoints and run inputs were
materialized before publication. Run from the Console or create a task run with the
published object's key. When constructing registry metadata, the aggregator key is
the published task key, not the project key.

Poll the task run to a terminal state. A successful import or publish patch is not a
successful integration run.

## Idempotency

- Re-upload the same immutable object intentionally.
- Import with `REPLACE`.
- Reuse an application only by exact identifier.
- Refresh object versions before updates.
- Generate a unique patch identifier per publish attempt.
- Emit `READY` only after mock health, import, materialization, application state,
  patch success, and published task verification all pass.
