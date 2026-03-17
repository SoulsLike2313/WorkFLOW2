# MACHINE_OPERATOR_GUIDE

## What This Machine Is
WorkFLOW2 controller machine is a governance-first repo operator.
It validates repo truth, policy compliance, and admission readiness before any canonical acceptance.

## What It Does
- Runs machine mode detection (`creator`, `helper`, `integration`).
- Runs repo control checks (`bundle`, `full-check`, `sync`, `trust`, `evolution`).
- Produces machine-readable runtime reports.
- Produces plain one-screen status for human operators.
- Enforces creator-only canonical acceptance.

## What It Cannot Do
- Cannot declare canonical acceptance in `helper` mode.
- Cannot bypass governance gates when `governance_acceptance != PASS`.
- Cannot treat drifted sync as accepted state.

## Modes
- `creator`: creator authority present, canonical acceptance allowed.
- `helper`: no creator authority, block work only, no canonical acceptance.
- `integration`: review mode for external handoff/inbox processing.

## Verdict Meanings
- `PASS` / `TRUSTED` / `IN_SYNC` / `ADMISSIBLE`: gate is clear for its scope.
- `WARNING`: system usable, but operator attention is required.
- `BLOCKED`: gate cannot proceed until blockers are removed.
- `REJECTED`: admission is denied for current state.

## Key Terms In Plain Language
- `creator authority`: local authority switch proving this is the canonical creator machine.
- `governance acceptance`: hard governance gate before next-stage progression.
- `admission`: final operational permission gate for controlled progression.
- `trust`: combined confidence from sync + governance + contradiction + mirror/bundle checks.
- `evolution`: maturity progression status, separate from current operational health.

## Operator Action Model
1. Run `python scripts/repo_control_center.py bundle`.
2. Run `python scripts/repo_control_center.py full-check`.
3. Read `runtime/repo_control_center/plain_status.md`.
4. If blocked, follow `blocking_reason_category` and `blocking_reason_detail` from `one_screen_status.json`.
5. Continue only when required gates are green for the intended action.

## Fast Decision Rules
- Want canonical acceptance: require `machine_mode=creator`, `authority_present=true`, `governance_acceptance=PASS`, `admission=ADMISSIBLE`.
- Want bundle export only: `bundle=READY` is required.
- Want progression planning: read `evolution` and `next_canonical_step`.
