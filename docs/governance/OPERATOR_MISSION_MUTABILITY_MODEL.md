# OPERATOR_MISSION_MUTABILITY_MODEL

## Scope
Wave 3C mission mutability/safety model for mission-layer execution guards.

## Mutability Levels

### `READ_ONLY`
- Required authority: none.
- Required policy gate: mission contract + policy basis present.
- Allowed state change: no state mutation.
- Stop condition: on unexpected blocked/failed program.
- Rollback expectation: none.
- Audit requirement: mission status/report/checkpoint/history.
- Escalation requirement: optional, mission-defined.

### `REFRESH_ONLY`
- Required authority: none.
- Required policy gate: refresh/report policy basis.
- Allowed state change: runtime status/evidence refresh only.
- Stop condition: on unexpected blocked/failed program.
- Rollback expectation: none.
- Audit requirement: mission status/report/checkpoint/history.
- Escalation requirement: optional.

### `PACKAGE_ONLY`
- Required authority: mode-specific per mission.
- Required policy gate: export/evidence policy basis.
- Allowed state change: packaging and evidence routing only.
- Stop condition: mission failure policy (`stop_on_failure`, `stop_on_blocked`, `continue_on_failure`).
- Rollback expectation: optional; no uncontrolled mutation.
- Audit requirement: mission status/report/checkpoint/history + audit trail.
- Escalation requirement: mission-defined.

### `REVIEW_DELIVERY`
- Required authority: mode-specific per mission.
- Required policy gate: handoff/inbox/review policy basis.
- Allowed state change: controlled review-delivery routing only.
- Stop condition: mission failure policy + explicit stop conditions.
- Rollback expectation: optional; review-delivery rollback when supported.
- Audit requirement: mission status/report/checkpoint/history + audit trail.
- Escalation requirement: required when review/delivery gates fail.

### `GUARDED_STATE_CHANGE`
- Required authority: creator authority (unless explicitly test-block mission).
- Required policy gate: governance protection + lifecycle/mutability policy basis.
- Allowed state change: policy-approved guarded transitions only.
- Stop condition: mandatory stop on unexpected failure/block.
- Rollback expectation: required when `rollback_supported=true` and transition fails.
- Audit requirement: mission status/report/checkpoint/history + mission audit trail.
- Escalation requirement: mandatory on blocked/failure transitions.

### `CREATOR_ONLY_TRANSITION`
- Required authority: creator mode + valid creator authority marker.
- Required policy gate: creator-only protection policies and acceptance gates.
- Allowed state change: creator-authorized acceptance/transition actions only.
- Stop condition: mandatory stop on unexpected failure/block.
- Rollback expectation: required for failed transition attempts.
- Audit requirement: mission status/report/checkpoint/history + mission audit trail.
- Escalation requirement: mandatory for blocked creator transition paths.

## Guard Rules
- Mission surface must enforce `creator_authority_required` before program execution.
- Mission surface must reject unsupported mutability levels.
- Mission surface must not silently downgrade guarded/creator-only missions into safe missions.
- Blocked mutation test missions are allowed only as explicit guard-certification paths.
- Any guarded failure with rollback support must be reported as rollback-required in mission runtime artifacts.
