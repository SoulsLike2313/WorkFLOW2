# MISSION_PROOF_BUNDLE_POLICY_V1

## Purpose
Define a disciplined mission execution proof bundle format under Constitution V1.

## Mission Proof Bundle Definition
A mission proof bundle is a bounded evidence package that proves one or more classes from `MISSION_EXECUTION_PROOF_PROFILE_V1.md` using runtime-truth artifacts plus supporting governance/report artifacts.

## Required Outputs
- Mission execution output(s):
  - at least one run artifact per claimed proof class
  - must include mission contract fields (`mission_class`, `mission_id`, `execution_result`, `completion_verdict`, `blocking_factors`, `evidence_source`)
- Mission runtime truth artifacts:
  - `runtime/repo_control_center/operator_mission_status.json`
  - `runtime/repo_control_center/operator_mission_report.md`
  - `runtime/repo_control_center/operator_mission_checkpoint.json`
  - `runtime/repo_control_center/operator_mission_history.json`
  - `runtime/repo_control_center/operator_mission_audit_trail.json`
- Authority/context proof:
  - `*detect_machine_mode*output*.json` for creator/denied path claims
- Repo-control proof for completion/certification linkage:
  - `*repo_control_full_check*output*.json`

## Optional Outputs
- Consistency outputs (`*operator_mission_consistency*output*.json`)
- Program-layer outputs referenced by mission runtime artifacts
- Bundle/export outputs (`*repo_control_bundle*output*.json`)
- Scenario/golden references for interpretive support (not as sole proof)

## Naming Expectations
- Preferred output naming tokens:
  - `<wave_or_context>_<surface>_output.json`
  - examples: `wave3c_mission_execute_sample_output.json`, `wave3c_repo_control_full_check_output.json`
- Prefix should identify scope (`wave3a`, `wave3b`, `wave3c`, `missionproof`, `creator`).
- Surface token should identify command/function (`detect_machine_mode`, `mission_execute`, `repo_control_full_check`, `mission_consistency`).
- Legacy names are tolerated if traceable and unambiguous.

## Runtime Truth Expectations
- Claimed proof classes must map to runtime-truth surfaces with explicit `run_id`.
- `operator_mission_status.json` and `operator_mission_history.json` must not conflict with claimed outcome.
- `operator_mission_audit_trail.json` must contain mission-class level gate/check context for guarded/blocked proofs.

## Certification and Mirror Refresh Relation
- Certification claims require completion-to-certification evidence, not only scenario text.
- Mirror-refresh-safe claims require safe mirror evidence validity:
  - `workspace_config/SAFE_MIRROR_MANIFEST.json`
  - `docs/review_artifacts/SAFE_MIRROR_BUILD_REPORT.md`
  - repo-control mirror verdict PASS in relevant snapshot
- If mirror evidence is stale or contract-invalid, mirror-safe proof class cannot be claimed as strong.

## Not Acceptable as Proof
- Scenario-only or golden-only claims without runtime execution artifacts.
- Mission outputs without identifiable `run_id` and mission identity fields.
- Claims that omit blocked factors for denied/blocked classes.
- Certification claims without runtime `completion_verdict=CERTIFIED` evidence.
- Mirror-safe claims without mirror-check evidence and safe-state artifact linkage.
- Contradictory outputs across mission status/history/audit trail.

## Usage Rule
- Proof bundles must be evaluated per proof class.
- Bundle completeness is class-based, not file-count based.
