# Pentaho Discovery

Use discovery to turn Pentaho XML and its supporting files into an evidence-backed
behavior contract. Never migrate from filenames or screenshots alone.

## Evidence order

1. Treat the approved migration specification and acceptance criteria as canonical.
2. Use `.kjb` and `.ktr` XML to fill gaps in the specification.
3. Use referenced scripts, SQL, schemas, fixtures, and connection metadata as
   supporting evidence.
4. Use the supplied OCI project only as a packaging-shape reference.
5. Record unresolved behavior in a gap register. Mock a missing boundary, but do not
   invent production semantics, credentials, hosts, or data.

Keep the source of truth read-only. Record relative evidence paths and stable XML
element names; use line numbers only when the source format makes them stable.

## Inventory

Run:

```bash
python3 scripts/inspect_pentaho.py SOURCE_ROOT --output analysis/pentaho-inventory.json
```

Then verify the inventory manually. Capture:

- every job and transformation, including nested references;
- job entries, transformation steps, and their configured types;
- all enabled and disabled hops, evaluation rules, unconditional hops, and error
  branches;
- parameters, variables, environment substitutions, and default values;
- database and JNDI connection names without copying secrets;
- referenced shell scripts, SQL, JavaScript, lookup files, mail settings, and
  filesystem side effects;
- source and target field names, types, order, widths, null rules, encodings,
  delimiters, quoting, line endings, and filename patterns;
- date arithmetic, calendar boundaries, current/previous-period rules, empty-input
  behavior, and retry/idempotency behavior;
- notification recipients and payload semantics as abstract roles, never real
  addresses or credentials.

Search outside the XML for every referenced artifact. A missing extractor, script,
connection, or schema is an evidence gap, not permission to fabricate it.

## Behavior matrix

Produce one row per stage with:

| Field | Required content |
| --- | --- |
| Order | Predecessors and success/failure conditions |
| Inputs | Boundary, format, schema, and cardinality |
| Logic | Exact filters, mappings, joins, derivations, and date rules |
| Outputs | Exact path/name, schema, field order, and byte format |
| Success | Observable completion condition |
| Failure | Error route, notification, retry, and partial-output behavior |
| Evidence | Spec/XML/script/fixture anchors |
| Confidence | Proven, inferred, or unresolved |

Derive expected object and output counts from this matrix. Never bake a case-study
count into the reusable migration workflow.

## Boundary decision

Classify each dependency as:

- pure transformation that belongs in locally testable Python, PySpark, or SQL;
- orchestration that belongs in an OCI Data Integration pipeline;
- available external service that needs an explicit deployment-time binding; or
- unavailable service that needs a deterministic fixture-backed mock.

`/health` proves only service liveness. It must not execute business processing.
