# EMPEROR_CHARACTER_EVOLUTION_LEDGER_V1

Status:
- ledger_state: `ACTIVE`
- mutation_mode: `owner_controlled_repo_visible_only`
- hidden_learning: `FORBIDDEN`

## Purpose

Control kernel evolution through explicit, reviewable, owner-approved entries only.

## Ledger Rules

1. New observation enters as `CANDIDATE` only.
2. Candidate must be repo-visible.
3. Candidate must explain:
   - why stable,
   - why project-useful,
   - what evidence supports it.
4. Candidate becomes kernel entry only after explicit owner acceptance.
5. Rejected candidates remain rejected (no silent absorption).
6. Hidden or implicit learning is forbidden.

## Candidate Template

- candidate_id:
- proposed_at_utc:
- proposed_by:
- scope:
- stability_evidence_paths:
- usefulness_statement:
- risk_if_wrong:
- decision_status: `CANDIDATE | ACCEPTED | REJECTED`
- decision_by:
- decision_at_utc:
- decision_note:
- kernel_change_paths:

## Current Candidate Registry

None.

## Decision History

None.

## Rejected Candidate Registry

None.

## Change Control

1. Every accepted entry must reference exact kernel diff path.
2. Every decision must be represented in this ledger.
3. Missing ledger record invalidates claimed kernel mutation.

