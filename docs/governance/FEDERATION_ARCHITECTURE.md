# Federation Architecture

## Model Summary

Federated v1 model separates roles:

- creator-capable node (rank-derived from `EMPEROR`)
- helper nodes with tiers (`PRIMARCH=high`, `ASTARTES=low`)
- integration posture (inbox-based review and decision preparation)

Current operational framing:

- Federation is an operational development block, not the sovereign core.
- Current stage has one real department: `Analytics Department`.
- `platform_test_agent` is the current implementation of `Analytics Department`.
- Other project lines are operational intake/analysis subjects, not departments.
- Canonical model surface: `docs/governance/FEDERATION_OPERATIONAL_MODEL.md`.

## Node Roles

### Creator Node

- derived from rank model (`EMPEROR -> creator`)
- owns canonical acceptance and final PASS decisions
- can review and accept/reject external blocks

### Helper Node

- default for non-emperor rank
- executes only task-scoped blocks via task_id contract
- returns work through handoff package

### Integration Posture

- posture overlay used while reviewing external deliveries
- uses inbox review flow to classify packages
- produces accept/reject/quarantine decision artifacts
- does not change base authority mode

## Safe Mirror Role

- `WorkFLOW2` remains public safe mirror only
- not a substitute for emperor proof or rank-derived creator mode
- not a direct integration bypass

## Canonical Flow

1. helper resolves `task_id`
2. helper executes within allowed scope
3. helper prepares handoff package
4. package enters `integration/inbox`
5. canonical machine reviews package in integration flow
6. rank-derived creator mode decides canonical acceptance/rejection

## Invariants

- local sovereign substrate path never tracked in repository
- full copy without genome/substrate resolves to `ASTARTES -> helper(low)`
- canonical acceptance rights remain creator-only (`EMPEROR`-derived)
- `repo + genome + substrate -> EMPEROR` (substrate decisive; genome is not emperor path)
