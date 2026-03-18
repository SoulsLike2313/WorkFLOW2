# GUARDED_BASELINE_TRANSITION_PREFLIGHT_REPORT

## Scope
Preflight investigation and closure for guarded baseline transition dependency issue:
- target dependency: `program.wave2b.review_certification_sequence.v1`
- target step: `S2 / inbox_review`
- previous issue: inbox review argument contract mismatch

## Root Cause
Two contract gaps existed in the program -> command interface:
1. `program.wave2b.review_certification_sequence.v1` step `S2` passed `inbox_mode`, but `scripts/operator_command_surface.py` did not accept `--inbox-mode`.
2. `scripts/operator_task_program_surface.py` initialized `inbox_mode` as empty by default, so `pass_args=["inbox_mode"]` could produce missing step input for `inbox_review`.

## Affected Path
- mission path: `mission.wave3c.guarded_baseline_transition.v1`
- dependency chain: `program.wave2c.guarded_governance_maintenance.v1` -> `program.wave2c.control_artifacts_rebuild.v1` -> `program.wave2b.review_certification_sequence.v1`
- affected interface files:
  - `scripts/operator_command_surface.py`
  - `scripts/operator_task_program_surface.py`

## Blocker Severity
- before closure: `CONDITIONAL_BLOCKER` for guarded transition success path when review certification sequence reached inbox review step.
- after closure: argument mismatch is `RESOLVED`.

## Change Applied
1. `scripts/operator_command_surface.py`
- added parser support for `--inbox-mode`.
- normalized handling in `action_inbox_review()`:
  - accepts `inbox_mode` metadata;
  - optional routing hint from `inbox_mode` values (`route`, `route_apply`).

2. `scripts/operator_task_program_surface.py`
- applied `default_context` merge from registry into runtime context.
- added safe default `inbox_mode=review_queue` when missing.

## Post-Check Result
- check run: `program.wave2b.review_certification_sequence.v1` (run_id `program-wave2c-20260318T021510798226Z`).
- result relevant to mismatch:
  - step `S2` command executed with `--inbox-mode review_queue`.
  - `inbox_review` step verdict: `SUCCESS`.
- conclusion: original inbox arg contract mismatch is fixed.

## Current Guarded Baseline Transition Status
- mission run: `mission.wave3c.guarded_baseline_transition.v1` (run_id `mission-wave3c-20260318T021530342547Z`).
- current block reason is no longer arg-contract mismatch.
- current block reason is precondition gate:
  - `sync_in_sync` failed
  - `worktree_clean` failed

## Fixed / Not Fixed / Bypassed
- mismatch status: `FIXED`.
- guarded mission full success in current local run: `NOT FIXED` (blocked by sync/worktree preconditions).
- bypass status: `INTENTIONALLY NOT BYPASSED` (guards preserved).

## Safe Workaround
For pilot readiness and proof continuity:
- use guarded reference mission `mission.wave3c.creator_only_certification.v1` as mandatory guarded success path;
- treat `mission.wave3c.guarded_baseline_transition.v1` as conditional mission requiring clean and in-sync workspace before execution.

## Final Technical State
- original dependency mismatch: closed.
- remaining constraint: operational preconditions, not contract mismatch.
