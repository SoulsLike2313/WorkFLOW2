# OPERATOR_TASK_PROGRAM_MUTABILITY_MODEL

## Scope
Mutability and safety model for Wave 2C guarded creator programs in task/program layer.

## Mutability Levels

### READ_ONLY
- Required authority: none
- Required policy gate: command/program policy basis present
- Allowed state change: no guarded mutation; runtime evidence updates only
- Stop condition: `any_step_failed`, `any_step_blocked`
- Rollback expectation: not required
- Audit requirement: execution payload + history entry
- Escalation requirement: optional

### REFRESH_ONLY
- Required authority: none
- Required policy gate: refresh program policy basis present
- Allowed state change: refresh of runtime status/evidence only
- Stop condition: `any_step_failed`
- Rollback expectation: not required
- Audit requirement: status/checkpoint/history trail
- Escalation requirement: optional

### PACKAGE_ONLY
- Required authority: none unless `creator_authority_required=true`
- Required policy gate: packaging and delivery policy basis present
- Allowed state change: packaging/routing artifacts, no unrestricted mutation
- Stop condition: `any_step_failed`, `any_step_blocked`
- Rollback expectation: optional if delivery side effects exist
- Audit requirement: delivery artifacts + execution trail
- Escalation requirement: as declared by program

### OPERATIONAL_ROUTING
- Required authority: mode-specific by registry
- Required policy gate: integration/inbox/evidence routing policy basis
- Allowed state change: controlled routing transitions only
- Stop condition: `any_step_blocked`
- Rollback expectation: required when routing changes are partial
- Audit requirement: routing outputs + audit trail entry
- Escalation requirement: required when review dependency fails

### GUARDED_STATE_CHANGE
- Required authority: creator authority required
- Required policy gate: guarded mutation policy basis + explicit approval basis
- Allowed state change: bounded controlled mutation only via registry steps
- Stop condition: `any_step_failed`, `any_step_blocked`, policy-defined hard stops
- Rollback expectation: required if sequence fails after mutation step
- Audit requirement: full audit trail with step results and rollback flag
- Escalation requirement: mandatory

### CREATOR_ONLY_MUTATION
- Required authority: creator authority + creator-only mode gate
- Required policy gate: creator policy basis + canonical machine protection policy
- Allowed state change: creator-approved mutation sequences only
- Stop condition: immediate stop on authority/policy/precondition failure
- Rollback expectation: required on failure or blocked mutation step
- Audit requirement: full audit trail + creator authority context
- Escalation requirement: mandatory creator review

## Guard Rules
- Unknown mutability level => `BLOCKED` (invalid program contract).
- `GUARDED_STATE_CHANGE` and `CREATOR_ONLY_MUTATION` cannot run without `creator_authority_required=true`.
- Risky request that falls back to safe status program is forbidden (`risky_request_not_mapped_to_guarded_program`).
- Guarded mutation path cannot auto-downgrade into safe fallback.

## Audit Outputs (Wave 2C)
- `runtime/repo_control_center/operator_program_status.json`
- `runtime/repo_control_center/operator_program_report.md`
- `runtime/repo_control_center/operator_program_checkpoint.json`
- `runtime/repo_control_center/operator_program_history.json`
- `runtime/repo_control_center/operator_program_audit_trail.json`
