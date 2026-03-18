# OBSERVED_ADVERSARIAL_CHECK_EXPANSION_REPORT

- generated_at_utc: `2026-03-18T14:33:00Z`
- scope: `convert high-value inferred rank-safety cases into observed checks`
- methodology: `lightweight validator invocations, fail-closed interpretation`

## Case Expansion Matrix

| case | prior state | current state | check path / validator | result | remaining weakness |
|---|---|---|---|---|---|
| wrong-root node context | inferred | observed | `detect_node_rank.py --canonical-root-override E:\\WorkFLOW2` | `canonical_root_valid=false`, rank narrowed to `ASTARTES`, fail-closed reason `canonical_root_invalid` | test uses override hook, not physical relocation |
| unavailable validators | inferred | observed | `run_constitution_checks.py --node-rank-script scripts/validation/does_not_exist_rank.py` | rank status became `UNKNOWN`; admission remained blocked fail-closed | still relies on script-level override, not process-level crash injection |
| partial reintegration bundle | inferred/legacy observed | observed (fresh) | `review_integration_inbox.py` with intentionally partial `handoff_package.json` | package decision `QUARANTINE` with missing-required-field reasons | check is schema-based; no deep semantic authority validation |
| missing / invalid warrant | inferred | observed | `check_sovereign_claim_denial.py` with `ASTARTES + execution_report_claim` and missing/invalid warrant | `DENY` with `missing_valid_warrant_or_charter_for_astartes_execution_claim` | coverage currently focused on claim gate, not all execution scripts |
| rank-check unavailable during admission | inferred | observed | same `run_constitution_checks.py` adversarial override | `node_rank_detection_status=UNKNOWN`, `detected_node_rank=UNKNOWN`, fail-closed denial path active | explicit hard-fail policy is present but broader operator workflow still needed |
| portable node with leftover artifacts | inferred | observed | `detect_node_rank.py --json-only --no-write` | `portable_residue_detected=true` while rank remained non-elevated (`ASTARTES`) | residue hygiene policy still partly procedural |
| claim attempt with unknown rank | inferred | observed | `check_sovereign_claim_denial.py --detected-rank UNKNOWN --claim-class canonical_acceptance_claim` | `DENY`, reason `unknown_rank_fail_closed` | none critical; expansion to more claim classes still recommended |
| safe mirror only context without canonical local root | inferred | observed | `check_sovereign_claim_denial.py --context-surface safe_mirror --canonical-root-valid false --claim-class canonical_acceptance_claim` | `DENY`, reason `invalid_canonical_root_fail_closed` | still policy-dependent for all external integrations |

## Lightweight Validator Updates Applied

1. `detect_node_rank.py`: added `--canonical-root-override` for controlled adversarial observation.
2. `run_constitution_checks.py`: added script-path overrides for node-rank and claim-denial validators; enables explicit unavailability testing.
3. `check_sovereign_claim_denial.py`: added `signature_assurance`, `warrant_status`, `charter_status` gates.

## Summary

- converted_to_observed: `8/8` targeted high-value cases
- still_inferred: `0` in this selected set
- caution: observed tests are controlled/adversarial harness runs and do not replace full Emperor-local sovereign acceptance verification.
