# REPO_MAP

## Canonical Identity

- Local working source: `E:\CVVCODEX`
- Public safe mirror only: `safe_mirror/main` -> `WorkFLOW2`
- `WorkFLOW2` is not full development workspace.
- External reading channel: targeted ChatGPT bundle export.

## Read Order (Bootstrap)

1. `README.md`
2. `workspace_config/workspace_manifest.json`
3. `workspace_config/codex_manifest.json`
4. `MACHINE_CONTEXT.md`
5. `docs/INSTRUCTION_INDEX.md`
6. `docs/CURRENT_PLATFORM_STATE.md`
7. `docs/NEXT_CANONICAL_STEP.md`
8. `docs/governance/FIRST_PRINCIPLES.md`
9. `docs/governance/GOVERNANCE_HIERARCHY.md`
10. `docs/governance/SELF_VERIFICATION_POLICY.md`
11. `docs/governance/CONTRADICTION_CONTROL_POLICY.md`
12. `docs/governance/ADMISSION_GATE_POLICY.md`
13. `docs/governance/ANTI_DRIFT_POLICY.md`
14. `docs/governance/DEVIATION_INTELLIGENCE_POLICY.md`
15. `docs/governance/GOVERNANCE_EVOLUTION_POLICY.md`
16. `docs/governance/CREATIVE_REASONING_POLICY.md`
17. `docs/governance/AGENT_CHARACTER_PROFILE.md`
18. `docs/governance/EVOLUTION_READINESS_POLICY.md`
19. `docs/governance/MODEL_MATURITY_MODEL.md`
20. `docs/governance/EVOLUTION_SIGNAL_REGISTRY.md`
21. `docs/governance/POLICY_EVOLUTION_LOG.md`
22. `docs/governance/NEXT_EVOLUTION_CANDIDATE.md`
23. `docs/governance/POLICY_CHANGE_AUTHORITY_POLICY.md`
24. `docs/governance/INCIDENT_AND_ROLLBACK_POLICY.md`
25. `docs/governance/VERIFICATION_DEPTH_POLICY.md`
26. `docs/governance/EVIDENCE_RETENTION_POLICY.md`
27. `docs/governance/PROMOTION_THRESHOLD_POLICY.md`
28. `docs/governance/SECURITY_AND_EXPOSURE_INCIDENT_POLICY.md`
29. `docs/governance/DEPRECATION_AND_RETIREMENT_POLICY.md`
30. `docs/governance/OPERATIONAL_METRICS_POLICY.md`
31. `docs/governance/NOTIFICATION_AND_ESCALATION_POLICY.md`
32. `docs/governance/GOVERNANCE_SCHEMA_VERSIONING_POLICY.md`
33. `scripts/repo_control_center.py`
34. `workspace_config/GITHUB_SYNC_POLICY.md`
35. `workspace_config/AGENT_EXECUTION_POLICY.md`
36. `workspace_config/MACHINE_REPO_READING_RULES.md`

## Canonical Top-Level Directories

- `projects/` - project roots and manifests.
- `shared_systems/` - shared module library.
- `workspace_config/` - machine policies/manifests.
- `scripts/` - validation, sync, export, startup tooling.
- `docs/` - governance and review artifacts.
- `runtime/` - generated runtime outputs.

## Project Registry Source

Authoritative registry:

- `workspace_config/workspace_manifest.json` -> `project_registry`

Current canonical active project:

- `platform_test_agent` -> `projects/platform_test_agent`

## External Reading Path

- Public baseline: `WorkFLOW2` safe mirror.
- Request-scoped context/code: `python scripts/export_chatgpt_bundle.py ...`
- Full-repo publication for ChatGPT reading is non-canonical.

## Repo Control Center

- Canonical CLI: `python scripts/repo_control_center.py <mode>`
- Primary modes: `status`, `trust`, `sync`, `bundle`, `evolution`, `full-check`
- Machine-readable outputs:
  - `runtime/repo_control_center/repo_control_status.json`
  - `runtime/repo_control_center/evolution_status.json`

## Governance v1.1 Hardening Policies

- `docs/governance/POLICY_CHANGE_AUTHORITY_POLICY.md`
- `docs/governance/INCIDENT_AND_ROLLBACK_POLICY.md`
- `docs/governance/VERIFICATION_DEPTH_POLICY.md`
- `docs/governance/EVIDENCE_RETENTION_POLICY.md`
- `docs/governance/PROMOTION_THRESHOLD_POLICY.md`
- `docs/governance/SECURITY_AND_EXPOSURE_INCIDENT_POLICY.md`
- `docs/governance/DEPRECATION_AND_RETIREMENT_POLICY.md`
- `docs/governance/OPERATIONAL_METRICS_POLICY.md`
- `docs/governance/NOTIFICATION_AND_ESCALATION_POLICY.md`
- `docs/governance/GOVERNANCE_SCHEMA_VERSIONING_POLICY.md`

## Bootstrap And Precedence Contracts

- `docs/governance/MACHINE_BOOTSTRAP_CONTRACT.md`
- `docs/governance/CANONICAL_SOURCE_PRECEDENCE.md`
- `docs/governance/ZERO_CONFIG_OPERATION_POLICY.md`

## Completion Guard

A task cannot be completed unless:

- outputs are repo-visible,
- sync with `safe_mirror/main` is confirmed,
- self-verification is completed.

## Legacy / Non-Canonical

- `origin` (`WorkFLOW`) is legacy remote for this architecture.
- `docs/review_artifacts/PUBLIC_REPO_SANITIZATION_REPORT.md` is legacy/non-canonical evidence and not in active read order.
