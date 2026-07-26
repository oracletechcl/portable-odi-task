# Pentaho Habitat Sucursales Portfolio Analysis

- **Platform**: Application estate inferred from discovered portfolio artifacts
- **Target**: OCI ODI
- **Scope**: 1 application versions → 1 canonical apps across 1 migration waves
- **Source**: Evidence-first static analysis of the decompiled source/artifact tree, generated module summaries, per-app analyses, strategic canonicalization, and migration-wave outputs.
- **Author**: GPS Code Introspector
- **Date**: July 2026

The following analysis was performed by Oracle Tech Cloud Engineering as part of a presales discovery excersice.

⚠️ Important: All findings in this analysis should be independently validated and re-confirmed during the actual migration execution. Decompiled code may contain artefacts that introduce inaccuracies; recommendations should be treated as directional guidance rather than definitive specifications.

**Generated**: 2026-07-22
**Scope**: 1 applications
**Methodology**: Programmatic static analysis with deterministic enrichment

This delivery is the main navigation entrypoint for the generated portfolio output.

## Quick Navigation by Audience

| You are... | Start here |
|---|---|
| **CTO / CIO** | [Portfolio CTO/CIO Report](strategic-analysis/PORTFOLIO_CTO_CIO.md) |
| **Senior Manager** | [Portfolio Senior Management Report](strategic-analysis/PORTFOLIO_SENIOR_MGMT.md) |
| **Engineering Lead** | [Portfolio Engineering Report](strategic-analysis/PORTFOLIO_ENGINEERING.md) |
| **Migration Planner** | [Migration Waves](strategic-analysis/MIGRATION_WAVES.md) |
| **Application Reviewer** | [App-by-App Analysis](app-by-app-analysis/INDEX.md) |

## Portfolio Snapshot

| Metric | Count |
|---|---|
| Total applications | 1 |
| Pentaho Data Integration apps | 1 |
| SOAP or API services | 0 |
| REST services | 0 |
| Apps with EOL libraries | 0 |

## Main Deliverables

| Path | Description |
|---|---|
| [ANALYSIS_COMPLETE.md](ANALYSIS_COMPLETE.md) | Delivery summary and 3-layer audience guide |
| [app-by-app-analysis/INDEX.md](app-by-app-analysis/INDEX.md) | Per-app `analysis.md` and `deep-dive.md` outputs |
| [code-architecture-analysis/INDEX.md](code-architecture-analysis/INDEX.md) | Per-app code architecture reports |
| [modernization-roadmap/INDEX.md](modernization-roadmap/INDEX.md) | Per-app `roadmap.md` outputs |
| [cloud-native-architecture/README.md](cloud-native-architecture/README.md) | Stage 06 `to-be.md` outputs when an explicit target architecture profile is supplied |
| [coliving-strategy/README.md](coliving-strategy/README.md) | Stage 08 coexistence outputs describing how current and target technologies run in parallel during phased migration |
| [strategic-analysis/APP_INVENTORY.md](strategic-analysis/APP_INVENTORY.md) | Portfolio-level strategic report index |
| [strategic-analysis/CANONICAL_APPS_MIGRATION_LIST.md](strategic-analysis/CANONICAL_APPS_MIGRATION_LIST.md) | Canonical portfolio migration list |
| [strategic-analysis/MIGRATION_WAVES.md](strategic-analysis/MIGRATION_WAVES.md) | Wave sequencing and linked roadmaps |
| [dependency-diagram/dependency-diagram.html](dependency-diagram/dependency-diagram.html) | Interactive dependency graph |
| [LICENSE.md](LICENSE.md) | Delivery license |

## Notes

- This package reflects current-state analysis only.
- Target-state architecture, migration strategy, and co-living outputs require an explicit target profile before Stage 06, Stage 07, or Stage 08 can be generated.
- The generated markdown files are cross-linked for direct navigation between analysis, deep-dive, roadmap, and strategic outputs.

**LICENSE**

Copyright (c) 2024, 2026 Oracle and/or its affiliates.

Licensed under the Universal Permissive License (UPL), Version 1.0.

See [LICENSE.md](LICENSE.md) for more details.
