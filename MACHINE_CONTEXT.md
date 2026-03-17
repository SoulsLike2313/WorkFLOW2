# MACHINE_CONTEXT

## Canonical State

- Working source of truth: `E:\CVVCODEX`
- Public safe mirror only: `WorkFLOW2` via `safe_mirror/main`
- Public mirror is not full working repository
- Canonical external reading path: targeted bundles from `scripts/export_chatgpt_bundle.py`
- Governance brain stack is mandatory for interpretation and execution
- Active project: `platform_test_agent`
- Mission Layer: `accepted / certified baseline`
- Current canonical phase: `constitution-first`
- New brain-level implementation layers are blocked until constitutional closure.
- Constitutional core path: `docs/governance/WORKFLOW2_CONSTITUTION_V0.md`

## Explainability Quick Files

Read these first when you need plain-language status without deep policy parsing:

- `docs/governance/MACHINE_OPERATOR_GUIDE.md`
- `docs/governance/MACHINE_CAPABILITIES_SUMMARY.md`
- `docs/governance/POLICY_DIGEST.md`
- `runtime/repo_control_center/plain_status.md`
- `runtime/repo_control_center/one_screen_status.json`

## Mandatory Bootstrap Read Order

1. `README.md`
2. `workspace_config/workspace_manifest.json`
3. `workspace_config/codex_manifest.json`
4. `REPO_MAP.md`
5. `MACHINE_CONTEXT.md`
6. `docs/INSTRUCTION_INDEX.md`
7. `docs/CURRENT_PLATFORM_STATE.md`
8. `docs/NEXT_CANONICAL_STEP.md`
   constitution-first anchor: `docs/governance/WORKFLOW2_CONSTITUTION_V0.md`
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
38. `docs/governance/CREATOR_AUTHORITY_POLICY.md`
39. `docs/governance/HELPER_NODE_POLICY.md`
40. `docs/governance/TASK_ID_EXECUTION_CONTRACT.md`
41. `docs/governance/EXTERNAL_BLOCK_HANDOFF_POLICY.md`
42. `docs/governance/INTEGRATION_INBOX_POLICY.md`
43. `docs/governance/CANONICAL_MACHINE_PROTECTION_POLICY.md`
44. `docs/governance/FEDERATION_ARCHITECTURE.md`
45. `scripts/repo_control_center.py`
46. `workspace_config/federation_mode_contract.json`
47. `workspace_config/block_task_schema.json`
48. `workspace_config/handoff_package_schema.json`
49. `workspace_config/integration_inbox_contract.json`
50. `workspace_config/creator_mode_detection_contract.json`
51. `integration/README.md`
52. `tasks/README.md`
53. `scripts/detect_machine_mode.py`
54. `scripts/resolve_task_id.py`
55. `scripts/prepare_handoff_package.py`
56. `scripts/review_integration_inbox.py`
57. `workspace_config/GITHUB_SYNC_POLICY.md`
58. `workspace_config/AGENT_EXECUTION_POLICY.md`
59. `workspace_config/MACHINE_REPO_READING_RULES.md`
60. `docs/governance/OPERATOR_QUERY_LAYER_BASELINE.md`
61. `docs/governance/OPERATOR_QUERY_CATALOG.md`
62. `docs/governance/OPERATOR_RESPONSE_CONTRACT.md`
63. `docs/governance/OPERATOR_INTENT_ROUTING.md`
64. `docs/governance/OPERATOR_COMMAND_EXECUTION_BASELINE.md`
65. `docs/governance/OPERATOR_COMMAND_CATALOG.md`
66. `docs/governance/OPERATOR_COMMAND_EXECUTION_CONTRACT.md`
67. `docs/governance/OPERATOR_COMMAND_INTENT_ROUTING.md`
68. `workspace_config/operator_command_registry.json`
69. `scripts/operator_command_surface.py`
70. `docs/review_artifacts/OPERATOR_COMMAND_GOLDEN_PACK.json`
71. `docs/governance/OPERATOR_PROGRAM_EXECUTION_BASELINE.md`
72. `docs/governance/OPERATOR_PROGRAM_CATALOG.md`
73. `docs/governance/OPERATOR_PROGRAM_EXECUTION_CONTRACT.md`
74. `docs/governance/OPERATOR_PROGRAM_INTENT_ROUTING.md`
75. `workspace_config/operator_program_registry.json`
76. `scripts/operator_program_surface.py`
77. `docs/review_artifacts/OPERATOR_PROGRAM_GOLDEN_PACK.json`
78. `docs/governance/OPERATOR_TASK_PROGRAM_LAYER_BASELINE.md`
79. `docs/governance/OPERATOR_TASK_PROGRAM_BASELINE.md`
80. `docs/governance/OPERATOR_TASK_PROGRAM_CONTRACT.md`
81. `workspace_config/operator_task_program_registry.json`
82. `scripts/operator_task_program_surface.py`
83. `docs/governance/OPERATOR_MISSION_LAYER_BASELINE.md`
84. `docs/governance/OPERATOR_MISSION_BASELINE.md`
85. `docs/governance/OPERATOR_MISSION_CONTRACT.md`
86. `docs/governance/OPERATOR_MISSION_REGISTRY.md`
87. `workspace_config/operator_mission_registry.json`
88. `scripts/operator_mission_surface.py`
89. `docs/review_artifacts/OPERATOR_MISSION_GOLDEN_PACK_FINAL.json`
90. `docs/review_artifacts/OPERATOR_MISSION_CERTIFICATION_REPORT.md`

## Execution Guardrails

- No completion without repo-visible truth.
- No completion without sync parity (`HEAD == safe_mirror/main`, divergence `0/0`).
- No completion without mandatory self-verification.
- No side work and no silent scope expansion.
- Full repo copy without creator marker resolves to helper mode and cannot declare canonical completion.

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

## Operator Command Execution Workflow

1. Classify command: `python scripts/operator_command_surface.py classify --command "<text>"`.
2. Execute command: `python scripts/operator_command_surface.py execute --command "<text>" [flags]`.
3. Validate deterministic routing: `python scripts/operator_command_surface.py consistency-check`.
4. Review command runtime evidence in `runtime/operator_command_layer/`.
5. Re-run `python scripts/repo_control_center.py full-check` after mutable command execution.

## Operator Task / Program Workflow

1. Classify request: `python scripts/operator_task_program_surface.py classify --request "<text>"`.
2. Execute program: `python scripts/operator_task_program_surface.py execute --request "<text>" [flags]`.
3. Validate deterministic routing: `python scripts/operator_task_program_surface.py consistency-check`.
4. Review program runtime evidence in `runtime/repo_control_center/operator_program_*.json|md`.
5. Re-run `python scripts/repo_control_center.py full-check` after guarded mutation programs.

## Work Package / Mission Workflow

1. Classify mission request: `python scripts/operator_mission_surface.py classify --request "<text>"`.
2. Execute mission: `python scripts/operator_mission_surface.py execute --request "<text>" [flags]`.
3. Validate deterministic routing: `python scripts/operator_mission_surface.py consistency-check`.
4. Review mission runtime evidence in `runtime/repo_control_center/operator_mission_*.json|md`.
5. Re-run `python scripts/repo_control_center.py full-check` after guarded creator missions.

## Federation / Integration Workflow

1. Detect mode: `python scripts/detect_machine_mode.py --intent auto`.
2. Resolve block contract: `python scripts/resolve_task_id.py --task-id <TASK_ID>`.
3. Helper prepares delivery: `python scripts/prepare_handoff_package.py ...`.
4. Canonical machine reviews inbox: `python scripts/review_integration_inbox.py`.
5. Final acceptance remains creator-only operation.

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
