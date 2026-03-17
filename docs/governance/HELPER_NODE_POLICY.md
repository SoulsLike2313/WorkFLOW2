# Helper Node Policy

## Purpose

Define helper-node execution boundaries for full repository copies without creator authority marker.

## Helper Mode Definition

Node is `helper` when creator authority detection is absent or invalid.

Helper mode is execution-capable for assigned block tasks but not canonical-authoritative.

## Allowed Operations

- resolve and execute assigned `task_id` block
- edit only task-allowed paths
- run local checks for assigned block
- prepare handoff package for integration inbox
- report risks, blockers, and local evidence

## Forbidden Operations

- canonical completion declaration
- governance core override
- protected-layer mutation outside assigned scope
- direct canonical integration
- final PASS claim for global repository state

## Output Contract

Helper output must be delivered only as structured handoff package into integration inbox flow.

