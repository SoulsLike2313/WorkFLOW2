# OPERATOR_MISSION_BASELINE

## Purpose
Freeze mission layer as registry-based work package execution surface over the accepted task/program layer.

## Canonical Artifacts
- mission contract: `docs/governance/OPERATOR_MISSION_CONTRACT.md`
- mission registry: `workspace_config/operator_mission_registry.json`
- mission surface: `scripts/operator_mission_surface.py`
- mission runtime truth:
  - `runtime/repo_control_center/operator_mission_status.json`
  - `runtime/repo_control_center/operator_mission_report.md`
  - `runtime/repo_control_center/operator_mission_checkpoint.json`
  - `runtime/repo_control_center/operator_mission_history.json`
  - `runtime/repo_control_center/operator_mission_audit_trail.json`

## Supported Mission Classes
- `status_refresh_mission`
- `validation_mission`
- `evidence_pack_mission`
- `report_mission`
- `multi_program_operational_mission`
- `packaging_review_transition_mission`
- `evidence_aggregation_mission`
- `readiness_transition_mission`
- `guarded_creator_mission`
- `creator_only_mission`
- `controlled_state_change_mission`
- `blocked_mission_test_mission`

## Baseline Constraints
- mission routing is deterministic and registry-bound
- mission decomposition is program-based
- authority/policy/precondition gates are mandatory
- blocked and denied mission states are first-class outputs
- uncontrolled autonomous mission management is forbidden
