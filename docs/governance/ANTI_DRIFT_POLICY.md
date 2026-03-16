# ANTI DRIFT POLICY

Policy class: Level 2 control policy.

Authority inputs:

- `docs/governance/FIRST_PRINCIPLES.md`
- `docs/governance/GOVERNANCE_HIERARCHY.md`
- `docs/governance/GOVERNANCE_GAP_AUDIT.md`

## 1) Objective

Detect and stop drift from canonical task intent, architecture, and governance truth.

## 2) Drift classes and detectors

## 2.1 Goal drift

Definition:

- work shifts away from declared task objective

Detection:

1. outputs do not map to requested deliverables
2. significant work appears outside task scope

Response:

1. stop further expansion
2. return to declared goal
3. mark off-scope items as rejected/deferred

## 2.2 Cosmetic work drift

Definition:

- visible activity without operational governance value

Detection:

1. wording changes with no control or verification impact
2. artifact growth without enforcement gain

Response:

1. remove non-operative edits from task claim
2. require measurable control effect for each doc change

## 2.3 Scope drift

Definition:

- unrequested paths/modules modified

Detection:

1. changed files exceed allowed task scope
2. additional subsystems touched without explicit contract

Response:

1. isolate and revert unrequested scope (if safe and owned by current task)
2. keep only bounded scope changes
3. report excluded work explicitly

## 2.4 Architecture drift

Definition:

- canonical model changes without explicit architecture task

Detection:

1. source-of-truth model changed implicitly
2. sync target model changed implicitly
3. policy hierarchy altered without dedicated governance task

Response:

1. block completion
2. require explicit architecture decision record before change

## 2.5 Doc drift

Definition:

- docs no longer match manifests/repo reality

Detection:

1. README/REPO_MAP/MACHINE_CONTEXT mismatch with manifests
2. governance docs contain stale canonical references

Response:

1. reconcile docs to canonical source precedence
2. rerun contradiction control checks

## 2.6 Manifest/report drift

Definition:

- generated state artifacts no longer reflect current committed reality

Detection:

1. manifest/report head SHA does not match final committed state
2. generated timestamps imply stale state against current head

Response:

1. regenerate required state artifacts
2. commit regenerated artifacts
3. re-validate sync parity and contradiction checks

## 3) Mandatory drift check points

Run drift checks:

1. before starting substantial edits
2. before commit
3. before push
4. before final verdict

## 4) Drift severity

`CRITICAL`:

1. architecture drift
2. sync-integrity drift
3. unresolved critical contradiction

Action:

1. completion blocked
2. status must be `FAIL` or `NOT_COMPLETED` until resolved

`MAJOR`:

1. scope drift
2. doc drift affecting machine interpretation

Action:

1. must be fixed in current task or explicitly deferred as blocker

`MINOR`:

1. non-authoritative wording drift without execution impact

Action:

1. may be deferred with explicit note

## 5) Completion guard

Completion is forbidden if any critical drift remains unresolved.

Required final evidence:

1. drift check summary
2. contradiction status
3. sync parity proof
4. bounded-scope changed-file list

