# OPERATOR_MISSION_BASELINE

## Purpose
Freeze Mission Layer as the canonical work-package surface above accepted governance/query/command/task-program layers.

## Machine Brain Composition
- governance engine
- operator query layer
- operator command execution layer
- operator task/program layer
- operator mission layer

## Canonical Mission Artifacts
- mission contract: `docs/governance/OPERATOR_MISSION_CONTRACT.md`
- mission mutability model: `docs/governance/OPERATOR_MISSION_MUTABILITY_MODEL.md`
- mission registry: `workspace_config/operator_mission_registry.json`
- mission surface: `scripts/operator_mission_surface.py`
- mission runtime truth:
  - `runtime/repo_control_center/operator_mission_status.json`
  - `runtime/repo_control_center/operator_mission_report.md`
  - `runtime/repo_control_center/operator_mission_checkpoint.json`
  - `runtime/repo_control_center/operator_mission_history.json`
  - `runtime/repo_control_center/operator_mission_audit_trail.json`

## Supported Mission Classes
- `certification_mission`
- `readiness_mission`
- `review_prep_mission`
- `status_consolidation_mission`
- `external_review_mission`
- `readiness_transition_mission`
- `handoff_delivery_mission`
- `evidence_consolidation_mission`
- `guarded_baseline_transition_mission`
- `creator_only_certification_mission`
- `controlled_upgrade_mission`
- `blocked_mutation_mission`

## Baseline Constraints
- mission routing is deterministic and registry-bound only
- mission decomposition is program-driven only
- authority/policy/precondition gates are mandatory
- safe/operational/guarded mission classes remain separated
- blocked and denied mission states are first-class outputs
- uncontrolled autonomous mission management is forbidden
