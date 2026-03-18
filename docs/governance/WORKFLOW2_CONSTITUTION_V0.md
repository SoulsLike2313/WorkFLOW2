# WORKFLOW2_CONSTITUTION_V0

Status:
- state: `historical_bootstrap`
- successor: `docs/governance/WORKFLOW2_CONSTITUTION_V1.md`

## 1. Purpose
WorkFLOW2 is an evidence-governed operator control system where execution rights, completion claims, and canonical state are determined by explicit authority, policy gates, and repo-visible proof.

## 2. Constitutional Role
- This document is the constitutional core for execution meaning, authority meaning, truth-state meaning, and completion meaning.
- It governs interpretation across governance/query/command/task-program/mission layers.
- It does not replace layer contracts; it constrains them.

## 3. Core Entities
- `mission`: bounded work package with scope, non-goals, checkpoints, and acceptance criteria.
- `program`: deterministic multi-step execution unit used by missions.
- `task`: scoped execution unit routed to command/program/mission surfaces.
- `command`: single controlled operator action with explicit preconditions.
- `artifact`: file output produced by execution, review, or reporting.
- `evidence`: artifact set sufficient to verify a claim.
- `decision`: explicit accepted/rejected determination tied to evidence.
- `review`: structured evaluation of evidence against policy.
- `certification`: formal statement that acceptance criteria are met.
- `authority`: execution rights context derived from mode + policy.
- `source_of_truth`: highest-precedence canonical source for a claim.
- `runtime_state`: generated execution state that is evidence, not policy authority.

## 4. Truth States
- `fact`: repo-visible, verifiable, currently valid claim.
- `hypothesis`: unverified claim pending evidence.
- `proposal`: intended change pending approval or execution.
- `decision`: explicit determination with policy basis.
- `certified_result`: decision with completed required evidence and gates.
- `stale`: once-valid claim contradicted by newer canonical evidence.
- `rejected`: claim/action denied by policy, authority, or validation.
- `superseded`: replaced by newer accepted canonical statement.
- `unknown`: no sufficient evidence in canonical sources.

## 5. Authority Lattice
- `creator authority`: may execute creator-only transitions, certification acceptance, and canonical completion claims.
- `helper role`: may execute bounded tasks/programs/missions inside allowed scope; cannot declare canonical completion.
- `integration role`: may review/classify handoff artifacts; cannot override creator-only acceptance.
- Allowed action class is always `role + policy + preconditions`.
- Escalation is mandatory for blocked creator-only transitions and unresolved critical contradictions.
- Completion authority and certification authority are creator-only.

## 6. Completion Law
- Completion exists only when output is repo-visible, required checks are passed, and sync parity is explicit.
- `draft`/`progress` means work exists but gates/evidence are incomplete.
- Certifiable completion requires:
  - authoritative mode for required action class,
  - passed policy/validation gates,
  - evidence chain linked to current accepted state,
  - clean sync discipline (`worktree_clean=true`, divergence `0/0`).

## 7. Contradiction Law
- Conflicting claims are resolved by canonical source precedence.
- Lower-precedence claims are marked `stale` or `non-canonical` when contradicted.
- Unresolved critical contradiction blocks completion and certification.
- Narrative must be updated to match accepted canonical state after each certified phase.

## 8. Anti-Sloppiness Law
WorkFLOW2 treats the following as invalid behavior:
- cosmetic progress without state change
- unsupported claims without evidence
- narrative drift between canonical surfaces
- unresolved contradiction at completion time
- fake completion (PASS without gates)
- uncontrolled scope expansion
- missing evidence chain for decisions

## 9. Initiative Boundaries
- Initiative is allowed only inside explicit scope, policy, and authority bounds.
- Bounded initiative ends where authority, policy, or accepted scope ends.
- Forbidden without explicit authority:
  - creator-only transitions from non-creator mode
  - policy-bypassing mutation
  - canonical completion/certification claims without required gates

## 10. Narrative Law
- Repository narrative is a control surface, not decoration.
- Canonical narrative surfaces must not contradict each other on phase state, authority model, or next step.
- Narrative clarity is a system requirement because machine routing and human verification depend on it.

## 11. V1 Doctrine
- Evidence outranks eloquence.
- Authority precedes action.
- Policy gates are executable constraints, not suggestions.
- Review is part of production.
- Completion is a gated state, not a statement.
- State must be explicit and machine-readable.
- Contradictions must be resolved or escalated, never ignored.
- Initiative is allowed, sovereignty is not.
- Runtime output is evidence; canonical docs define policy.
- Sync discipline is part of correctness.

## 12. Not Yet
- No new brain-level implementation layers before constitutional closure.
- No premature federation/factory expansion.
- No cosmetic architecture growth in place of constitutional hardening.
- No large optimization wave before constitutional narrative and source precedence are stable.
