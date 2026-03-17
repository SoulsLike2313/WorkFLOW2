# OPERATOR_MISSION_CATALOG_WAVE_3A

## Scope
Wave 3A safe mission foundation. Mission layer is limited to certification/readiness/review/package-safe flows.

## Mission: `certification_mission`
- Purpose: close baseline certification for current governance/query/command/task-program layer.
- Scope: certification chain execution only.
- Non-goals:
  - policy mutation
  - guarded creator mutation flows
  - lifecycle install/remove operations
- Program classes/dependencies:
  - `program.wave2a.creator_grade_validation.v1`
  - `program.wave2a.governance_chain_validation.v1`
  - `program.wave2a.status_evidence_report.v1`
- Mission checkpoints:
  - authority and policy gates PASS
  - each program returns `SUCCESS`
  - completion rule `certify_on_success`
- Required artifacts:
  - `runtime/repo_control_center/repo_control_status.json`
  - `runtime/repo_control_center/repo_control_report.md`
  - `runtime/repo_control_center/operator_mission_status.json`
  - `runtime/repo_control_center/operator_mission_report.md`
  - `runtime/repo_control_center/operator_mission_checkpoint.json`
- Acceptance criteria:
  - creator authority present
  - all dependencies return `SUCCESS`
  - creator-grade `full-check` remains `PASS`
- Blocked conditions:
  - missing creator authority
  - sync not `IN_SYNC`
  - dirty worktree
  - step execution failure

## Mission: `readiness_mission`
- Purpose: assemble readiness package and verify transition readiness for next stage.
- Scope: readiness evidence aggregation.
- Non-goals:
  - mutation-heavy programs
  - integration lifecycle updates
  - governance override behavior
- Program classes/dependencies:
  - `program.wave2a.full_status_reconstruction.v1`
  - `program.wave2a.governance_evidence_pack.v1`
  - `program.wave2a.operator_engineering_report.v1`
- Mission checkpoints:
  - reconstruction complete
  - evidence pack generated
  - operator report generated
- Required artifacts:
  - `runtime/repo_control_center/plain_status.md`
  - `runtime/repo_control_center/one_screen_status.json`
  - `runtime/repo_control_center/operator_mission_status.json`
  - `runtime/repo_control_center/operator_mission_report.md`
  - `runtime/repo_control_center/operator_mission_checkpoint.json`
- Acceptance criteria:
  - all dependencies return `SUCCESS`
  - readiness package available for next-stage assessment
- Blocked conditions:
  - missing creator authority
  - sync not `IN_SYNC`
  - dirty worktree
  - step execution failure

## Mission: `review_prep_mission`
- Purpose: prepare review-ready mission package in safe export scope.
- Scope: review package preparation and report assembly.
- Non-goals:
  - creator-only guarded mutations
  - integration mutation flows
  - external lifecycle operations
- Program classes/dependencies:
  - `program.wave2a.governance_evidence_pack.v1`
  - `program.wave2a.status_evidence_report.v1`
  - `program.wave2a.operator_engineering_report.v1`
- Mission checkpoints:
  - evidence package built
  - status evidence report built
  - mission report produced
- Required artifacts:
  - `runtime/chatgpt_bundle_exports`
  - `runtime/repo_control_center/operator_mission_status.json`
  - `runtime/repo_control_center/operator_mission_report.md`
  - `runtime/repo_control_center/operator_mission_checkpoint.json`
- Acceptance criteria:
  - review-safe evidence artifacts generated
  - mission report generated
- Blocked conditions:
  - policy basis missing
  - step execution failure

## Mission: `status_consolidation_mission`
- Purpose: consolidate runtime status/evidence into mission-level truth surface.
- Scope: status refresh and consolidation only.
- Non-goals:
  - policy mutation
  - state-changing programs
  - guarded creator operations
- Program classes/dependencies:
  - `program.wave2a.status_refresh_surface.v1`
  - `program.wave2a.full_status_reconstruction.v1`
  - `program.wave2a.status_evidence_report.v1`
- Mission checkpoints:
  - status refreshed
  - full reconstruction complete
  - evidence report emitted
- Required artifacts:
  - `runtime/repo_control_center/plain_status.md`
  - `runtime/repo_control_center/one_screen_status.json`
  - `runtime/repo_control_center/operator_mission_status.json`
  - `runtime/repo_control_center/operator_mission_report.md`
  - `runtime/repo_control_center/operator_mission_checkpoint.json`
- Acceptance criteria:
  - status artifacts refreshed
  - status/evidence chain available in mission report
- Blocked conditions:
  - policy basis missing
  - step execution failure
