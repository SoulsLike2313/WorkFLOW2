# OPERATOR_TASK_PROGRAM_CONTRACT

## Scope
Unified contract for Wave 2A, Wave 2B, and Wave 2C task/program execution over governance/query/command baseline.

## Required Execution Shape
- `program_class`
- `task_id_or_program_id`
- `resolved_goal`
- `execution_scope`
- `authority_check`
- `policy_check`
- `preconditions`
- `step_plan`
- `current_step`
- `checkpoint_state`
- `execution_result`
- `artifacts_produced`
- `state_change`
- `blocking_factors`
- `next_step`
- `evidence_source`

## Wave 2B Required Extensions
- `failure_policy`
- `resume_supported`
- `stop_conditions`
- `delivery_target`
- `review_requirement`
- `escalation_requirement`

## Wave 2C Guarded Extensions
- `mutability_level`
- `creator_authority_required`
- `rollback_supported`
- `rollback_required`
- `approval_basis`
- `audit_trail_reference`

## Optional Fields
- `notes`
- `command_dependencies`
- `review_dependencies`
- `delivery_artifacts`
- `audit_outputs`

## Contract Semantics
- `program_class`: one registered class in `workspace_config/operator_task_program_registry.json`.
- `task_id_or_program_id`: deterministic program identifier resolved via registry or explicit override.
- `execution_scope`: bounded scope declared by registry; no out-of-registry planning is allowed.
- `authority_check`: mode and creator-authority gate result from machine-mode detection contract.
- `policy_check`: policy-basis file presence and policy gate status.
- `preconditions`: explicit precondition checks and failed items.
- `step_plan`: ordered step model where each step maps to command-layer execution units.
- `current_step`: active or last executed step id.
- `checkpoint_state`: completed steps, pending steps, failed step, resume pointer, stop condition state.
- `execution_result`: `SUCCESS | FAILED | BLOCKED`.
- `artifacts_produced`: declared evidence outputs plus step-produced artifacts.
- `state_change`: git-status based state-delta snapshot plus mutability/execution mode.
- `blocking_factors`: exact blockers; no generic placeholders.
- `next_step`: deterministic remediation, resume path, or follow-up review path.
- `evidence_source`: canonical files and runtime outputs used for verdict.
- `failure_policy`: minimum supported values are `stop_on_failure`, `stop_on_blocked`, `continue_on_failure`.
- `stop_conditions`: hard stop triggers for multi-step operational programs.
- `delivery_target`: declared handoff/review destination path class.
- `review_requirement`: required review model before acceptance.
- `escalation_requirement`: explicit escalation flag for creator/integration review chain.
- `mutability_level`: bounded mutability classification defined in `docs/governance/OPERATOR_TASK_PROGRAM_MUTABILITY_MODEL.md`.
- `creator_authority_required`: explicit creator gate requirement (`true/false`), independent from request text.
- `rollback_supported`: whether rollback path exists for this program class.
- `rollback_required`: runtime-derived rollback requirement for failed/blocked guarded mutations.
- `approval_basis`: explicit policy artifacts required for guarded/creator programs.
- `audit_trail_reference`: runtime trail path for audit-grade execution evidence.

## Wave Boundaries
- Wave 2A classes: `status_refresh_program`, `validation_program`, `evidence_pack_program`, `report_program`.
- Wave 2B classes: `handoff_preparation_program`, `inbox_review_program`, `evidence_delivery_program`, `certification_program`.
- Wave 2C classes: `guarded_maintenance_program`, `creator_only_program`, `controlled_lifecycle_program`, `blocked_mutation_test_program`.
- Allowed mutability levels are bounded to:
  - `READ_ONLY`
  - `REFRESH_ONLY`
  - `PACKAGE_ONLY`
  - `OPERATIONAL_ROUTING`
  - `GUARDED_STATE_CHANGE`
  - `CREATOR_ONLY_MUTATION`
- No unrestricted autonomous mutation programs are allowed.
- Command execution must be delegated to `scripts/operator_command_surface.py`.

## Failure/Resume/Delivery Rules
- Blocked authority/policy/precondition checks must return `BLOCKED` before step execution.
- Resume is allowed only when `resume_supported=true` and `resume_pointer` is within step range.
- `failure_policy` and `stop_conditions` together define deterministic stop behavior for multi-step programs.
- Delivery/review semantics must be explicit: `delivery_target` and `review_requirement` are mandatory for Wave 2B operational classes.
- Guarded mutation semantics must be explicit: `mutability_level`, `creator_authority_required`, `rollback_supported`, and `approval_basis` are mandatory for Wave 2C guarded classes.
