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
38. `docs/governance/CREATOR_AUTHORITY_POLICY.md`
39. `docs/governance/HELPER_NODE_POLICY.md`
40. `docs/governance/TASK_ID_EXECUTION_CONTRACT.md`
41. `docs/governance/EXTERNAL_BLOCK_HANDOFF_POLICY.md`
42. `docs/governance/INTEGRATION_INBOX_POLICY.md`
43. `docs/governance/CANONICAL_MACHINE_PROTECTION_POLICY.md`
44. `docs/governance/FEDERATION_ARCHITECTURE.md`
45. `workspace_config/creator_mode_detection_contract.json`
46. `workspace_config/federation_mode_contract.json`
47. `workspace_config/block_task_schema.json`
48. `workspace_config/handoff_package_schema.json`
49. `workspace_config/integration_inbox_contract.json`
50. `integration/README.md`
51. `tasks/README.md`
52. `scripts/detect_machine_mode.py`
53. `scripts/resolve_task_id.py`
54. `scripts/prepare_handoff_package.py`
55. `scripts/review_integration_inbox.py`
56. `scripts/repo_control_center.py`
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
91. `docs/governance/WORKFLOW2_CONSTITUTION_V1.md`
92. `docs/governance/WORKFLOW2_CONSTITUTION_V0.md`
93. `docs/governance/WORKFLOW2_CANONICAL_VOCABULARY_V1.md`
94. `docs/governance/TRUTH_STATE_MODEL_V1.md`
95. `workspace_config/schemas/truth_state_schema.json`
96. `docs/governance/PROOF_OUTPUT_NAMING_POLICY_V1.md`
97. `docs/governance/CONSTITUTION_PHASE_HYGIENE_CHECKLIST_V1.md`
98. `docs/governance/CONSTITUTIONAL_ADMISSION_FLOW_V1.md`
99. `docs/governance/CONSTITUTION_V1_STABILIZATION_CRITERIA.md`
100. `docs/governance/CONSTITUTION_GATE_SEVERITY_MODEL_V1.md`
101. `docs/governance/CONSTITUTION_OPERATOR_RESPONSE_GUIDE_V1.md`
102. `docs/governance/CONSTITUTION_V1_FINALIZATION_NOTE.md`
103. `docs/governance/CONSTITUTION_V1_SCOPE_BOUNDARIES.md`
104. `docs/review_artifacts/CONSTITUTION_V1_FINALIZATION_REPORT.md`
105. `docs/review_artifacts/POST_CONSTITUTION_V1_OPTIONS.md`
106. `scripts/validation/run_constitution_checks.py`

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
- `runtime/repo_control_center/machine_mode_status.json`
- `runtime/repo_control_center/machine_mode_report.md`

Tracked safe-state evidence contract:

- `workspace_config/SAFE_MIRROR_MANIFEST.json` and `docs/review_artifacts/SAFE_MIRROR_BUILD_REPORT.md` describe `basis_head_sha` (basis commit evidence), not self-referential final commit hash.
- In `tracked_evidence_refresh_commit` mode, current `HEAD` is valid if it is an evidence refresh commit over `basis_head_sha` and `basis..HEAD` changes only safe evidence files.

## Rule 9: Federation Mode Enforcement

- creator authority detection is defined only by:
  - `workspace_config/creator_mode_detection_contract.json`
  - env var `CVVCODEX_CREATOR_AUTHORITY_DIR`
  - marker `creator_authority.json`
- tracked repository must not disclose creator authority directory path.
- full copy without valid authority marker is `helper` mode.
- helper mode cannot declare canonical completion or governance acceptance.
- integration inbox is mandatory entrypoint for external helper deliveries.

## Rule 10: Operator Command Surface Enforcement

- command execution layer entrypoint:
  - `scripts/operator_command_surface.py`
- unified command registry:
  - `workspace_config/operator_command_registry.json`
- mandatory command evidence outputs:
  - `runtime/operator_command_layer/last_execution.json`
  - `runtime/operator_command_layer/command_surface_status.json`
- mutable command actions must be:
  - explicit `--allow-mutation`
  - or dry-run mode with formal execution contract output

## Rule 11: Operator Task / Program Surface Enforcement

- program execution layer entrypoint:
  - `scripts/operator_task_program_surface.py`
- unified program registry:
  - `workspace_config/operator_task_program_registry.json`
- mandatory program evidence outputs:
  - `runtime/repo_control_center/operator_program_status.json`
  - `runtime/repo_control_center/operator_program_report.md`
  - `runtime/repo_control_center/operator_program_checkpoint.json`
  - `runtime/repo_control_center/operator_program_history.json`
  - `runtime/repo_control_center/operator_program_audit_trail.json`
- program execution must emit:
  - checkpoint state
  - step results
  - blocking factors
  - next-step remediation path

## Rule 12: Work Package / Mission Surface Enforcement

- mission execution layer entrypoint:
  - `scripts/operator_mission_surface.py`
- unified mission registry:
  - `workspace_config/operator_mission_registry.json`
- mandatory mission evidence outputs:
  - `runtime/repo_control_center/operator_mission_status.json`
  - `runtime/repo_control_center/operator_mission_report.md`
  - `runtime/repo_control_center/operator_mission_checkpoint.json`
  - `runtime/repo_control_center/operator_mission_history.json`
  - `runtime/repo_control_center/operator_mission_audit_trail.json`
  - `runtime/repo_control_center/operator_mission_consistency.json`
- mission execution must emit:
  - program plan and mission checkpoint state
  - authority/policy/precondition checks
  - completion verdict (`CERTIFIED|SUCCESS|BLOCKED|PARTIAL`)
  - blocking factors and next-step remediation path
