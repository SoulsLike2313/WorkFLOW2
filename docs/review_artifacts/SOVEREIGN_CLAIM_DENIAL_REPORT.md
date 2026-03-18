# SOVEREIGN_CLAIM_DENIAL_REPORT

- generated_at_utc: `2026-03-18T14:04:00Z`
- validator: `scripts/validation/check_sovereign_claim_denial.py`
- policy_anchor: `docs/governance/SOVEREIGN_CLAIM_DENIAL_POLICY_V1.md`

## 1) Claim Types Already Machine-Denied

Observed deny behavior:

1. `PRIMARCH` + `canonical_acceptance_claim` -> `DENY` (`primarch_cannot_issue_sovereign_claim`)
2. `UNKNOWN` rank + any evaluated claim -> `DENY` (`unknown_rank_fail_closed`)
3. invalid canonical root + sovereign claim -> `DENY` (`invalid_canonical_root_fail_closed`)
4. `ASTARTES` sovereign/elevated claims -> deny path active by rank matrix.

## 2) Claim Types Allowed Under Rank Bounds

Observed allow behavior:

1. `ASTARTES` + `execution_report_claim` -> `ALLOW`
2. `PRIMARCH` + `bounded_engineering_proposal` -> `ALLOW`
3. `PRIMARCH` + `denial_as_expected_claim` -> `ALLOW`

## 3) Policy-Level Only Areas

1. signature status is currently metadata-driven without full cryptographic verification;
2. inter-node issuer identity trust is not yet cryptographically anchored;
3. full warrant/charter execution enforcement across all execution surfaces is not complete.

## 4) Operational Readiness For Real Inter-Node Mode

- current_gate_readiness: `MODERATE`

Reason:
1. claim-class/rank/root denial logic is executable and fail-closed;
2. some identity/signature guarantees remain hardening-stage only.

## 5) Sovereign Claims That Must Stay Emperor-Local

1. canonical acceptance final claim;
2. sovereign policy change claim;
3. Emperor-rank assertion in acceptance context;
4. unrestricted structural mutation authorization.

## 6) Verdict

`MODERATE`
