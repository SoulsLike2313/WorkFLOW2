# OPERATOR_PROGRAM_EXECUTION_BASELINE

## Purpose
Define the Task/Program execution layer over accepted governance, query, and operator command execution baselines.

## Baseline Binding
- Program layer does not replace governance engine.
- Query layer remains canonical for operator query responses.
- Command layer remains canonical execution unit for program steps.
- Program orchestration is policy-bound, authority-aware, checkpointed, and auditable.

## Canonical Sources For Program Decisions
Program runtime truth:
- `runtime/repo_control_center/one_screen_status.json`
- `runtime/repo_control_center/repo_control_status.json`

Authority and mode:
- `scripts/detect_machine_mode.py`
- `workspace_config/creator_mode_detection_contract.json`
- `workspace_config/federation_mode_contract.json`

Program contracts:
- `workspace_config/operator_program_registry.json`
- `docs/governance/OPERATOR_PROGRAM_EXECUTION_CONTRACT.md`
- `docs/governance/OPERATOR_PROGRAM_INTENT_ROUTING.md`

Execution units:
- `scripts/operator_command_surface.py`
- `workspace_config/operator_command_registry.json`

## Waves Covered
- Wave 2A: task contract, program registry, safe read/validate/report programs, checkpoint model.
- Wave 2B: multi-step operational programs, handoff/review/packaging, deterministic routing, failure/resume model.
- Wave 2C: creator-guarded programs, approval/escalation controls, controlled mutation flows, rollback/stop behavior.

## Hard Constraints
- No program can bypass authority checks.
- No program can bypass policy checks.
- No program can execute mutable flow without explicit mutation guard and confirmation.
- Creator-only programs require creator mode + authority present.
- Program failures must produce formal contract evidence and checkpoint state.
