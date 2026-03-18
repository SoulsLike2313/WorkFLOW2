# NODE_AUTHORITY_RANK_POLICY_V1

Status:
- policy_version: `v1`
- scope: `node-rank identity and claim boundaries`
- non_goal: `no federation/factory expansion; no new brain layer`

## 1) Purpose

Define rank authority classes:
1. `Emperor` - canonical sovereign node.
2. `Primarch` - creator-grade portable node without sovereign status.
3. `Astartes` - helper/integration node with bounded authority.

Creator/helper mode remains execution routing logic, while rank governs sovereignty/claim authority.

## 2) Rank Resolution Order

1. valid creator authority path + valid emperor-local proof -> `EMPEROR`
2. valid creator authority path + no emperor-local proof -> `PRIMARCH`
3. otherwise -> `ASTARTES`

Hard rule:
- portable/safe-mirror copy never auto-inherits Emperor rank.

## 3) Rank Capabilities and Limits

### Emperor
Can:
1. execute creator-grade operations;
2. make sovereign canonical acceptance decisions;
3. issue warrants/charters and sovereign directives.

Cannot:
1. transfer sovereignty by bundle copy;
2. bypass constitutional fail-closed gates.

### Primarch
Can:
1. execute creator-grade non-sovereign work;
2. issue proposals/reintegration recommendations;
3. operate within chartered boundaries.

Cannot:
1. assert Emperor rank;
2. assert sovereign final acceptance;
3. issue sovereign policy changes.

### Astartes
Can:
1. execute helper/integration bounded tasks;
2. submit execution evidence/report artifacts.

Cannot:
1. claim creator-grade sovereignty;
2. claim sovereign acceptance;
3. execute authority-bearing work without valid warrant/charter context.

## 4) Claim Restrictions by Rank

Emperor-only claim classes:
1. `canonical_acceptance_claim`
2. `sovereign_policy_change_claim`
3. `emperor_rank_claim`
4. `unrestricted_structural_mutation_claim`

Primarch and Astartes are restricted to non-sovereign claims per `SOVEREIGN_CLAIM_DENIAL_POLICY_V1.md`.

## 5) Warrant/Charter and Signature Coupling

1. authority-bearing execution on Astartes requires valid warrant or charter per `WARRANT_CHARTER_LIFECYCLE_V1.md`;
2. authority-bearing documents must carry issuer identity/signature assurance per `ISSUER_IDENTITY_AND_SIGNATURE_DISCIPLINE_V1.md`;
3. unknown/invalid identity-signature states narrow claim scope fail-closed.

## 6) Root and Mirror Constraints

1. canonical root expectation: `E:\CVVCODEX`.
2. `WorkFLOW2` is safe mirror only and does not provide sovereign rank proof.
3. root ambiguity or mismatch narrows rank confidence and blocks sovereign elevation.
