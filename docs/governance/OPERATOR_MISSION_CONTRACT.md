# OPERATOR_MISSION_CONTRACT

## Scope
Wave 3A safe mission execution contract over accepted governance/query/command/task-program baseline.

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
- `resume_supported`
- `mission_priority`
- `notes`

## Wave 3A Mission Classes
- `certification_mission`
- `readiness_mission`
- `review_prep_mission`
- `status_consolidation_mission`

## Wave 3A Mutability Boundaries
- `READ_ONLY`
- `REFRESH_ONLY`
- `PACKAGE_ONLY`
- `CERTIFICATION_ONLY`

## Execution Rules
- Mission routing is registry-based only (`workspace_config/operator_mission_registry.json`).
- Mission decomposition is program-based only (`workspace_config/operator_task_program_registry.json`).
- Authority/policy/precondition gates are mandatory before mission program execution.
- Mission outcomes are explicit: `SUCCESS`, `BLOCKED`, `FAILED`, `PARTIAL`, `CERTIFIED`.
- Mission layer may execute only safe certification/readiness/review/package flows on Wave 3A.
- Mutation-heavy or uncontrolled autonomous mission behavior is forbidden on Wave 3A.
