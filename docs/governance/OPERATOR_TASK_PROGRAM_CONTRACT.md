# OPERATOR_TASK_PROGRAM_CONTRACT

## Scope
Wave 2A contract for safe operator task/program execution over the accepted governance/query/command baseline.

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

## Optional Fields
- `resume_supported`
- `failure_policy`
- `notes`

## Contract Semantics
- `program_class`: one of Wave 2A safe classes (`status_refresh_program`, `validation_program`, `evidence_pack_program`, `report_program`).
- `task_id_or_program_id`: deterministic program identifier resolved from request.
- `execution_scope`: bounded scope from registry; no out-of-registry planning is allowed.
- `authority_check`: mode/authority gate result from machine-mode detection contract.
- `policy_check`: policy-basis file presence and policy gate status.
- `preconditions`: explicit precondition checks and failed items.
- `step_plan`: ordered step model, each step mapped to command-layer execution units.
- `current_step`: active or last executed step id.
- `checkpoint_state`: completed steps, failed step, resume pointer, resume capability.
- `execution_result`: `SUCCESS | FAILED | BLOCKED`.
- `artifacts_produced`: program artifacts + step output artifacts.
- `state_change`: git-status based state-delta snapshot.
- `blocking_factors`: exact blockers; no generic placeholders.
- `next_step`: deterministic remediation or continuation path.
- `evidence_source`: canonical files and runtime outputs used for verdict.

## Wave 2A Safety Boundaries
- Allowed mutability levels only: `READ_ONLY`, `REFRESH_ONLY`, `PACKAGE_ONLY`.
- No guarded mutation flows in Wave 2A.
- No autonomous planning outside registry.
- Command execution must be delegated to `scripts/operator_command_surface.py`.

## Failure and Resume Rules
- Default failure policy: `stop_on_failure`.
- Resume is allowed only when `resume_supported=true` and checkpoint pointer is valid.
- Blocked precondition/authority/policy checks must return `BLOCKED` before step execution.
