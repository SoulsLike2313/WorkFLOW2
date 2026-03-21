# CONSTITUTION_CHANGE_AUTHORITY_POLICY

Status:
- policy_version: `v1`
- scope: `constitutional change authority and role boundaries`
- non_goal: `no broad governance-stack redesign`

## 1) Purpose

Make constitutional mutation authority explicit and fail-closed:
1. Constitution is a protected foundation.
2. Sovereign constitutional mutation is Emperor-only.
3. Proposal work is separated from mutation authority.

## 2) Constitutional Change Classes

1. `constitutional_commentary`
   - interpretation notes and non-binding commentary.
2. `constitutional_proposal`
   - structured proposal for constitutional adjustment.
3. `constitutional_amendment_candidate`
   - prepared candidate package for sovereign review (non-binding).
4. `sovereign_constitutional_mutation`
   - binding constitutional mutation with sovereign authority.

Runtime claim-class mapping:
1. `constitutional_commentary` -> `constitutional_commentary_claim`
2. `constitutional_proposal` -> `bounded_engineering_proposal`
3. `constitutional_amendment_candidate` -> `constitutional_amendment_candidate_claim`
4. `sovereign_constitutional_mutation` -> `constitutional_mutation_claim`

## 3) Authority Model by Rank

### EMPEROR
Can:
1. authorize and execute `constitutional_mutation_claim`;
2. accept/reject amendment candidates;
3. finalize constitutional state transition.

Cannot:
1. bypass fail-closed constitutional checks;
2. transfer constitutional authority via mirror/import/bundle.

### PRIMARCH
Can:
1. produce `constitutional_proposal`;
2. prepare `constitutional_amendment_candidate`;
3. submit policy-grade recommendations.

Cannot:
1. execute sovereign constitutional mutation;
2. claim constitutional finalization authority.

### ASTARTES
Can:
1. provide `constitutional_commentary` and evidence support;
2. execute bounded analysis/report tasks.

Cannot:
1. prepare final amendment candidate authority package;
2. execute or claim constitutional mutation authority.

## 4) Explicit Non-Equivalence Rules

1. creator authority marker != constitutional sovereign mutation authority.
2. creator/development activity != constitutional mutation authority.
3. portable session / import bundle / safe mirror context != constitutional mutation authority.
4. dossier/recommendation/commentary artifacts != constitutional mutation authority.

## 5) Mandatory Preconditions for Sovereign Constitutional Mutation

1. detected rank must be `EMPEROR`.
2. `constitutional_mutation_claim` must pass claim-denial gates.
3. constitutional checks and contradiction checks must be known/explicit before mutation closure.
4. resulting constitutional state must remain repo-visible and auditable.

## 6) References

1. `docs/governance/WORKFLOW2_CONSTITUTION_V1.md`
2. `docs/governance/NODE_AUTHORITY_RANK_POLICY_V1.md`
3. `docs/governance/SOVEREIGN_CLAIM_DENIAL_POLICY_V1.md`
4. `docs/governance/CONSTITUTION_AMENDMENT_FLOW.md`
5. `docs/governance/CONSTITUTION_IMMUTABILITY_BOUNDARY.md`
