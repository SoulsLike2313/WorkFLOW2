# OPERATOR_TASK_PROGRAM_BASELINE

## Purpose
Freeze Task/Program Layer as the canonical operator-facing program execution baseline after Wave 2A + Wave 2B + Wave 2C.

## Baseline Components
- canonical registry: `workspace_config/operator_task_program_registry.json`
- canonical contract: `docs/governance/OPERATOR_TASK_PROGRAM_CONTRACT.md`
- canonical mutability model: `docs/governance/OPERATOR_TASK_PROGRAM_MUTABILITY_MODEL.md`
- canonical runtime truth:
  - `runtime/repo_control_center/operator_program_status.json`
  - `runtime/repo_control_center/operator_program_report.md`
  - `runtime/repo_control_center/operator_program_checkpoint.json`
  - `runtime/repo_control_center/operator_program_history.json`
  - `runtime/repo_control_center/operator_program_audit_trail.json`

## Supported Program Classes
- `status_refresh_program`
- `validation_program`
- `evidence_pack_program`
- `report_program`
- `handoff_preparation_program`
- `inbox_review_program`
- `evidence_delivery_program`
- `certification_program`
- `guarded_maintenance_program`
- `creator_only_program`
- `controlled_lifecycle_program`
- `blocked_mutation_test_program`

## Baseline Guarantees
- deterministic request -> class -> program routing via registry precedence
- explicit authority/policy/precondition gates before execution
- checkpoint/resume model is persisted and auditable
- guarded mutation paths cannot run without creator authority
- blocked/denied cases are first-class outcomes and preserved in evidence trail

## Intentionally Unsupported
- unrestricted autonomous mutation
- silent auto-approval of guarded programs
- policy override from helper/integration mode
- product-domain orchestration outside governance/control scope
