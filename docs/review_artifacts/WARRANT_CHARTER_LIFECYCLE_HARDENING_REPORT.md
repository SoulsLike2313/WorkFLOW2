# WARRANT_CHARTER_LIFECYCLE_HARDENING_REPORT

- generated_at_utc: `2026-03-18T14:30:00Z`
- scope: `warrant/charter lifecycle hardening for rank-aware execution`
- primary_policy: `docs/governance/WARRANT_CHARTER_LIFECYCLE_V1.md`

## 1) What Is Now Enforceable

Machine-enforceable now:
1. Astartes `execution_report_claim` is denied unless at least one of `warrant_status` or `charter_status` is `valid`.
2. missing/invalid warrant paths fail closed in claim-denial validator.
3. lifecycle status classes are explicitly normalized in policy/schema (`valid|invalid|expired|superseded|unknown`).

Evidence (observed):
1. `check_sovereign_claim_denial.py` with `ASTARTES + execution_report_claim + warrant_status=missing + charter_status=missing` -> `DENY`.
2. same with `warrant_status=valid` -> `ALLOW`.

## 2) What Is Doctrine-Only (Current Stage)

1. full warrant/charter issuance registry and supersession chain are policy-defined, not globally machine-enforced.
2. global cross-script lifecycle checks for every execution surface are not yet unified.
3. Emperor-local sovereign acceptance still required for final authority interpretation.

## 3) Where Lifecycle Is Still Soft

1. non-validation scripts can still process artifacts without strict warrant lifecycle parsing.
2. warrant/charter linkage is not yet mandatory in every historical handoff document.
3. replay-safe lifecycle transitions are not cryptographically anchored.

## 4) Uncovered or Partially Covered Execution Paths

1. generic task scripts outside claim-denial path do not yet enforce warrant lifecycle directly.
2. intake/reintegration scripts rely on checklist discipline; no single universal lifecycle verifier yet.
3. manual review remains required for ambiguous legacy documents.

## 5) Lightweight Validation Hooks Added

Added in this hardening cycle:
1. `scripts/validation/check_sovereign_claim_denial.py` now accepts `warrant_status` and `charter_status`.
2. Astartes execution claim path now has explicit fail-closed authority check.

## 6) Verdict

`MODERATE`

Rationale:
- high-value execution path now has machine-enforced warrant/charter gate,
- but end-to-end lifecycle enforcement across all execution paths is not yet complete.
