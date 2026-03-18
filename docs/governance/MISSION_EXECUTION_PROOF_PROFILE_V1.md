# MISSION_EXECUTION_PROOF_PROFILE_V1

## Purpose
Define the minimum representative proof set for Mission Layer execution under finalized Constitution V1.

## Proof Class 1: successful creator-grade mission path
- Purpose: prove mission execution works end-to-end in creator context.
- Why it matters: confirms mission layer can complete and certify a valid execution path.
- Required evidence:
  - creator-mode proof (`machine_mode=creator`, `authority_present=true`)
  - mission execution output with `execution_result=SUCCESS`
  - mission output with `completion_verdict=CERTIFIED`
  - mission runtime artifacts updated for the run
- Minimum artifacts:
  - `runtime/repo_control_center/*detect_machine_mode*output*.json`
  - `runtime/repo_control_center/*mission_execute*output*.json`
  - `runtime/repo_control_center/operator_mission_status.json`
  - `runtime/repo_control_center/operator_mission_report.md`
  - `runtime/repo_control_center/operator_mission_checkpoint.json`
  - `runtime/repo_control_center/operator_mission_history.json`
  - `runtime/repo_control_center/operator_mission_audit_trail.json`
- Acceptance signal: creator-grade mission run ends with `SUCCESS + CERTIFIED` and zero blocking factors.

## Proof Class 2: guarded state-change mission path
- Purpose: prove guarded mutability routes execute with strict authority/policy controls.
- Why it matters: validates that state-change capable paths are constrained, auditable, and rollback-aware.
- Required evidence:
  - guarded mission output (`mutability_level=GUARDED_STATE_CHANGE` or `CREATOR_ONLY_TRANSITION`)
  - explicit authority/policy/precondition checks
  - explicit stop/rollback/escalation semantics
  - mission audit-trail entry for the run
- Minimum artifacts:
  - `runtime/repo_control_center/*guarded*output*.json`
  - `runtime/repo_control_center/*creator_only*output*.json`
  - `runtime/repo_control_center/operator_mission_audit_trail.json`
  - `workspace_config/operator_mission_registry.json`
- Acceptance signal: guarded route is executed with explicit gate evaluation and audit-trail capture.

## Proof Class 3: blocked-by-policy mission path
- Purpose: prove policy basis can actively deny mission execution.
- Why it matters: prevents fake progress and prevents policy bypass by runtime execution.
- Required evidence:
  - mission output with `policy_check=BLOCKED`
  - blocking reason explicitly tied to policy basis/missing policy requirement
  - completion stays `BLOCKED`
- Minimum artifacts:
  - `runtime/repo_control_center/*policy_blocked*output*.json`
  - `runtime/repo_control_center/operator_mission_report.md`
  - `runtime/repo_control_center/operator_mission_audit_trail.json`
- Acceptance signal: mission denial is policy-driven, explicit, and traceable.

## Proof Class 4: blocked mutation / denied execution path
- Purpose: prove unauthorized or invalid mutation paths are denied.
- Why it matters: protects authority boundaries and constitutional safety discipline.
- Required evidence:
  - blocked mission output caused by authority/precondition constraints
  - clear denied reason (`machine_mode not allowed`, missing required context, etc.)
  - completion remains `BLOCKED` or certified blocked case where policy requires explicit blocked proof
- Minimum artifacts:
  - `runtime/repo_control_center/*blocked*output*.json`
  - `runtime/repo_control_center/operator_mission_status.json`
  - `runtime/repo_control_center/operator_mission_audit_trail.json`
- Acceptance signal: denied path is explicit, reproducible, and non-silent.

## Proof Class 5: completion-to-certification path
- Purpose: prove mission completion can transition to certified outcome with evidence chain.
- Why it matters: validates completion law and certification discipline.
- Required evidence:
  - mission run with successful execution result
  - mission status/report with `completion_verdict=CERTIFIED`
  - certification artifact that references mission-layer evidence
- Minimum artifacts:
  - `runtime/repo_control_center/*mission_execute*output*.json`
  - `runtime/repo_control_center/operator_mission_status.json`
  - `runtime/repo_control_center/operator_mission_report.md`
  - `docs/review_artifacts/OPERATOR_MISSION_CERTIFICATION_REPORT.md`
- Acceptance signal: certified mission state is visible in runtime truth and review artifacts.

## Proof Class 6: mirror-refresh-safe post-completion path
- Purpose: prove post-completion mission evidence can be mirrored safely without evidence-contract break.
- Why it matters: links mission completion claims to safe external snapshot discipline.
- Required evidence:
  - post-completion repo-control check with mirror verdict PASS
  - safe mirror evidence files valid under evidence contract
  - no unresolved mismatch between mission completion claim and mirror evidence freshness
- Minimum artifacts:
  - `runtime/repo_control_center/*repo_control_full_check*output*.json`
  - `workspace_config/SAFE_MIRROR_MANIFEST.json`
  - `docs/review_artifacts/SAFE_MIRROR_BUILD_REPORT.md`
  - `runtime/repo_control_center/repo_control_status.json`
- Acceptance signal: mission completion evidence and mirror evidence are both valid and non-stale.

## Profile Use Rule
- Claims of "mission-proof complete" must be backed by all six proof classes.
- Synthetic scenarios may support interpretation, but cannot replace runtime execution evidence for strong coverage.
