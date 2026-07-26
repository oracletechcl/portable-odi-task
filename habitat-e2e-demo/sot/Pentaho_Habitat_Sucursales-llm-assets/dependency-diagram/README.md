# Dependency Diagram — Pentaho Habitat Sucursales
**Generated**: 2026-07-22
## Files
| File | Description |
|---|---|
| `dependency-diagram.html` | Rich interactive dependency graph with sidebar filters |
| `dependency-graph.csv` | Node inventory for the graph |
| `dependency-relationships.csv` | Edge inventory for the graph |
## Publish-Time Placeholders
- `dependency-diagram.html` includes publish-time placeholders `__PUBLISH_REPO_URL__` and `__PUBLISH_BRANCH__` for external GitHub landing links.
- Application nodes expose local delivery links immediately and a published-repo roadmap link once those placeholders are replaced during promotion.
## Behavior
- Uses app deep-dives as the primary evidence source for resource dependencies.
- Adds migration-wave filters when `strategic-analysis/MIGRATION_WAVES.md` exists.
- Preserves application-to-resource and shared-resource application links across runs.