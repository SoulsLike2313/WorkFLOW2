# OPERATOR_COMMAND_CATALOG

## Purpose
Formal catalog of operator commands accepted by the execution layer.

## Wave 1A

### status_refresh_command
- Action: `status_refresh`
- Scope: refresh repo-control runtime status artifacts.
- Mutability: `read_only`
- Evidence: `runtime/repo_control_center/*`

### validation_command
- Action: `validation_run`
- Scope: run workspace/sync/trust validation chain.
- Mutability: `read_only`
- Evidence: command outputs + validation artifacts.

### evidence_bundle_command
- Action: `evidence_bundle_context`
- Scope: export context safe bundle for operator evidence.
- Mutability: `read_only`
- Evidence: bundle summary + zip path.

### report_generation_command
- Action: `report_generation`
- Scope: generate execution report from runtime truth.
- Mutability: `read_only`
- Evidence: `runtime/operator_command_layer/operator_execution_report_<run_id>.md`

## Wave 1B

### handoff_command
- Action: `handoff_prepare`
- Scope: prepare external block handoff package.
- Mutability: `guarded_state_change`
- Required inputs: `task_id`, `node_id`

### inbox_review_command
- Action: `inbox_review`
- Scope: review integration inbox packages.
- Mutability: `guarded_state_change` (`--route` only in live mutation mode)

### evidence_routing_command
- Action: `evidence_routing`
- Scope: route allowlisted runtime evidence package.
- Mutability: `guarded_state_change`

### policy_reference_command
- Action: `policy_reference_execute`
- Scope: materialize policy basis artifact for requested topic.
- Mutability: `read_only`

## Wave 1C

### guarded_state_change_command
- Action: `refresh_safe_mirror_evidence`
- Scope: guarded refresh of safe-state evidence artifacts.
- Mutability: `guarded_state_change`
- Authority: creator only

### creator_only_execution_command
- Action: `creator_acceptance_precheck`
- Scope: strict creator precheck before acceptance decisions.
- Mutability: `read_only`
- Authority: creator only

### governance_maintenance_command
- Action: `governance_maintenance_check`
- Scope: integrity scan of required governance artifacts.
- Mutability: `read_only`

### install_remove_controlled_command
- Actions: `install_system`, `remove_system`
- Scope: controlled shared-system install/remove path.
- Mutability: `guarded_state_change` (dry-run default)
- Authority: creator only
- Required inputs: `project_slug`, `system_slug`

## Determinism Rule
- Same command intent must resolve to same `command_class` and `resolved_action`.
- Routing precedence is fixed by `OPERATOR_COMMAND_INTENT_ROUTING.md`.
