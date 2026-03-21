# CONSTITUTION_AMENDMENT_FLOW

Status:
- flow_version: `v1`
- scope: `bounded constitutional amendment lifecycle`
- non_goal: `no automation-heavy constitutional orchestration framework`

## 1) Flow Objective

Separate preparation from authority:
1. proposal and candidate work is allowed in bounded non-sovereign mode;
2. constitutional mutation remains sovereign-only (`EMPEROR`).

## 2) Amendment Lifecycle

1. `Commentary Intake`
   - inputs: constitutional commentary, contradiction notes, drift findings.
   - output: `constitutional_commentary` (non-binding).

2. `Proposal Formation`
   - owner: Primarch/creator-grade non-sovereign lane.
   - output: `constitutional_proposal`.
   - claim class: `bounded_engineering_proposal`.

3. `Amendment Candidate Packaging`
   - owner: Primarch lane.
   - output: `constitutional_amendment_candidate`.
   - claim class: `constitutional_amendment_candidate_claim`.
   - state: review-ready, not binding.

4. `Sovereign Constitutional Mutation Decision`
   - owner: Emperor-only authority.
   - claim class: `constitutional_mutation_claim`.
   - result: `ACCEPT_MUTATION` or `REJECT_MUTATION`.

5. `Post-Mutation Validation`
   - mandatory: contradiction visibility, constitutional status coherence, repo-visible change trace.
   - output: constitutional mutation evidence package.

## 3) Stop Conditions

Stop and deny mutation when at least one condition is true:
1. rank is not `EMPEROR` for mutation step;
2. claim-denial check rejects `constitutional_mutation_claim`;
3. mutation request has proposal/candidate ambiguity;
4. required constitutional validation status is unknown or contradictory.

## 4) Roles and Handoffs

1. Astartes: commentary/evidence support only.
2. Primarch: proposal and amendment candidate preparation.
3. Emperor: sovereign mutation authority and constitutional finalization.

## 5) Evidence Requirements

Minimal mutation chain:
1. proposal/candidate artifact;
2. mutation decision artifact;
3. post-mutation validation output;
4. canonical surface update trace.
