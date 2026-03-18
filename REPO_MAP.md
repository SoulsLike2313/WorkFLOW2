# REPO_MAP

## Canonical Identity

- Local working source: `E:\CVVCODEX`
- Public safe mirror only: `safe_mirror/main` -> `WorkFLOW2`
- `WorkFLOW2` is not full development workspace.
- Expected canonical workspace root across nodes: `E:\CVVCODEX` unless exception is explicitly documented.
- Path drift from canonical root is non-authoritative for sovereign/rank claims until revalidated.
- External reading channel: targeted ChatGPT bundle export.
- Creator authority path is never tracked; machine role is detected only via env+marker contract.
- Mission Layer status: `accepted / certified baseline`.
- Current canonical phase: `constitution-v1-finalized`.
- Constitutional regime: `lightweight constitutional enforcement`.
- Constitution anchor: `docs/governance/WORKFLOW2_CONSTITUTION_V1.md`.
- Constitution V0 status: `historical bootstrap`.
- Vocabulary anchor: `docs/governance/WORKFLOW2_CANONICAL_VOCABULARY_V1.md`.
- Rapid full-context onboarding: `docs/governance/WORKFLOW2_GPT_ONBOARDING_MASTER_V1.md`.

## Read Order (Bootstrap)

1. `README.md`
2. `workspace_config/workspace_manifest.json`
3. `workspace_config/codex_manifest.json`
4. `REPO_MAP.md`
5. `MACHINE_CONTEXT.md`
6. `docs/INSTRUCTION_INDEX.md`
7. `docs/CURRENT_PLATFORM_STATE.md`
8. `docs/NEXT_CANONICAL_STEP.md`
   constitutional anchor: `docs/governance/WORKFLOW2_CONSTITUTION_V1.md`
   historical predecessor: `docs/governance/WORKFLOW2_CONSTITUTION_V0.md`
   vocabulary freeze anchor: `docs/governance/WORKFLOW2_CANONICAL_VOCABULARY_V1.md`
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
71. `docs/governance/OPERATOR_TASK_PROGRAM_LAYER_BASELINE.md`
72. `docs/governance/OPERATOR_TASK_PROGRAM_BASELINE.md`
73. `docs/governance/OPERATOR_TASK_PROGRAM_CONTRACT.md`
74. `docs/governance/OPERATOR_TASK_PROGRAM_REGISTRY.md`
75. `workspace_config/operator_task_program_registry.json`
76. `scripts/operator_task_program_surface.py`
77. `docs/review_artifacts/OPERATOR_TASK_PROGRAM_GOLDEN_PACK_FINAL.json`
78. `docs/governance/OPERATOR_MISSION_LAYER_BASELINE.md`
79. `docs/governance/OPERATOR_MISSION_BASELINE.md`
80. `docs/governance/OPERATOR_MISSION_CONTRACT.md`
81. `docs/governance/OPERATOR_MISSION_REGISTRY.md`
82. `workspace_config/operator_mission_registry.json`
83. `scripts/operator_mission_surface.py`
84. `docs/review_artifacts/OPERATOR_MISSION_GOLDEN_PACK_FINAL.json`

## Canonical Top-Level Directories

- `projects/` - project roots and manifests.
- `shared_systems/` - shared module library.
- `workspace_config/` - machine policies/manifests.
- `scripts/` - validation, sync, export, startup tooling.
- `docs/` - governance and review artifacts.
- `runtime/` - generated runtime outputs.
- `integration/` - external block intake/review state machine.
- `tasks/` - task_id registry for helper block contracts.

## Project Registry Source

Authoritative registry:

- `workspace_config/workspace_manifest.json` -> `project_registry`

Current canonical active project:

- `platform_test_agent` -> `projects/platform_test_agent`

## External Reading Path

- Public baseline: `WorkFLOW2` safe mirror.
- Request-scoped context/code: `python scripts/export_chatgpt_bundle.py ...`
- Full-repo publication for ChatGPT reading is non-canonical.
- Safe mirror is never sovereign rank proof source.

## Repo Control Center

- Canonical CLI: `python scripts/repo_control_center.py <mode>`
- Primary modes: `status`, `mode`, `integration`, `trust`, `sync`, `bundle`, `evolution`, `full-check`
- Machine-readable outputs:
  - `runtime/repo_control_center/repo_control_status.json`
  - `runtime/repo_control_center/evolution_status.json`
  - `runtime/repo_control_center/machine_mode_status.json`

## Operator Command Layer

- Command surface: `scripts/operator_command_surface.py`
- Registry: `workspace_config/operator_command_registry.json`
- Golden pack: `docs/review_artifacts/OPERATOR_COMMAND_GOLDEN_PACK.json`
- Consistency report: `docs/review_artifacts/OPERATOR_COMMAND_CONSISTENCY_REPORT.md`
- Runtime outputs:
  - `runtime/operator_command_layer/last_execution.json`
  - `runtime/operator_command_layer/command_execution_log.jsonl`
  - `runtime/operator_command_layer/command_surface_status.json`
  - `runtime/operator_command_layer/command_surface_report.md`
  - `runtime/operator_command_layer/operator_command_consistency_check.json`

## Operator Task / Program Layer

- Program surface: `scripts/operator_task_program_surface.py`
- Registry: `workspace_config/operator_task_program_registry.json`
- Golden pack: `docs/review_artifacts/OPERATOR_TASK_PROGRAM_GOLDEN_PACK_FINAL.json`
- Consistency report: `docs/review_artifacts/OPERATOR_TASK_PROGRAM_CERTIFICATION_REPORT.md`
- Runtime outputs:
  - `runtime/repo_control_center/operator_program_status.json`
  - `runtime/repo_control_center/operator_program_report.md`
  - `runtime/repo_control_center/operator_program_checkpoint.json`
  - `runtime/repo_control_center/operator_program_history.json`
  - `runtime/repo_control_center/operator_program_audit_trail.json`
  - `runtime/repo_control_center/operator_task_program_consistency.json`

## Work Package / Mission Layer

- Mission surface: `scripts/operator_mission_surface.py`
- Registry: `workspace_config/operator_mission_registry.json`
- Golden pack: `docs/review_artifacts/OPERATOR_MISSION_GOLDEN_PACK_FINAL.json`
- Certification report: `docs/review_artifacts/OPERATOR_MISSION_CERTIFICATION_REPORT.md`
- Runtime outputs:
  - `runtime/repo_control_center/operator_mission_status.json`
  - `runtime/repo_control_center/operator_mission_report.md`
  - `runtime/repo_control_center/operator_mission_checkpoint.json`
  - `runtime/repo_control_center/operator_mission_history.json`
  - `runtime/repo_control_center/operator_mission_audit_trail.json`
  - `runtime/repo_control_center/operator_mission_consistency.json`

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
- `docs/governance/GOVERNANCE_ACCEPTANCE_GATE.md`

## Federation / Integration Contracts

- `workspace_config/federation_mode_contract.json`
- `workspace_config/creator_mode_detection_contract.json`
- `workspace_config/block_task_schema.json`
- `workspace_config/handoff_package_schema.json`
- `workspace_config/integration_inbox_contract.json`
- `integration/README.md`
- `tasks/README.md`

## Completion Guard

A task cannot be completed unless:

- outputs are repo-visible,
- sync with `safe_mirror/main` is confirmed,
- self-verification is completed.

## Legacy / Non-Canonical

- `origin` (`WorkFLOW`) is legacy remote for this architecture.
- `docs/review_artifacts/PUBLIC_REPO_SANITIZATION_REPORT.md` is legacy/non-canonical evidence and not in active read order.
