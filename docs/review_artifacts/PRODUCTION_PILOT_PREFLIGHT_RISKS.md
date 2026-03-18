# PRODUCTION_PILOT_PREFLIGHT_RISKS

## Risk Register (Preflight)

### R1: guarded baseline transition contract mismatch
- issue: `mission.wave3c.guarded_baseline_transition.v1` can fail because dependency `program.wave2b.review_certification_sequence.v1` hits `inbox_review` argument contract mismatch.
- classification: `NON_BLOCKER` for pilot start if this mission is excluded from required pilot mission set.
- why: pilot can still validate guarded success via `mission.wave3c.creator_only_certification.v1`.
- mitigation/monitoring:
  - do not use guarded baseline transition as mandatory pilot success path.
  - track mismatch as targeted hardening candidate.

### R2: publication_safe_verdict FAIL from allowlist gap
- issue: `scripts/build_safe_mirror_manifest.py` reports `publication_safe_verdict=FAIL` due allowlist treatment for tracked `runtime/repo_control_center/constitution_status.*`.
- classification: `NON_BLOCKER` for mission execution, `CONDITIONAL_BLOCKER` for publication-safe claim in pilot closure package.
- why: mission runtime verification can pass while publication-safe export verdict remains fail.
- mitigation/monitoring:
  - mark publication-safe claim as conditional until allowlist rule is aligned.
  - keep repo-control mirror/admission verdicts explicit and separate from publication-safe verdict.

### R3: runtime truth freshness slippage
- issue: mission evidence can become stale if full-check and mirror evidence refresh are delayed after mission completion.
- classification: `NON_BLOCKER` with operational discipline.
- why: freshness is controllable by sequencing.
- mitigation/monitoring:
  - run refresh/full-check immediately after closure mission.
  - record timestamps and run_id chain in pilot report.

### R4: closure-path dependency sensitivity
- issue: closure-heavy missions can surface hidden dependency assumptions in review/certification sequences.
- classification: `NON_BLOCKER` unless repeated failures prevent closure coherence.
- why: this is an expected pilot discovery zone.
- mitigation/monitoring:
  - keep one optional closure-heavy mission in pilot set.
  - escalate to blocker only if closure path cannot produce coherent evidence chain.

## Optional Low-Risk Preparation (Pre-Pilot)
1. add explicit pointer from mission report template to `runtime/repo_control_center/mission_proof_index.json`.
2. add one short pilot run checklist block to mission execution report before first real run.
3. capture check command order in mission report to reduce repeated check burden.
