# Integration Inbox Policy

## Purpose

Define canonical entrypoint and review states for external helper deliveries.

## Folder Contract

- `integration/inbox/` - newly delivered packages
- `integration/review_queue/` - reviewed packages with review artifacts
- `integration/accepted/` - accepted candidate packages
- `integration/rejected/` - rejected packages
- `integration/quarantine/` - suspicious or malformed packages

## Review Flow

1. scan inbox
2. validate handoff schema
3. validate task_id and scope contract
4. validate forbidden paths are untouched
5. validate metadata completeness
6. produce decision:
   - `ACCEPT_CANDIDATE`
   - `REJECT`
   - `QUARANTINE`

## Decision Triggers

- `QUARANTINE`:
  - malformed package schema
  - unsafe payload indicators
  - unresolved package identity
- `REJECT`:
  - scope violation
  - forbidden path touched
  - missing required checks/outputs
- `ACCEPT_CANDIDATE`:
  - schema valid
  - scope valid
  - required metadata present

## Canonical Protection

Integration decision does not auto-merge into canonical branch.
Final acceptance remains creator-authority operation.

