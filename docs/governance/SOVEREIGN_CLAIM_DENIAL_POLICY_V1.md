# SOVEREIGN_CLAIM_DENIAL_POLICY_V1

Status:
- policy_version: `v1.rewritten_for_status_model_v2`
- scope: `deny unauthorized sovereign and elevation claims`

## 1) Claim Classes

Sovereign-only:
1. `canonical_acceptance_claim`
2. `sovereign_policy_change_claim`
3. `emperor_rank_claim`
4. `genome_bundle_issuance_claim`
5. `local_sovereign_substrate_activation_claim`
6. `unrestricted_structural_mutation_claim`
7. `constitutional_mutation_claim`

Primarch-allowed non-sovereign:
1. `primarch_rank_claim`
2. `bounded_engineering_proposal`
3. `constitutional_amendment_candidate_claim`
4. `constitutional_commentary_claim`
5. `execution_report_claim`
6. `denial_as_expected_claim`

Astartes-allowed non-sovereign:
1. `constitutional_commentary_claim`
2. `execution_report_claim`
3. `denial_as_expected_claim`

## 2) Hard Guard Rules

1. ASTARTES cannot claim `primarch_rank_claim`.
2. ASTARTES cannot claim any sovereign-only class.
3. PRIMARCH cannot claim sovereign-only classes.
4. PRIMARCH cannot issue `constitutional_mutation_claim`.
5. only EMPEROR can issue `genome_bundle_issuance_claim`.
6. `genome bundle` material cannot satisfy `local_sovereign_substrate_activation_claim`.

## 3) Signature/Identity Gate

1. sovereign-only classes require `signature_status=valid`, `issuer_identity_status=verified`, and assurance at least `locally_verifiable`.
2. bounded engineering and amendment candidates require at least `structurally_bound`.
3. insufficient/unknown assurance narrows authority fail-closed.

## 4) Context Fail-Closed

1. invalid repo/root context -> deny elevated claims;
2. safe mirror or portable/import context cannot elevate claims;
3. denial under these rules is expected and correct behavior.
