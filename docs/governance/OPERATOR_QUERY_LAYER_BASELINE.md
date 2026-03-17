# OPERATOR_QUERY_LAYER_BASELINE

## Purpose
Define the operator query/response layer baseline on top of the accepted governance engine.

## Baseline Scope
- Governance/policy/repo-control baseline remains canonical and unchanged.
- Query layer is an operator-facing normalization surface.
- Query layer does not override governance engine decisions.

## Canonical Runtime Truth Sources
Primary:
- `runtime/repo_control_center/one_screen_status.json`
- `runtime/repo_control_center/plain_status.md`

Deep evidence:
- `runtime/repo_control_center/repo_control_status.json`
- `runtime/repo_control_center/repo_control_report.md`
- `runtime/repo_control_center/evolution_status.json`
- `runtime/repo_control_center/evolution_report.md`

Creator proof outputs:
- `runtime/repo_control_center/creator_authority_env_output.txt`
- `runtime/repo_control_center/creator_detect_machine_mode_output.json`
- `runtime/repo_control_center/creator_repo_control_bundle_output.json`
- `runtime/repo_control_center/creator_repo_control_full_check_output.json`

## Canonical Truth Fields for Query Responses
- `machine_mode`
- `authority_present`
- `authority_status`
- `trust_verdict`
- `sync_verdict`
- `governance_verdict`
- `governance_acceptance_verdict`
- `admission_verdict`
- `admission_status`
- `workspace_health`
- `blocking_reason_category`
- `blocking_reason_detail`
- `next_canonical_step`

## Query Layer Role
- Resolve operator request class.
- Return response in stable contract shape.
- Attach evidence source references.
- Preserve engineering semantics and gate distinctions.
- Provide non-mutating context for the Operator Command Execution Layer.

## Non-Goals
- No governance rule redefinition.
- No policy hierarchy override.
- No runtime truth mutation.
- No conversational simplification layer.
