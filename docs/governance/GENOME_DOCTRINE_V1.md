# GENOME_DOCTRINE_V1

Status:
- doctrine_version: `v1`
- doctrine_layer: `status`
- scope: `Primarch status-attestation document`

## 1) Definition

`Genome` is a status document.
It grants the right to be recognized as `Primarch` within the governed command model.

## 2) What Genome Gives

1. Primarch status attestation for the bound subject identity.
2. Eligibility for Primarch-level non-sovereign directive/proposal lanes.
3. Traceable status origin from Emperor authority.

## 3) What Genome Does Not Give

1. No task/order payload by itself.
2. No sovereign mutation authority by itself.
3. No automatic constitutional mutation authority.
4. No replacement for warrant/charter/gramota command documents.

## 4) Issuer and Signature Discipline

1. Issuer rank: `EMPEROR` only.
2. Signature class: `genome_status_signature`.
3. Minimum assurance: `locally_verifiable` (preferred `emperor_local_only_verifiable`).
4. Verification must bind:
   - issuer identity,
   - subject identity,
   - granted status level.

## 5) Required Distinguishers

A valid Genome must be explicitly distinguishable from command/binding documents:
1. `document_type=genome`
2. `document_role_layer=status`
3. `status_granted_level=PRIMARCH`
4. `tasking_marker=false`
5. `binding_marker=false`

## 6) Nearest Equivalents (Current Repo)

1. nearest status-equivalent surfaces:
   - `docs/governance/NODE_AUTHORITY_RANK_POLICY_V1.md`
   - `scripts/validation/detect_node_rank.py`
2. Genome does not replace rank-proof chain; it formalizes status-attestation semantics.
