# OPERATOR_PROGRAM_CATALOG

## Purpose
Formal catalog of policy-bound operator task/program flows.

## Wave 2A Programs

### safe_status_validation_report_program
- program_id: `program.safe_status_validation_report.v1`
- class: `safe_read_validate_report_program`
- goal: refresh status, run validation chain, materialize report.
- mutability: `read_only`
- resume_supported: `true`

### safe_evidence_bundle_program
- program_id: `program.safe_evidence_bundle.v1`
- class: `safe_read_validate_report_program`
- goal: generate context evidence bundle with explicit safety verdict.
- mutability: `read_only`

### safe_policy_reference_program
- program_id: `program.safe_policy_reference.v1`
- class: `safe_read_validate_report_program`
- goal: generate policy-reference evidence artifact.
- mutability: `read_only`

## Wave 2B Programs

### task_handoff_review_packaging_program
- program_id: `program.task_handoff_review_packaging.v1`
- class: `operational_handoff_review_program`
- goal: resolve task, prepare handoff package, review inbox, route evidence.
- mutability: `guarded_state_change`
- required inputs: `task_id`, `node_id`
- failure_policy: `stop_on_failure`
- resume_supported: `true`

### integration_inbox_triage_program
- program_id: `program.integration_inbox_triage.v1`
- class: `operational_handoff_review_program`
- goal: review inbox and produce execution report.
- mutability: `read_only`

### deterministic_task_route_program
- program_id: `program.deterministic_task_route.v1`
- class: `operational_task_routing_program`
- goal: resolve task contract and generate policy reference snapshot.
- required inputs: `task_id`
- mutability: `read_only`

## Wave 2C Programs

### creator_guarded_refresh_precheck_program
- program_id: `program.creator_guarded_refresh_precheck.v1`
- class: `creator_guarded_program`
- goal: guarded safe-state refresh + creator precheck + governance maintenance.
- mutability: `guarded_state_change`
- creator authority required: `true`
- operator confirmation required for live mutation.

### creator_controlled_install_remove_cycle_program
- program_id: `program.creator_install_remove_cycle.v1`
- class: `creator_guarded_program`
- goal: controlled install/remove execution cycle under guard.
- required inputs: `project_slug`, `system_slug`
- mutability: `guarded_state_change`
- rollback_supported: `true`

## Determinism Rule
- Same request intent resolves to same `program_class` and `program_id`.
- Step plan is explicit and checkpointed.
- Program execution result must follow execution contract semantics.
