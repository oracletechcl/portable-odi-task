# Portfolio-Wide Application Deduplication Analysis
**Generated:** 2026-07-22

📦 [App Inventory](./APP_INVENTORY.md) | 📋 [Canonical App Inventory](./CANONICAL_APPS_MIGRATION_LIST.md) | 🌊 [Migration Waves](./MIGRATION_WAVES.md) | 🧩 [Deduplication Detail](./DEDUPLICATION.md) | 🏛️ [CTO / CIO Brief](./PORTFOLIO_CTO_CIO.md) | 🧭 [Senior Management Brief](./PORTFOLIO_SENIOR_MGMT.md) | 🛠️ [Engineering Brief](./PORTFOLIO_ENGINEERING.md) | 🤝 [Co-Living Overview](../coliving-strategy/README.md)

## Executive Summary

- **Total apps analyzed:** 1 applications
- **Logical app groups identified:** 1
- **Redundant versions found:** 0 (0.0% of portfolio)
- **Recommendation:** proceed with canonical-first migration planning so downstream artifacts target one preferred implementation per logical app family

| App Base | Family | Proxy Services | Business Services | Canonical | Redundant | Status |
|---|---|---|---|---|---|---|
| [Web](../modernization-roadmap/Web/roadmap.md) | Pentaho Data Integration | unversioned | - | [Web](../modernization-roadmap/Web/roadmap.md) | 0 | SINGLE |

## Dedup Index (All Apps)

| App ID | Status | Canonical | Proxy / Business Relationship | Reason |
|---|---|---|---|---|
| [Web](../modernization-roadmap/Web/roadmap.md) | **CANONICAL** | - | - | Preferred version for `Web` (0 retired variant(s)) |