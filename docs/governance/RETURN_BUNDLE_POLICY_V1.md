# RETURN_BUNDLE_POLICY_V1

Status:
- policy_version: `v1`
- scope: `portable-to-canonical reintegration package policy`

## 1) Purpose

Define required structure and acceptance discipline for return bundles from non-canonical nodes.

## 2) Required Return Bundle Payload

Return bundle must include:

1. return summary document (scope, outcomes, blockers, risks);
2. changed-files list and rationale;
3. session identity (`base_head`, `session_end_head`);
4. check outputs and runtime truth surfaces;
5. explicit claim-to-evidence mapping.

## 3) Required Return Metadata

Return metadata must declare:

1. `source_node_rank_claim` (`Primarch` or `Astartes`);
2. `creator_authority_contract_state` (valid/invalid + evidence);
3. `emperor_sovereignty_claim` (must be `false` unless Emperor local proof validated on canonical machine);
4. `source_truth_basis` and branch/head details;
5. `claim_class` for requested reintegration action;
6. `issuer_identity` and `signature_status`;
7. unresolved blockers and known limitations.

## 4) Rank And Sovereignty Rules

1. Return bundle never auto-grants Emperor rank.
2. Primarch-origin bundle remains non-sovereign.
3. Astartes-origin bundle remains helper/integration scoped.
4. Sovereign claim acceptance is Emperor-only canonical decision.

## 5) Canonical Review Gates

Canonical machine must validate:

1. source precedence and identity integrity;
2. declared rank against authority evidence;
3. scope compliance and protected-zone rules;
4. claim class admissibility for declared rank;
5. issuer identity / signature status for authority-bearing documents;
6. required checks are present and reproducible;
7. no forbidden sovereign claims by non-Emperor nodes.

## 6) Reintegration Decisions

Allowed decisions:

1. `ACCEPT`
2. `PARTIAL_ACCEPT`
3. `REJECT`

Decision must be evidence-backed and recorded.

## 7) Rejection/Quarantine Triggers

Reject or quarantine when:

1. package identity/scope is malformed;
2. authority/rank claim is inconsistent with evidence;
3. protected-zone mutation attempted outside contract;
4. check evidence is missing or contradictory;
5. sovereign claim attempted without Emperor proof chain;
6. issuer identity/signature is invalid for requested authority scope.

## 8) Claim Restrictions

Non-Emperor return bundles cannot produce final sovereign canonical claims.

They can provide:
1. implementation deltas,
2. check evidence,
3. recommendation for canonical decision.
