# Machine Repo Reading Rules (Execution Gate)

## Rule 1: Task Start Forbidden Without Read Gate

Machine must complete this canonical order before execution:

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

If any mandatory step is skipped: `STATUS: REJECTED`.

## Rule 2: Canonical Identity

- Working source of truth: `E:\CVVCODEX`
- Public safe mirror only: `WorkFLOW2` on `safe_mirror/main`
- Targeted bundle export is canonical external reading channel

## Rule 3: Source-of-Truth Resolution

1. `docs/governance/FIRST_PRINCIPLES.md`
2. `docs/governance/GOVERNANCE_HIERARCHY.md`
3. `workspace_config/workspace_manifest.json`
4. `workspace_config/codex_manifest.json`
5. target `PROJECT_MANIFEST.json`
6. `README.md`
7. review artifacts as non-authoritative evidence

## Rule 4: Active Project Detection

Resolve active project only via:

- `workspace_config/workspace_manifest.json` -> `active_project` + `project_registry`

No folder-name guessing.

## Rule 5: Completion Preconditions

Completion is forbidden without:

1. repo-visible truth
2. sync parity (`HEAD == safe_mirror/main`, divergence `0/0`)
3. self-verification pass
4. contradiction control pass

## Rule 6: ChatGPT Reading Contract

For external machine reading use only:

- `scripts/export_chatgpt_bundle.py`
- `docs/CHATGPT_BUNDLE_EXPORT.md`
- `workspace_config/chatgpt_audit_runtime_allowlist.json` (only for `audit-runtime` mode)

Do not treat full repository publication as required path for task-scoped ChatGPT analysis.

## Rule 7: Legacy Handling

- `origin` (`WorkFLOW`) is legacy/non-canonical for completion decisions.
- `docs/review_artifacts/PUBLIC_REPO_SANITIZATION_REPORT.md` is legacy evidence and excluded from active bootstrap read order.

## Rule 8: Repo Control Center Readiness Gate

Machine must treat `scripts/repo_control_center.py` as control entrypoint for:

1. trust verdict
2. sync verdict
3. governance verdict
4. admission verdict
5. evolution verdict

Mandatory runtime evidence files:

- `runtime/repo_control_center/repo_control_status.json`
- `runtime/repo_control_center/repo_control_report.md`
- `runtime/repo_control_center/evolution_status.json`
- `runtime/repo_control_center/evolution_report.md`

Tracked safe-state evidence contract:

- `workspace_config/SAFE_MIRROR_MANIFEST.json` and `docs/review_artifacts/SAFE_MIRROR_BUILD_REPORT.md` describe `basis_head_sha` (basis commit evidence), not self-referential final commit hash.
- In `tracked_evidence_refresh_commit` mode, current `HEAD` is valid if it is an evidence refresh commit over `basis_head_sha` and `basis..HEAD` changes only safe evidence files.
