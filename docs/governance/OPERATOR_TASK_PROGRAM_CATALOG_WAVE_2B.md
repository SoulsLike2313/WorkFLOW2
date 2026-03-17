# OPERATOR_TASK_PROGRAM_CATALOG_WAVE_2B

## Scope
Wave 2B controlled operational programs over existing Wave 2A safe foundation.

## Program Classes

### handoff_preparation_program
- Purpose: assemble delivery-ready handoff package with validation and evidence chain.
- Checkpoints:
  - validation completed
  - package prepared
  - handoff metadata produced
  - final report generated
- Command classes used:
  - `validation_command`
  - `evidence_bundle_command`
  - `handoff_command`
  - `report_generation_command`
- Delivery/review behavior:
  - target: `integration/inbox`
  - review requirement: `integration_review_required`
- Failure/resume behavior:
  - `failure_policy=stop_on_failure`
  - stop on `any_step_failed` or `any_step_blocked`
  - resume supported
- Blocking conditions:
  - missing required inputs (`task_id`, `node_id`)
  - step execution failure

### inbox_review_program
- Purpose: execute full inbox/review queue audit and produce review trace.
- Checkpoints:
  - inbox scan completed
  - policy reference generated
  - review report generated
- Command classes used:
  - `inbox_review_command`
  - `policy_reference_command`
  - `report_generation_command`
- Delivery/review behavior:
  - target: `integration/review_queue`
  - review requirement: `canonical_review_flow`
- Failure/resume behavior:
  - `failure_policy=stop_on_blocked`
  - stop on blocked/failure conditions
  - resume supported
- Blocking conditions:
  - mode not allowed
  - review dependency missing

### evidence_delivery_program
- Purpose: build and route policy-backed runtime evidence for review.
- Checkpoints:
  - status refresh completed
  - validation completed
  - evidence routing completed
  - report generated
- Command classes used:
  - `status_refresh_command`
  - `validation_command`
  - `evidence_routing_command`
  - `report_generation_command`
- Delivery/review behavior:
  - target: `integration/inbox`
  - review requirement: `integration_review_required`
- Failure/resume behavior:
  - `failure_policy=stop_on_failure`
  - stop on failed/blocked step
  - resume supported
- Blocking conditions:
  - delivery target unavailable
  - step execution failure

### certification_program
- Purpose: run readiness/certification operational sequence over governance chain.
- Checkpoints:
  - authority precheck (creator path)
  - validation and/or inbox review
  - policy reference evidence
  - certification report
- Command classes used:
  - `creator_only_execution_command`
  - `validation_command`
  - `inbox_review_command`
  - `policy_reference_command`
  - `report_generation_command`
- Delivery/review behavior:
  - targets: `runtime/repo_control_center`, `integration/review_queue`
  - review requirements: `creator_review` or `canonical_review_flow`
- Failure/resume behavior:
  - creator pass: `stop_on_failure`
  - review sequence: `continue_on_failure` + stop on blocked condition
  - resume supported
- Blocking conditions:
  - missing creator authority for creator-bound program
  - missing policy basis
  - sync precondition failure for creator certification pass

## Expected Final Outputs
- `runtime/repo_control_center/operator_program_status.json`
- `runtime/repo_control_center/operator_program_report.md`
- `runtime/repo_control_center/operator_program_checkpoint.json`
- `runtime/repo_control_center/operator_program_history.json`
- step-level outputs under `runtime/repo_control_center/operator_program_outputs/<run_id>/`
