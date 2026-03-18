# MISSION_EXECUTION_PROOF_STRENGTHENING_PLAN

## Objective
Increase mission execution proof strength without adding a new brain layer or heavy automation framework.

## Recommended Low-Risk / High-Value Changes

### 1) Add explicit post-completion mirror-refresh proof run
- Change: run a dedicated sequence `mission completion -> safe mirror evidence refresh -> repo_control full-check` and store outputs with one shared run context.
- Expected effect: upgrades "mirror-refresh-safe post-completion path" from weak to medium/strong.
- Risk: low (operational sequencing only).
- Do now / later: **do now**.

### 2) Add one successful guarded state-change reference run
- Change: execute one guarded mission on a clean precondition set where policy basis is valid and expected guarded programs can succeed.
- Expected effect: closes current gap where guarded coverage is mostly blocked/failed evidence.
- Risk: medium (requires clean controlled conditions).
- Do now / later: **later**.

### 3) Introduce lightweight mission proof pointer index
- Change: add a tiny pointer artifact (for example `runtime/repo_control_center/mission_proof_index.json`) mapping proof classes to latest valid runtime evidence.
- Expected effect: faster machine and operator discovery of proof surfaces; less evidence hunting.
- Risk: low.
- Do now / later: **do now**.

### 4) Tighten blocked-path evidence completeness
- Change: require blocked outputs to always include explicit denied reason category (`authority`, `policy`, `precondition`, `sync`), not only raw blockers list.
- Expected effect: clearer denied-execution diagnostics and more stable coverage scoring.
- Risk: low.
- Do now / later: **later**.

### 5) Align mission-proof naming with V1 policy expectations
- Change: add mission-proof naming guidance to future outputs (`<context>_<surface>_output.json`) and keep a short legacy alias map.
- Expected effect: reduced ambiguity in proof discovery and bundle curation.
- Risk: low.
- Do now / later: **do now**.

### 6) Add freshness marker for proof claims
- Change: include `proof_basis_head` + `proof_generated_at` in mission-proof summary artifacts.
- Expected effect: prevents stale proof from being interpreted as current strong proof.
- Risk: low.
- Do now / later: **later**.

## Priority Sequence
1. Post-completion mirror-refresh proof run.
2. Lightweight mission-proof pointer index.
3. Naming alignment.
4. Guarded success-path run.
5. Blocked-path category normalization.
6. Freshness marker standardization.

## Current Recommendation
- Short-term posture: keep current proof posture as moderate and avoid overstating mirror/guarded success strength.
