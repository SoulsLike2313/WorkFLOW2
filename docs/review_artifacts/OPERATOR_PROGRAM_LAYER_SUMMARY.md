# OPERATOR_PROGRAM_LAYER_SUMMARY

## Layer
Task/Program Layer v1 implemented over governance/query/operator-command baseline.

## Entrypoint
`python scripts/operator_program_surface.py <execute|classify|status|registry|consistency-check>`

## Registry
`workspace_config/operator_program_registry.json`

## Program Classes
- `safe_read_validate_report_program`
- `operational_handoff_review_program`
- `operational_task_routing_program`
- `creator_guarded_program`

## Runtime Evidence
- `runtime/operator_program_layer/last_execution.json`
- `runtime/operator_program_layer/program_surface_status.json`
- `runtime/operator_program_layer/program_surface_report.md`

## Guard Model
- authority and policy checks are mandatory preconditions
- step-level execution is checkpointed
- failure policy defaults to `stop_on_failure`
- resume path is explicit via `--resume-from-step`
- rollback path is explicit via `--attempt-rollback` when supported
