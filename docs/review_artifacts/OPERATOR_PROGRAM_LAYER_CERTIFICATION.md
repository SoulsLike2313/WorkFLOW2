# OPERATOR_PROGRAM_LAYER_CERTIFICATION

## Certification Scope
Operator Task/Program Layer v1 over command execution layer v1.

## Wave Coverage
- Wave 2A: safe read/validate/report programs
- Wave 2B: handoff/review/task-routing programs
- Wave 2C: creator-guarded/mutation-aware programs

## Contract Coverage
Mandatory fields enforced in runtime output:
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

## Certification Gates
- routing consistency on golden pack
- creator-grade detect/bundle/full-check chain remains valid
- runtime artifacts generated and machine-readable
- no governance boundary weakening
