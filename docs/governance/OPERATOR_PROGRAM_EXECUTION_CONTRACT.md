# OPERATOR_PROGRAM_EXECUTION_CONTRACT

## Purpose
Define mandatory execution contract for operator task/program runs.

## Mandatory Fields
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
- `rollback_supported`
- `escalation_requirement`
- `mutability_level`
- `failure_policy`
- `stop_conditions`
- `operator_confirmation_required`
- `notes`

## Required Semantics
- `authority_check`: mode + creator authority gate result.
- `policy_check`: policy basis existence and program-policy gate result.
- `preconditions`: explicit machine-checkable preconditions and failures.
- `step_plan`: ordered executable steps with type and contract references.
- `checkpoint_state`: completed/current/failed step index and resume pointer.
- `execution_result`: `SUCCESS | BLOCKED | FAILED` with summary and exit code.
- `state_change`: mutation class and git-status delta.
- `blocking_factors`: exact blockers preventing completion.
- `next_step`: deterministic remediation path.
- `evidence_source`: canonical files and generated outputs used for the verdict.

## Program Failure Rules
- `stop_on_failure`: stop immediately at first failed step.
- `continue_on_failure`: continue only if explicitly allowed by registry.
- `blocked_path`: return `BLOCKED` without execution if authority/policy/preconditions fail.

## Resume / Rollback Rules
- Resume is allowed only when `resume_supported=true` and checkpoint is valid.
- Rollback is allowed only when `rollback_supported=true` and rollback plan exists.
- Rollback execution is itself evidence-bearing and must not hide original failure.

## Mutability Discipline
- `read_only`: no intentional mutation.
- `guarded_state_change`: mutable steps allowed only with explicit guard.
- For guarded creator programs, live mutation requires:
  - creator authority present,
  - explicit `--allow-mutation`,
  - operator confirmation flag when required.
