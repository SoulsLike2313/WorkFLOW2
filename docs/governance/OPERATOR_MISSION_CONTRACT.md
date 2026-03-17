# OPERATOR_MISSION_CONTRACT

## Scope
Wave 3A + Wave 3B mission execution contract over accepted governance/query/command/task-program baseline.

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
- `dependency_set`
- `failure_policy`
- `stop_conditions`
- `delivery_target`
- `review_requirement`
- `escalation_requirement`

## Wave 3A Mission Classes
- `certification_mission`
- `readiness_mission`
- `review_prep_mission`
- `status_consolidation_mission`

## Wave 3B Mission Classes
- `external_review_mission`
- `readiness_transition_mission`
- `handoff_delivery_mission`
- `evidence_consolidation_mission`

## Wave 3A Mutability Boundaries
- `READ_ONLY`
- `REFRESH_ONLY`
- `PACKAGE_ONLY`
- `CERTIFICATION_ONLY`

## Wave 3B Mutability Boundaries
- `OPERATIONAL_ROUTING`
- `PACKAGE_ONLY`
- `CERTIFICATION_ONLY`

## Execution Rules
- Mission routing is registry-based only (`workspace_config/operator_mission_registry.json`).
- Mission decomposition is program-based only (`workspace_config/operator_task_program_registry.json`).
- Authority/policy/precondition gates are mandatory before mission program execution.
- Mission outcomes are explicit: `SUCCESS`, `BLOCKED`, `FAILED`, `PARTIAL`, `CERTIFIED`.
- Mission layer may execute only safe certification/readiness/review/package flows on Wave 3A.
- Wave 3B mission layer may execute controlled multi-program operational flows through registered program sequences only.
- Mutation-heavy or uncontrolled autonomous mission behavior is forbidden on Wave 3A/3B.
- Hidden branching outside registry routing precedence is forbidden.

## Failure / Resume / Delivery Semantics (Wave 3B)
- `dependency_set`: required program chain and mission-level gate dependencies.
- `failure_policy`: supported values:
  - `stop_on_failure`
  - `stop_on_blocked`
  - `continue_on_failure`
- `resume_supported`: mission can resume from `resume_pointer` in checkpoint artifact.
- `stop_conditions`: explicit triggers for stop behavior.
- `delivery_target`: mission-level delivery route for operational outputs.
- `review_requirement`: required review gate before mission acceptance.
- `escalation_requirement`: explicit escalation requirement flag for blocked/critical operational missions.
