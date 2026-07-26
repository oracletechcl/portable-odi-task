# Modernization Roadmap — Web

🏠 [Delivery Home](../../README.md) | 📘 [Delivery Summary](../../ANALYSIS_COMPLETE.md) | 🗂️ [Roadmap Index](../INDEX.md) | 🌊 [Migration Waves](../../strategic-analysis/MIGRATION_WAVES.md) | 📊 [View Analysis](../../app-by-app-analysis/Web/analysis.md) | 🔬 [Deep Dive](../../app-by-app-analysis/Web/deep-dive.md) | ☁️ [To-Be](../../cloud-native-architecture/canonical-app-to-be/Web/to-be.md) | 🤝 [Co-Living](../../coliving-strategy/app-by-app/Web/coliving-strategy.md)

**Generated**: 2026-07-22

---

## 1. App Snapshot

| Attribute | Value |
|---|---|
| **App ID** | `Web` |
| **Domain** | Enterprise Services |
| **Type** | Source Module |
| **Complexity** | LOW |
| **Source Files** | 8 |
| **Tech Stack** | Not detected |

## 2. Key Dependencies

| Category | Dependencies |
|---|---|
| None detected | — |

## 3. 6R Options Assessment

| Strategy | Score (1–5) | Notes |
|---|---|---|
| Retire | 1 | Active application — do not retire |
| Retain | 2 | Not recommended |
| Rehost | 1 | Platform-specific packaging; rehost insufficient |
| Replatform | 2 | Partial; still needs code changes |
| Refactor | 3 | Reduce coupling; extract shared libraries |
| Rearchitect | 3 | Optional; replatform may suffice |

## 4. Recommended Path

**Primary Strategy**: Replatform + Rearchitect

**Rationale**: Application requires runtime standardisation plus targeted framework modernisation

**Selected Destination**: OCI ODI using Running on OCI ODI via OCI deployment

**Evidence-Based Receiving Stack Recommendation**: OCI ODI using Running on OCI ODI

**Target Pattern**: OCI ODI using Running on OCI ODI via OCI deployment

## 5. Target Platform Pattern

**Recommended Direction**: OCI ODI using Running on OCI ODI via OCI deployment

**Receiving Stack**: OCI ODI using Running on OCI ODI

**Chosen Destination Profile**: OCI ODI using Running on OCI ODI via OCI deployment

| Platform Capability | Role |
|---|---|
| OCI Container Registry / Artifact Registry | Build artifact or image storage |
| OCI Vault | Credentials / secrets management |
| OCI Logging | Application log aggregation |
| OCI Monitoring | Metrics + alerting |

## 5A. Internet-Backed Migration Pattern

**Origin Stack Profile**: Mixed or partially classified application workload

**Pattern Family**: Evidence-first runtime stabilization before target cutover

**Registry Key**: `generic`

**Authoritative References Reflected In This Plan**:
- Kubernetes readiness and configuration guidance
- Containerization and externalized configuration best practices

### Step-by-Step Migration Instructions

1. **Close classification gaps first**
   Action: Resolve missing runtime, integration, and packaging evidence before committing to a target-specific migration path for OCI ODI using Running on OCI ODI via OCI deployment.
   Exit criteria: Source runtime, deployment style, and integration boundaries are explicit enough to choose a stable target pattern.

2. **Standardize the delivery artifact**
   Action: Produce a repeatable build and deployment artifact that can be promoted onto OCI ODI using Running on OCI ODI via OCI deployment without workstation-specific steps.
   Exit criteria: Build and deployment automation can recreate the artifact deterministically.

3. **Externalize configuration before scaling**
   Action: Move environment-specific settings, secrets, and service endpoints into platform-managed configuration aligned to OCI ODI using Running on OCI ODI via OCI deployment.
   Exit criteria: The same promoted artifact can run across environments without code edits.

## 6. Data & Integration

| Category | Finding |
|---|---|
| Direct relational access sites | 0 |
| SQL statements | 0 |
| ORM/entities/models | 0 |
| Async queues | 0 |
| Async topics | 0 |
| Contract endpoints | 0 |
| HTTP/API endpoints | 0 |

## 7. Security Baseline

- ☐ Add OWASP Top-10 scan (SAST/DAST) before migration sign-off

## 8. Audience Summaries

### 8A. CTO/CIO Summary

- **What it does**: Enterprise Services service; Source Module
- **Risk**: LOW complexity; Pentaho Data Integration (Kettle) runtime
- **Target pattern**: OCI ODI using Running on OCI ODI via OCI deployment
- **Destination status**: OCI ODI using Running on OCI ODI via OCI deployment

### 8B. Senior Management Summary

| Item | Value |
|---|---|
| Strategy | Replatform + Rearchitect |
| Receiving stack | OCI ODI using Running on OCI ODI |
| Key risk | Test coverage for migration validation |
| Execution model | Cross-functional application, platform, and validation ownership |

### 8C. Engineering Detail

- **Receiving stack to engineer toward**: OCI ODI using Running on OCI ODI
- **Migration pattern registry entry**: generic (Evidence-first runtime stabilization before target cutover)
- **Build and packaging focus**: Standardize packaging and deployment automation
- **Data migration focus**: 0 relational access site(s), 0 SQL fragment(s), 0 stored procedure reference(s)
- **Integration migration focus**: 0 SOAP endpoint(s), 0 REST endpoint(s), 0 async channel(s)
- **Security focus**: No EOL library signal; validate credentials, secrets, and endpoint protection
- **Validation gate**: complete regression, integration, and rollout-readiness checks before platform cutover.
## 9. Assumptions & Unknowns

| Assumption | Risk | Mitigation |
|---|---|---|
| Test coverage ≥ 60% exists | HIGH if absent | Build regression suite first |
| No undocumented remote clients | MEDIUM | Search codebase for named service lookups and outbound integrations |
| Database schema is migratable | MEDIUM | Run schema analysis against target DB |
| Final Stage 06 destination supplied | LOW | Profile loaded from explicit target architecture input |

---

> **Note**: This roadmap is generated automatically from current static evidence. If a later stage requires user-specific target-state choices, the skill should ask in chat instead of emitting manual prompt instructions.

*Generated: 2026-07-22 — Programmatic analysis; validate with domain experts*
