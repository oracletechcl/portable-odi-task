# Web — To-Be Cloud-Native Architecture

🏠 [Delivery Home](../../../README.md) | 📘 [Delivery Summary](../../../ANALYSIS_COMPLETE.md) | 🌊 [Migration Waves](../../../strategic-analysis/MIGRATION_WAVES.md) | 🗺️ [Roadmap](../../../modernization-roadmap/Web/roadmap.md) | 📄 [Analysis](../../../app-by-app-analysis/Web/analysis.md) | 🔬 [Deep Dive](../../../app-by-app-analysis/Web/deep-dive.md) | 🚚 [Migration Strategy](./migration-strategy.md) | 🤝 [Co-Living](../../../coliving-strategy/app-by-app/Web/coliving-strategy.md)

## 1. Executive Summary
**Application Name:** Web
**Source Stack:** SOAP + WSDL + Oracle + Database
**Selected Target Stack:** OCI ODI
**Selected Target Platform:** OCI
**Selected Target Runtime:** Running on OCI ODI
**Target Architecture Summary:** This target-state document is bound to the explicit target architecture profile provided for this engagement. It does not reuse an old provider/runtime default.
**Confidence:** Medium-High



## 2. Current-State Constraints That Drive the Target Design
| Constraint | Evidence | Target Design Impact |
|---|---|---|
| Stateful orchestration footprint | Analysis/deep-dive keywords: orchestration | Must be preserved or explicitly redesigned in the chosen target state |
| Contract-first integration footprint | Analysis/deep-dive keywords: soap, wsdl, rest, api | Must be preserved or explicitly redesigned in the chosen target state |
| Database-coupled processing | Analysis/deep-dive keywords: database/sql | Must be preserved or explicitly redesigned in the chosen target state |

## 3. Target Architecture Overview
The target state for `Web` is `OCI ODI using Running on OCI ODI via OCI deployment`. Data, ingress, eventing, security, and observability are taken from the same explicit profile so every downstream to-be document stays aligned.

**Primary Oracle Reference Architecture:** [Implement fine-grained access control on Oracle Integration](https://docs.oracle.com/en/solutions/integration-access-control/index.html)

```mermaid
flowchart LR
    clients["Upstream Users and Systems"]
    runtime["Running on OCI ODI"]
    data["Data platform"]
    clients --> runtime
    runtime --> data
```

## 4. Target Component Model
| Target Component | Responsibility | Inputs / Outputs | Replaces / Evolves From | Evidence Basis |
|---|---|---|---|---|
| Runtime workload | Executes `Web` on `OCI` | Inbound business requests, outbound service calls | Legacy runtime footprint | Explicit target profile + analysis |
| Core runtime | Hosts business or orchestration logic in `Running on OCI ODI` | Contract payloads, state transitions, business outputs | Existing implementation | Explicit target profile |
| Deployment boundary | `OCI deployment` | Release artifact, config, secrets | Legacy deployment model | Explicit target profile |
| Data services | Not specified | Business state reads/writes | Existing operational data layer | Explicit target profile / follow-up analysis |
| Observability plane | Not specified | Logs, metrics, traces, alerts | Legacy operations tooling | Explicit target profile |
| Integration edge | Not specified | Inbound/outbound interfaces | Existing service entry points | Explicit target profile + current-state analysis |

## 5. OCI Services In Scope
| OCI / Platform Component | Selected Service | Evidence Basis |
|---|---|---|
| OCI Platform | OCI | Explicit target profile |
| OCI Runtime | Running on OCI ODI | Explicit target profile |
| OCI Deployment Model | OCI deployment | Explicit target profile |

## 6. OCI Reference-Architecture Mapping
| Inferred OCI Component | Target Role | Inference Basis | Oracle Solutions Reference |
|---|---|---|---|
| OCI API Gateway | Publishes and mediates inbound APIs, contract adapters, and controlled service exposure. | Current-state interface evidence plus live Oracle Solutions API Gateway matches. | [Deploy a disaster recovery solution for OCI API Gateway](https://docs.oracle.com/en/solutions/deploy-data-rcvy-oci-api-gateway/index.html) |
| Oracle Integration | Implements hybrid integration, process automation, adapters, and private connectivity where direct service decomposition is insufficient. | Current-state integration evidence plus live Oracle Solutions integration matches. | [Implement fine-grained access control on Oracle Integration](https://docs.oracle.com/en/solutions/integration-access-control/index.html) |

## 7. Oracle Solutions Reference-Architecture Basis
- [Implement fine-grained access control on Oracle Integration](https://docs.oracle.com/en/solutions/integration-access-control/index.html) — Current-state evidence shows API or contract exposure. Current-state integration footprint needs Oracle Integration guidance. Source summary: Implement fine-grained access control in Oracle Integration 3 integrations, using best practices to ensure secure, role-based access, helping teams manage who can view, modify, or execute integrations with precision and confidence.
- [Deploy a disaster recovery solution for OCI API Gateway](https://docs.oracle.com/en/solutions/deploy-data-rcvy-oci-api-gateway/index.html) — Current-state contracts or API entry points need OCI API mediation and controlled exposure. Current-state evidence shows API or contract exposure. Source summary: Build a cross-region, customer-managed disaster recovery solution for OCI API Gateway.
- [Process bulk data using OCI Data Integration and Oracle Integration](https://docs.oracle.com/en/solutions/oci-bulk-data-integration/index.html) — Current-state evidence shows API or contract exposure. Current-state integration footprint needs Oracle Integration guidance. Source summary: Describes processing bulk data using OCI Data Integration and Oracle Integration Cloud services.
- [Configure resource-based access for REST endpoints using OCI API Gateway](https://docs.oracle.com/en/solutions/configure-resource-based-access-rest/index.html) — Current-state contracts or API entry points need OCI API mediation and controlled exposure. Current-state evidence shows API or contract exposure. Source summary: Learn how to implement fine-grained control for your REST endpoints.
- [Deploy an Oracle API Gateway service in a hybrid environment](https://docs.oracle.com/en/solutions/deploy-oracle-api-gateway-hybrid/index.html) — Current-state contracts or API entry points need OCI API mediation and controlled exposure. Current-state evidence shows API or contract exposure. Source summary: Deploy an Oracle API Gateway hybrid environment with external and internal API environment components.
- [Implement message-level encryption in Oracle Integration using OCI Vault](https://docs.oracle.com/en/solutions/oic-message-level-encryption/index.html) — Current-state evidence shows API or contract exposure. Current-state integration footprint needs Oracle Integration guidance. Source summary: Describes how to implement message-level encryption in Oracle Integration Cloud using OCI Vault Rest APIs.
- [Implement seamless customer inquiry management with OCI Generative AI and Oracle Integration](https://docs.oracle.com/en/solutions/oracle-genai-customer-inquiry-mgmt/index.html) — Current-state integration footprint needs Oracle Integration guidance. Current-state evidence indicates application or data integration needs. Source summary: Implement an integrated, automated solution that can streamline the entire process - from receiving customer inquiries to updating the customer service platform with AI-generated issue resolution steps using OCI Generative AI and Oracle Integration.
- [Implement Retrieval Augmented Generation by using Oracle Integration](https://docs.oracle.com/en/solutions/implement-rag-oci/index.html) — Current-state integration footprint needs Oracle Integration guidance. Current-state evidence indicates application or data integration needs. Source summary: Implement a RAG framework by using semantic search technique to answer a user query on corporate data using low-code or no-code integration platforms such as Oracle Integration service.
- [Use Oracle Integration to Connect E-Business Suite with Financials Cloud](https://docs.oracle.com/en/solutions/oracle-ebs-erpcloud-integration/index.html) — Current-state integration footprint needs Oracle Integration guidance. Current-state evidence indicates application or data integration needs. Source summary: You can provision Oracle E-Business Suite on Oracle Cloud Infrastructure or migrate Oracle E-Business Suite environments from your data center to the cloud.
- [Set up a landing zone architecture with Oracle Integration](https://docs.oracle.com/en/solutions/set-up-lz-oic/index.html) — Current-state integration footprint needs Oracle Integration guidance. Current-state evidence indicates application or data integration needs. Source summary: Learn about the components you can use in a landing zone architecture, when to use those components, and how they interact with landing zone architectural concepts.
- [Establish multi-cloud private network connectivity through Oracle Integration Cloud](https://docs.oracle.com/en/solutions/multi-cloud-with-oic/index.html) — Current-state integration footprint needs Oracle Integration guidance. Current-state evidence indicates application or data integration needs. Source summary: Connect to a service or application running on an AWS private network VPC from Oracle Autonomous Transaction Processing database through Oracle Integration Cloud while bypassing the public internet.
- [Enable a Low Code Modular LLM App Engine using Oracle Integration and OCI Generative AI](https://docs.oracle.com/en/solutions/oci-generative-ai-integration/index.html) — Current-state integration footprint needs Oracle Integration guidance. Current-state evidence indicates application or data integration needs. Source summary: Understand the necessary considerations and recommendations to enable an AI based, modular and event driven LLM App Engine using Oracle Integration and Oracle Cloud Infrastructure Generative AI (OCI Generative AI).

## 8. Target Deployment & Runtime Topology
- Platform: `OCI`
- Runtime: `Running on OCI ODI`
- Deployment model: `OCI deployment`
- Configuration model: `Externalized configuration`
- Secrets model: `Not specified`
- Scaling model: `To be defined from workload evidence`
- Network exposure: `Only declared ingress and integration boundaries should be exposed`

## 9. Target Data Architecture
- Operational data target: `Not specified`
- Data ownership model: `To be confirmed per application`
- State strategy: `Preserve required process/workflow state where evidenced`
- Consistency model: `To be confirmed with business and integration owners`

## 10. Key Integration Obligations
- No strongly evidenced external system names were extracted from the current analysis corpus. Preserve the currently exposed contract boundaries and validate them during implementation.

## 11. Security, Configuration, and Secrets Model
- Security target: `Not specified`
- Identity / access model: `Not specified`
- Configuration model: `Externalized configuration`
- Network policy model: `Least-privilege boundaries to be defined`

## 12. Observability, Reliability, and Operations Model
- Observability target: `Not specified`
- Reliability target: `Availability and recovery objectives not yet specified`
- Deployment safety model: `Progressive rollout / rollback rules to be defined`
- Support model: `Operational ownership to be defined`

## 13. Architecture Decisions, Assumptions, and Open Questions
| Decision | Status | Rationale | Evidence / Missing Evidence |
|---|---|---|---|
| Use explicit target profile instead of generator defaults | Final | Previous outputs were pinned to old implementation assumptions | <target-profile>/target-architecture-profile.json |
| Deploy `OCI ODI using Running on OCI ODI via OCI deployment` | Final | User-selected target state | Explicit target profile |
| Runtime target is `Running on OCI ODI` | Final | Stage 06 and Stage 07 outputs must align to the same target architecture | Explicit target profile |
| Preserve contract compatibility until verified cutover | Proposed | Existing dependency evidence is partial and integration risk remains | Analysis corpus is incomplete |

**Assumptions**
- The supplied target architecture profile is authoritative for provider, platform, runtime, and deployment choices.

**Non-Goals**
- Do not infer a different provider or runtime than the one explicitly supplied.

**Open Questions**
- Confirm app-specific contract compatibility, payload transformations, and cutover sequencing.

## 14. Metadata
- analysis date: 2026-07-22
- analyst / agent: GPS Code Introspector
- target stack: OCI ODI
- target platform: OCI
- target runtime: Running on OCI ODI
- deployment model: OCI deployment
- data platform target: Not specified
- eventing target: Not specified
- api edge target: Not specified
- observability target: Not specified
- security target: Not specified
- primary reference architecture: Implement fine-grained access control on Oracle Integration
- primary reference architecture url: https://docs.oracle.com/en/solutions/integration-access-control/index.html
- profile source: <target-profile>/target-architecture-profile.json
