# OPERATOR_COMMAND_EXECUTION_BASELINE

## Purpose
Define execution-layer baseline on top of accepted governance/query/repo-control stack.

## Baseline Binding
- Execution layer does not override governance engine.
- Query layer remains canonical for operator query responses.
- Command execution is policy-bound and authority-aware.
- Creator/helper/integration boundaries remain enforced.

## Canonical Sources For Execution Decisions
Primary runtime:
- `runtime/repo_control_center/one_screen_status.json`
- `runtime/repo_control_center/repo_control_status.json`

Authority and mode:
- `scripts/detect_machine_mode.py`
- `workspace_config/creator_mode_detection_contract.json`
- `workspace_config/federation_mode_contract.json`

Execution registry and contract:
- `workspace_config/operator_command_registry.json`
- `docs/governance/OPERATOR_COMMAND_EXECUTION_CONTRACT.md`
- `docs/governance/OPERATOR_COMMAND_INTENT_ROUTING.md`

## Waves Covered
- Wave 1A: status/validation/bundle/report commands.
- Wave 1B: handoff/inbox/evidence-routing/policy-reference commands.
- Wave 1C: guarded/creator-only/governance-maintenance/install-remove controlled commands.

## Hard Constraints
- No command can bypass policy checks.
- No command can bypass authority checks.
- Mutable commands default to dry-run unless explicitly allowed.
- Creator-only actions require creator mode + authority present.
- Blocked preconditions must return formal refusal in execution contract.
