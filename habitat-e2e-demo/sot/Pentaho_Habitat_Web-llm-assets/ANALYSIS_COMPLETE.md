# Code Introspector — Pentaho Habitat Web Portfolio Analysis Delivery

**Delivery Date**: 2026-07-22
**Scope**: 1 modules | Programmatic static analysis
**Methodology**: Evidence-first (all claims linked to source code scan)

---

> **HOW TO USE THIS DOCUMENT**
>
> | Audience | Go To | Reading Time |
> |----------|-------|--------------|
> | **CIO / CTO** | [Layer 1: Executive View](#layer-1--executive-view-ciocto) | 5 minutes |
> | **Senior Management** | [Layer 2: Management View](#layer-2--management-view-senior-management) | 15 minutes |
> | **Engineering Teams** | [Layer 3: Engineering View](#layer-3--engineering-view-technical-teams) | Reference |

---

# LAYER 1 — Executive View (CIO/CTO)

## Portfolio Health Snapshot

| Dimension | Status | Headline Risk |
|-----------|--------|---------------|
| **Observability** | 🟠 UNKNOWN | Verify logging/tracing coverage before migration |

## What This Portfolio Is

This analysis covers **1 software modules** from the **Pentaho Habitat Web** portfolio.
Analysis was performed by programmatic static analysis of source code.

## Automation Coverage

> This delivery was generated automatically from deterministic analysis and enrichment steps.
>
> If a downstream stage depends on user-selected inputs such as target architecture,
> the responsible skill must ask in chat rather than writing manual prompt instructions
> into the output files.

---

# LAYER 2 — Management View (Senior Management)

## Program Overview

| Category | Count |
|---|---|
| Total modules | 1 |
| SOAP/API services | 0 |
| Workflow/BPEL processes | 0 |
| Container-ready Java services | 0 |
| REST services | 0 |
| Modules with EOL JARs | 0 |

See [strategic-analysis/PORTFOLIO_SENIOR_MGMT.md](strategic-analysis/PORTFOLIO_SENIOR_MGMT.md) for tier breakdown and [strategic-analysis/MIGRATION_WAVES.md](strategic-analysis/MIGRATION_WAVES.md) for canonical wave sequencing.

---

# LAYER 3 — Engineering View (Technical Teams)

## Deliverables Inventory

| Artifact | Count | Location |
|---|---|---|
| App-by-app analysis | 1 | `app-by-app-analysis/{module}/analysis.md` |
| Deep-dive reports (B0–B9) | 1 | `app-by-app-analysis/{module}/deep-dive.md` |
| Forms / Reports UI mockups | 1 | `app-by-app-analysis/{module}/UI/index.html` when applicable |
| Code architecture analysis | 1 | `code-architecture-analysis/{module}/analysis.md` |
| Modernization roadmaps | 1 | `modernization-roadmap/{module}/roadmap.md` |
| Co-living strategy | canonical apps + portfolio overview | `coliving-strategy/` when Stage 08 is generated |
| Portfolio INDEX | 1 | `app-by-app-analysis/INDEX.md` |
| Dependency graph (HTML) | 1 | `dependency-diagram/dependency-diagram.html` |
| Strategic analysis | 12 docs + app briefs + JSON manifests | `strategic-analysis/` |

## Deep-Dive Section Reference (B0–B9)

| Section | Name | Use |
|---|---|---|
| **B0** | Evidence Index | Jump to source files |
| **B1** | Interface / Entry-Point Contracts | Interface names, routes, exposed methods |
| **B2** | Integration / Request Flow | Service operations, route declarations, process flow |
| **B3** | Core Library Dependencies | JARs, versions |
| **B4** | Code Complexity Profile | NLOC, cyclomatic, hotspots |
| **B5** | Modernization Impact Deltas | Per-feature migration impact |
| **B6** | Recommendations | Next steps and ownership |
| **B7** | Software Requirements Spec | FRs, NFRs, SLAs |
| **B8** | Architecture Diagram | Tier diagram |
| **B9** | Data Flow & Processing Logic | Input/processing/output |

## File Structure Reference

```
output/Pentaho Habitat Web/
├── ANALYSIS_COMPLETE.md               ← This file
├── app-by-app-analysis/
│   ├── INDEX.md
│   └── {{module}}/analysis.md + deep-dive.md + UI/
├── code-architecture-analysis/
│   ├── INDEX.md
│   └── {{module}}/analysis.md + evidence-index.md
├── dependency-diagram/
│   ├── dependency-diagram.html
│   ├── dependency-graph.csv
│   └── dependency-relationships.csv
├── modernization-roadmap/
│   ├── INDEX.md
│   └── {{module}}/roadmap.md
├── coliving-strategy/
│   ├── README.md
│   └── {{app}}/coliving-strategy.md
├── strategic-analysis/
│   ├── APP_INVENTORY.md
│   ├── PORTFOLIO_CTO_CIO.md
│   ├── PORTFOLIO_SENIOR_MGMT.md
│   ├── PORTFOLIO_ENGINEERING.md
│   ├── DEDUPLICATION.md
│   ├── CANONICAL_APPS_MIGRATION_LIST.md
│   ├── MIGRATION_WAVES.md
│   ├── CANONICAL_APPS.json
│   ├── REDUNDANT_APPS.json
│   ├── PORTFOLIO_CTO_CIO_WITH_DEDUP.md
│   ├── PORTFOLIO_SENIOR_MGMT_WITH_DEDUP.md
│   ├── PORTFOLIO_ENGINEERING_DEDUP.md
│   └── apps/{{app_id}}.md
```

*Generated: 2026-07-22 | Modules: 1 | Method: Programmatic static analysis*
