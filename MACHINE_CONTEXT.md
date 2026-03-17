# MACHINE_CONTEXT

## Canonical State

- Working source of truth: `E:\CVVCODEX`
- Public safe mirror only: `WorkFLOW2` via `safe_mirror/main`
- Public mirror is not full working repository
- Canonical external reading path: targeted bundles from `scripts/export_chatgpt_bundle.py`
- Governance brain stack is mandatory for interpretation and execution
- Active project: `platform_test_agent`

## Mandatory Bootstrap Read Order

1. `README.md`
2. `workspace_config/workspace_manifest.json`
3. `workspace_config/codex_manifest.json`
4. `REPO_MAP.md`
5. `MACHINE_CONTEXT.md`
6. `docs/INSTRUCTION_INDEX.md`
7. `docs/CURRENT_PLATFORM_STATE.md`
8. `docs/NEXT_CANONICAL_STEP.md`
9. `docs/governance/FIRST_PRINCIPLES.md`
10. `docs/governance/GOVERNANCE_HIERARCHY.md`
11. `docs/governance/SELF_VERIFICATION_POLICY.md`
12. `docs/governance/CONTRADICTION_CONTROL_POLICY.md`
13. `docs/governance/ADMISSION_GATE_POLICY.md`
14. `docs/governance/ANTI_DRIFT_POLICY.md`
15. `docs/governance/DEVIATION_INTELLIGENCE_POLICY.md`
16. `docs/governance/GOVERNANCE_EVOLUTION_POLICY.md`
17. `docs/governance/CREATIVE_REASONING_POLICY.md`
18. `docs/governance/AGENT_CHARACTER_PROFILE.md`
19. `docs/governance/EVOLUTION_READINESS_POLICY.md`
20. `docs/governance/MODEL_MATURITY_MODEL.md`
21. `docs/governance/EVOLUTION_SIGNAL_REGISTRY.md`
22. `docs/governance/POLICY_EVOLUTION_LOG.md`
23. `docs/governance/NEXT_EVOLUTION_CANDIDATE.md`
24. `docs/governance/POLICY_CHANGE_AUTHORITY_POLICY.md`
25. `docs/governance/INCIDENT_AND_ROLLBACK_POLICY.md`
26. `docs/governance/VERIFICATION_DEPTH_POLICY.md`
27. `docs/governance/EVIDENCE_RETENTION_POLICY.md`
28. `docs/governance/PROMOTION_THRESHOLD_POLICY.md`
29. `docs/governance/SECURITY_AND_EXPOSURE_INCIDENT_POLICY.md`
30. `docs/governance/DEPRECATION_AND_RETIREMENT_POLICY.md`
31. `docs/governance/OPERATIONAL_METRICS_POLICY.md`
32. `docs/governance/NOTIFICATION_AND_ESCALATION_POLICY.md`
33. `docs/governance/GOVERNANCE_SCHEMA_VERSIONING_POLICY.md`
34. `docs/governance/MACHINE_BOOTSTRAP_CONTRACT.md`
35. `docs/governance/CANONICAL_SOURCE_PRECEDENCE.md`
36. `docs/governance/ZERO_CONFIG_OPERATION_POLICY.md`
37. `docs/governance/GOVERNANCE_ACCEPTANCE_GATE.md`
38. `scripts/repo_control_center.py`
39. `workspace_config/GITHUB_SYNC_POLICY.md`
40. `workspace_config/AGENT_EXECUTION_POLICY.md`
41. `workspace_config/MACHINE_REPO_READING_RULES.md`
42. target `PROJECT_MANIFEST.json`

## Execution Guardrails

- No completion without repo-visible truth.
- No completion without sync parity (`HEAD == safe_mirror/main`, divergence `0/0`).
- No completion without mandatory self-verification.
- No side work and no silent scope expansion.

## Canonical ChatGPT Request Workflow

1. ChatGPT requests exact files/paths.
2. User passes request to exporter (`request`, `files`, or `paths` mode).
3. Exporter performs safety scan.
4. Exporter writes zip + `CHATGPT_BUNDLE_MANIFEST.json` + `EXPORT_REPORT.md`.
5. User uploads only produced safe bundle.

Audit-safe runtime evidence export:

- use `python scripts/export_chatgpt_bundle.py audit-runtime --include-rcc-runtime`
- only allowlisted `runtime/repo_control_center/*` reports may pass
- standard `files/paths/request/project/context` modes keep runtime blocked

## Repo Control Center Workflow

1. Run `python scripts/repo_control_center.py status`.
2. Run `python scripts/repo_control_center.py trust`.
3. Run `python scripts/repo_control_center.py evolution`.
4. Run `python scripts/repo_control_center.py full-check`.
5. Use generated runtime reports as evidence package for completion/promotion decisions.

## Governance v1.1 Hardening Focus

Hardening layer defines authority, incident handling, verification depth, evidence retention, promotion thresholds, exposure response, lifecycle retirement, metrics, escalation, and schema versioning.

Bootstrap and source-authority contracts:

- `docs/governance/MACHINE_BOOTSTRAP_CONTRACT.md`
- `docs/governance/CANONICAL_SOURCE_PRECEDENCE.md`
- `docs/governance/ZERO_CONFIG_OPERATION_POLICY.md`
- `docs/governance/GOVERNANCE_ACCEPTANCE_GATE.md`

## Non-Canonical Inputs

Do not use as source of truth:

- stale review artifacts,
- runtime-only outputs,
- local untracked files,
- legacy remote assumptions.
