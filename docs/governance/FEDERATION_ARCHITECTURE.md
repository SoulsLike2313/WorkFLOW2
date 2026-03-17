# Federation Architecture

## Model Summary

Federated v1 model separates roles:

- creator node (canonical authority)
- helper nodes (block execution only)
- integration flow (inbox-based review and decision preparation)

## Node Roles

### Creator Node

- detected by external creator authority contract
- owns canonical acceptance and final PASS decisions
- can review and accept/reject external blocks

### Helper Node

- default for full repository copies without valid authority marker
- executes only task-scoped blocks via task_id contract
- returns work through handoff package

### Integration Mode

- canonical machine reviewing external deliveries
- uses inbox review flow to classify packages
- produces accept/reject/quarantine decision artifacts

## Safe Mirror Role

- `WorkFLOW2` remains public safe mirror only
- not a substitute for creator authority
- not a direct integration bypass

## Canonical Flow

1. helper resolves `task_id`
2. helper executes within allowed scope
3. helper prepares handoff package
4. package enters `integration/inbox`
5. canonical machine reviews package in integration flow
6. creator authority decides canonical acceptance/rejection

## Invariants

- creator authority path never tracked in repository
- full copy without marker always resolves to helper mode
- canonical acceptance rights remain creator-only

