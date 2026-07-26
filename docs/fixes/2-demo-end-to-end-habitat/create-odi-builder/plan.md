# Plan: Standalone ODI Builder Skill

## Goal

Create an isolated `odi-builder` skill that migrates Pentaho KJB/KTR projects to
OCI Data Integration end to end. Preserve every proven packaging, mock, deployment,
publication, pagination, execution, and validation caveat from the Habitat
Sucursales migration without depending on another workflow skill.

## Scope

- Standalone skill instructions and metadata.
- Pentaho discovery, SDD/TDD, OCI project, mock deployment, live OCI, and
  troubleshooting references.
- Standard-library discovery, scaffolding, and OCI project validation tools.
- Reusable specification, traceability, deployment, and operator templates.
- Structural, security, functional, and negative-fixture tests.
- Forward test against the supplied Pentaho source and proven OCI artifact.
- README Mermaid diagram for the working Sucursales POC.

## Plan

- [x] Extract reusable knowledge and live OCI caveats.
- [x] Write the initial failing standalone-skill contract.
- [x] Initialize with the official skill-creator scaffolder.
- [x] Implement `SKILL.md`, references, scripts, assets, and agent metadata.
- [x] Expand tests for isolation, genericity, discovery, scaffolding, and malformed
  OCI exports.
- [x] Forward-test discovery and project validation against Habitat evidence.
- [x] Add and verify the separate-agent Mermaid architecture diagram.
- [x] Run migration regression, repository checks, secret scans, and artifact
  integrity checks.
- [x] Commit and push intended files while excluding SOT and local credentials.

## Agent roster and file ownership

| Agent | Assignment | Files |
| --- | --- | --- |
| Root | Skill implementation, tests, integration, validation, commit | Skill tree, tests, fix docs |
| `odi_skill_knowledge` | Read-only reusable caveat inventory | None |
| `odi_skill_verification` | Read-only forward-test/contract review | None |
| `sucursales_mermaid` | POC architecture diagram | Migrated demo `README.md` only |

The root agent reviewed and corrected the diagram's `/v1/periods` method to POST,
matching the mock dispatcher and OCI REST task.

## Protected inputs

The original SOT, canonical project samples, SSH keys, ignored deployment config,
and environment-specific identifiers are not part of the commit.
