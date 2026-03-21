# Helper Node Policy

## Purpose

Define helper-mode boundaries under rank-derived machine mode v2.

## Helper Mode Definition

Node is `helper` when rank is not `EMPEROR`.

Tiers:
1. `helper(high)` = `PRIMARCH`
2. `helper(low)` = `ASTARTES`

Helper mode is execution-capable but not canonical-authoritative.

## Allowed Operations

Common helper operations:
- resolve and execute assigned `task_id` block
- edit only task-allowed paths
- run local checks for assigned block
- prepare handoff package for integration inbox flow
- report risks, blockers, and local evidence

Additional `helper(high)` operations:
- issue bounded engineering proposals
- issue amendment candidates in non-sovereign envelope

## Forbidden Operations

- canonical completion declaration
- governance core override
- protected-layer mutation outside assigned scope
- direct canonical integration
- final PASS claim for global repository state

## Hard Guards

1. `PRIMARCH` never maps to creator mode.
2. `ASTARTES` never maps to creator mode.
3. Only `EMPEROR` maps to creator mode.
4. Integration posture never upgrades helper tier or authority.

## Output Contract

Helper output must be delivered only as structured handoff package into integration inbox flow.
