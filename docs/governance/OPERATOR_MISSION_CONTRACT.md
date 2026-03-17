# OPERATOR_MISSION_CONTRACT

## Scope
Wave 3A + Wave 3B + Wave 3C mission execution contract over accepted governance/query/command/task-program baseline.

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
- `mutability_level`
- `rollback_supported`
- `creator_authority_required`
- `approval_basis`
- `audit_trail_reference`
- `acceptance_transition_semantics`

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

## Wave 3C Mission Classes
- `guarded_baseline_transition_mission`
- `creator_only_certification_mission`
- `controlled_upgrade_mission`
- `blocked_mutation_mission`

## Mission Mutability Levels
- `READ_ONLY`
- `REFRESH_ONLY`
- `PACKAGE_ONLY`
- `REVIEW_DELIVERY`
- `GUARDED_STATE_CHANGE`
- `CREATOR_ONLY_TRANSITION`

## Execution Rules
- Mission routing is registry-based only (`workspace_config/operator_mission_registry.json`).
- Mission decomposition is program-based only (`workspace_config/operator_task_program_registry.json`).
- Authority/policy/precondition gates are mandatory before mission program execution.
- Mission outcomes are explicit: `SUCCESS`, `BLOCKED`, `FAILED`, `PARTIAL`, `CERTIFIED`.
- Mission layer may execute only safe certification/readiness/review/package flows on Wave 3A.
- Wave 3B may execute controlled multi-program operational review/delivery flows only.
- Wave 3C may execute guarded creator missions only with explicit mutability/authority gates.
- Mutation-heavy or uncontrolled autonomous mission behavior is forbidden.
- Hidden branching outside registry routing precedence is forbidden.

## Guarded Mission Semantics (Wave 3C)
- `creator_authority_required=true` enforces creator mode + valid authority marker.
- `mutability_level` must be one of supported mission mutability levels.
- `rollback_supported=true` requires rollback-required reporting for failed guarded transitions.
- `approval_basis` must reference policy documents that authorize the guarded transition.
- `audit_trail_reference` must point to mission-level auditable runtime artifact.
- `acceptance_transition_semantics` must explicitly define how completion affects acceptance/transition state.

## Failure / Resume / Delivery Semantics
- `failure_policy` supported values:
  - `stop_on_failure`
  - `stop_on_blocked`
  - `continue_on_failure`
- `resume_supported`: mission can resume from `resume_pointer` in checkpoint artifact.
- `stop_conditions`: explicit triggers for stop behavior.
- `delivery_target`: mission-level delivery route for operational outputs.
- `review_requirement`: required review gate before mission acceptance.
- `escalation_requirement`: explicit escalation requirement flag for blocked/critical missions.
