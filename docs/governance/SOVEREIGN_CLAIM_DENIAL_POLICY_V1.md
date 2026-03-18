# SOVEREIGN_CLAIM_DENIAL_POLICY_V1

Status:
- policy_version: `v1`
- scope: `deny unauthorized sovereign claims in runtime and reintegration`

## 1) Claim Classes

1. `canonical_acceptance_claim`
2. `sovereign_policy_change_claim`
3. `emperor_rank_claim`
4. `unrestricted_structural_mutation_claim`
5. `bounded_engineering_proposal`
6. `execution_report_claim`
7. `denial_as_expected_claim`

Sovereign classes:
1. `canonical_acceptance_claim`
2. `sovereign_policy_change_claim`
3. `emperor_rank_claim`
4. `unrestricted_structural_mutation_claim`

## 2) Rank-Based Allow/Deny

### EMPEROR
- may issue all classes subject to constitutional gates.

### PRIMARCH
- allowed: `bounded_engineering_proposal`, `execution_report_claim`, `denial_as_expected_claim`.
- denied: all sovereign claim classes.

### ASTARTES
- allowed: `execution_report_claim`, `denial_as_expected_claim`.
- denied: all sovereign claim classes and unbounded engineering claims.

## 3) Additional Hardening Gates

### Signature/Identity gates

1. sovereign classes require:
   - `signature_status=valid`
   - `issuer_identity_status=verified`
   - `signature_assurance` in `{locally_verifiable, emperor_local_only_verifiable}`.
2. bounded engineering proposal requires `signature_assurance` at least `structurally_bound`.
3. unknown or insufficient signature assurance narrows authority (deny elevation).

### Warrant/Charter gates

1. Astartes `execution_report_claim` requires at least one of:
   - `warrant_status=valid`
   - `charter_status=valid`.
2. missing/invalid/expired/superseded/unknown warrant+charter states deny authority-bearing execution claim.

## 4) Runtime/Reintegration Denial Points

1. node-rank validation stage;
2. constitutional aggregation stage;
3. reintegration intake/review stage.

## 5) Root and Context Fail-Closed Rules

1. unknown rank -> deny elevated claims fail-closed;
2. invalid canonical root -> deny elevated claims fail-closed;
3. safe mirror/portable-only context never elevates claim authority.

## 6) Expected Denial Semantics

Denial of unauthorized claim is expected safe behavior, not an operational defect.
