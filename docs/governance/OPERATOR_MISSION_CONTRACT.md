# OPERATOR_MISSION_CONTRACT

## Scope
Mission layer execution contract over accepted governance/query/command/task-program baseline.

## Required Mission Execution Shape
- `mission_class`
- `mission_id`
- `resolved_goal`
- `mission_scope`
- `non_goals`
- `authority_check`
- `policy_check`
- `preconditions`
- `program_plan`
- `current_program`
- `mission_checkpoint_state`
- `execution_result`
- `artifacts_produced`
- `state_change`
- `blocking_factors`
- `acceptance_criteria`
- `completion_verdict`
- `next_step`
- `evidence_source`

## Optional Fields
- `mission_priority`
- `resume_supported`
- `rollback_supported`
- `escalation_requirement`
- `mutability_level`
- `dependency_set`
- `stop_conditions`
- `operator_confirmation_required`
- `notes`

## Execution Rules
- Mission routing is registry-based only.
- Mission decomposition is program-based only (`workspace_config/operator_task_program_registry.json`).
- Authority/policy/precondition gates are mandatory before mission program execution.
- Mission outcomes must be explicit: `SUCCESS`, `BLOCKED`, `FAILED`, `PARTIAL`, `CERTIFIED`.
- Uncontrolled autonomous mission planning is forbidden.
