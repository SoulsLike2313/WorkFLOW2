# CVVCODEX Workspace

## Canonical Architecture

- Working source of truth: `E:\CVVCODEX`.
- Public safe mirror only: `WorkFLOW2` (`safe_mirror/main`, `https://github.com/SoulsLike2313/WorkFLOW2.git`).
- `WorkFLOW2` is not the full working repository and must receive only approved safe state.
- Official external reading channel for ChatGPT: targeted bundle export (`scripts/export_chatgpt_bundle.py`).
- Governance brain stack is mandatory interpretation layer for all machine/agent execution.
- Federation/Integration layer v1 is mandatory for multi-node collaboration (`creator`, `helper`, `integration` modes).

## Active Project

- Active project slug: `platform_test_agent`
- Active path: `projects/platform_test_agent`
- Canonical project registry source: `workspace_config/workspace_manifest.json`

## Canonical Workflow

1. Local work and validation in `E:\CVVCODEX`.
2. Reconcile docs/manifests/policy against repo reality.
3. Run sync and self-verification gates.
4. Push approved safe state to `safe_mirror/main` (`WorkFLOW2`).
5. For ChatGPT reading, export targeted bundle instead of exposing full repo.

## Current Canonical Phase

- Mission / Work Package Layer: `accepted / certified baseline`.
- Current phase: `Constitution-first`.
- Constraint: no new brain-level implementation layers before constitutional closure.
- Constitutional core: `docs/governance/WORKFLOW2_CONSTITUTION_V0.md`.
- Vocabulary freeze: `docs/governance/WORKFLOW2_CANONICAL_VOCABULARY_V1.md`.

## Federation / Integration Layer V1

Machine role model:

- `creator` - canonical machine with final acceptance rights.
- `helper` - external/full-copy node without creator authority marker; block execution only.
- `integration` - canonical review mode for external handoff packages.

Creator authority contract:

- env var: `CVVCODEX_CREATOR_AUTHORITY_DIR`
- marker file: `creator_authority.json`
- required marker fields:
  - `authority_mode = "creator"`
  - `profile_version = "v1"`
  - `machine_role = "canonical_creator_machine"`

Hard rule:

- full repository copy without valid authority marker is always `helper` mode and cannot declare canonical completion.

## Governance Brain Stack (Mandatory)

### Level 0

- `docs/governance/FIRST_PRINCIPLES.md`
- `docs/governance/WORKFLOW2_CONSTITUTION_V0.md`
- `docs/governance/WORKFLOW2_CANONICAL_VOCABULARY_V1.md`

### Level 1-4 Integration Anchor

- `docs/governance/GOVERNANCE_HIERARCHY.md`
- `docs/governance/SELF_VERIFICATION_POLICY.md`
- `docs/governance/CONTRADICTION_CONTROL_POLICY.md`
- `docs/governance/ADMISSION_GATE_POLICY.md`
- `docs/governance/ANTI_DRIFT_POLICY.md`
- `docs/governance/DEVIATION_INTELLIGENCE_POLICY.md`
- `docs/governance/GOVERNANCE_EVOLUTION_POLICY.md`
- `docs/governance/CREATIVE_REASONING_POLICY.md`
- `docs/governance/AGENT_CHARACTER_PROFILE.md`
- `docs/governance/EVOLUTION_READINESS_POLICY.md`
- `docs/governance/MODEL_MATURITY_MODEL.md`
- `docs/governance/EVOLUTION_SIGNAL_REGISTRY.md`
- `docs/governance/POLICY_EVOLUTION_LOG.md`
- `docs/governance/NEXT_EVOLUTION_CANDIDATE.md`

### Governance v1.1 Hardening Layer

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
- `docs/governance/MACHINE_BOOTSTRAP_CONTRACT.md`
- `docs/governance/CANONICAL_SOURCE_PRECEDENCE.md`
- `docs/governance/ZERO_CONFIG_OPERATION_POLICY.md`
- `docs/governance/GOVERNANCE_ACCEPTANCE_GATE.md`

### Federation / Integration Policies

- `docs/governance/CREATOR_AUTHORITY_POLICY.md`
- `docs/governance/HELPER_NODE_POLICY.md`
- `docs/governance/TASK_ID_EXECUTION_CONTRACT.md`
- `docs/governance/EXTERNAL_BLOCK_HANDOFF_POLICY.md`
- `docs/governance/INTEGRATION_INBOX_POLICY.md`
- `docs/governance/CANONICAL_MACHINE_PROTECTION_POLICY.md`
- `docs/governance/FEDERATION_ARCHITECTURE.md`

## Repo Control Center V1 (CLI-First)

Canonical control entrypoint:

```powershell
python scripts/repo_control_center.py <mode>
```

Supported modes:

- `status`
- `mode`
- `integration`
- `audit`
- `trust`
- `sync`
- `mirror`
- `bundle`
- `evolution`
- `full-check`

Core verdicts:

- TRUST VERDICT: `TRUSTED | WARNING | NOT_TRUSTED`
- SYNC VERDICT: `IN_SYNC | DRIFTED | BLOCKED`
- GOVERNANCE VERDICT: `COMPLIANT | PARTIAL | NON_COMPLIANT`
- ADMISSION VERDICT: `ADMISSIBLE | CONDITIONAL | REJECTED`
- EVOLUTION VERDICT: `HOLD | PREPARE | V2_CANDIDATE | V2_READY | PROMOTE | BLOCKED`
- GOVERNANCE ACCEPTANCE: `PASS | FAIL`

Runtime artifacts:

- `runtime/repo_control_center/repo_control_status.json`
- `runtime/repo_control_center/repo_control_report.md`
- `runtime/repo_control_center/evolution_status.json`
- `runtime/repo_control_center/evolution_report.md`
- `runtime/repo_control_center/machine_mode_status.json`
- `runtime/repo_control_center/machine_mode_report.md`

## Operator Command Execution Layer V1 (CLI-First)

Canonical execution entrypoint:

```powershell
python scripts/operator_command_surface.py <mode>
```

Modes:

- `execute`
- `classify`
- `status`
- `registry`
- `consistency-check`

Execution contract is fixed by:

- `docs/governance/OPERATOR_COMMAND_EXECUTION_CONTRACT.md`
- `workspace_config/operator_command_registry.json`

Execution runtime artifacts:

- `runtime/operator_command_layer/last_execution.json`
- `runtime/operator_command_layer/command_execution_log.jsonl`
- `runtime/operator_command_layer/command_surface_status.json`
- `runtime/operator_command_layer/command_surface_report.md`
- `runtime/operator_command_layer/operator_command_consistency_check.json`

Example commands:

```powershell
python scripts/operator_command_surface.py execute --command "status refresh"
python scripts/operator_command_surface.py execute --command "run validation"
python scripts/operator_command_surface.py execute --command "prepare handoff" --task-id WF-TASK-EXAMPLE-001 --node-id helper-node-01 --dry-run
python scripts/operator_command_surface.py consistency-check
```

## Operator Task / Program Layer V1 (CLI-First)

Canonical execution entrypoint:

```powershell
python scripts/operator_task_program_surface.py <mode>
```

Modes:

- `execute`
- `classify`
- `status`
- `registry`
- `consistency-check`

Program execution contract is fixed by:

- `docs/governance/OPERATOR_TASK_PROGRAM_CONTRACT.md`
- `workspace_config/operator_task_program_registry.json`

Program runtime artifacts:

- `runtime/repo_control_center/operator_program_status.json`
- `runtime/repo_control_center/operator_program_report.md`
- `runtime/repo_control_center/operator_program_checkpoint.json`
- `runtime/repo_control_center/operator_program_history.json`
- `runtime/repo_control_center/operator_program_audit_trail.json`
- `runtime/repo_control_center/operator_task_program_consistency.json`

Example commands:

```powershell
python scripts/operator_task_program_surface.py classify --request "safe status validation report"
python scripts/operator_task_program_surface.py execute --request "safe status validation report"
python scripts/operator_task_program_surface.py execute --request "task handoff review packaging" --task-id WF-TASK-EXAMPLE-001 --node-id helper-node-01
python scripts/operator_task_program_surface.py consistency-check
```

## Work Package / Mission Layer V1 (CLI-First)

Canonical execution entrypoint:

```powershell
python scripts/operator_mission_surface.py <mode>
```

Modes:

- `execute`
- `classify`
- `status`
- `registry`
- `consistency-check`

Mission execution contract is fixed by:

- `docs/governance/OPERATOR_MISSION_CONTRACT.md`
- `workspace_config/operator_mission_registry.json`

Mission runtime artifacts:

- `runtime/repo_control_center/operator_mission_status.json`
- `runtime/repo_control_center/operator_mission_report.md`
- `runtime/repo_control_center/operator_mission_checkpoint.json`
- `runtime/repo_control_center/operator_mission_history.json`
- `runtime/repo_control_center/operator_mission_audit_trail.json`
- `runtime/repo_control_center/operator_mission_consistency.json`

Example commands:

```powershell
python scripts/operator_mission_surface.py classify --request "status consolidation mission"
python scripts/operator_mission_surface.py execute --mission-id mission.wave3a.status_consolidation.complete.v1 --intent creator
python scripts/operator_mission_surface.py consistency-check
```

## Completion Gate (Hard)

Completion is forbidden if any of the following is missing:

- repo-visible truth in tracked files,
- sync parity with `safe_mirror/main`,
- mandatory self-verification pass.

Required checks:

- `git status --short --branch`
- `git rev-parse HEAD`
- `git rev-parse safe_mirror/main`
- `git rev-list --left-right --count HEAD...safe_mirror/main`
- `python scripts/check_repo_sync.py --remote safe_mirror --branch main`

## Targeted ChatGPT Bundle Export

Canonical command:

```powershell
python scripts/export_chatgpt_bundle.py <mode> [options]
```

Modes:

- `context`
- `files --include ...`
- `paths --include ...`
- `project --slug <slug>`
- `request --request-file <file>`
- `audit-runtime --include-rcc-runtime` (only allowlisted RCC runtime reports)

Federated helper workflow commands:

- resolve task: `python scripts/resolve_task_id.py --task-id <TASK_ID>`
- prepare handoff package: `python scripts/prepare_handoff_package.py --task-id <TASK_ID> --node-id <NODE_ID>`
- review inbox (canonical): `python scripts/review_integration_inbox.py`

Protocol reference:

- `docs/CHATGPT_BUNDLE_EXPORT.md`

## Root Map

- `projects/` - project roots.
- `shared_systems/` - reusable systems.
- `workspace_config/` - governance/manifests/policies.
- `scripts/` - execution and validation scripts.
- `docs/` - governance and review artifacts.
- `runtime/` - generated runtime outputs (non-authoritative).
- `integration/` - canonical inbox/review/accepted/rejected/quarantine flow.
- `tasks/` - block task registry for helper execution contracts.

## Source-of-Truth Order

1. `docs/governance/FIRST_PRINCIPLES.md`
2. `docs/governance/GOVERNANCE_HIERARCHY.md`
3. `workspace_config/workspace_manifest.json`
4. `workspace_config/codex_manifest.json`
5. project `PROJECT_MANIFEST.json`
6. this `README.md`
7. review artifacts as evidence only

## Legacy Note

- `origin` (`WorkFLOW`) is legacy/non-canonical for completion and safe mirror sync.
