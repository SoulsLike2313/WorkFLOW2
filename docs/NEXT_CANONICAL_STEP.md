# Next Canonical Step

- step_id: `next-step-gameruai-focused-fix-cycle`
- effective_date_utc: `2026-03-14`
- previous_accepted_stage: `machine-alignment-hardening`

## What Do We Do Next

Canonical next execution step is:

`GameRuAI focused fix cycle` with strict bounded scope.

## Canonical Goal

Stabilize `projects/GameRuAI` on two blocked axes:

1. verification timeout during `python -m pytest -q`
2. UI snapshot pipeline failure with missing required product states

## Canonical Scope

- target project: `projects/GameRuAI`
- allowed scope:
  - verification timeout root cause and fix
  - UI snapshot capture failure root cause and fix
  - update GameRuAI verification/UI summaries and fix-cycle report
- allowed paths:
  - `projects/GameRuAI/**`
  - `runtime/projects/game_ru_ai/**`
  - `docs/review_artifacts/GAMERUAI_FIX_CYCLE_REPORT.md`
- forbidden paths:
  - any non-GameRuAI product project paths
  - architecture/governance redesign files outside required report updates

## Canonical Outputs

- updated `projects/GameRuAI` verification summaries
- updated `projects/GameRuAI` UI-QA summaries and snapshot manifest
- updated `docs/review_artifacts/GAMERUAI_FIX_CYCLE_REPORT.md`
- run_id-linked evidence for verification and UI-QA

## Canonical Acceptance Criteria

1. verification run finishes with explicit exit code and summary
2. UI snapshot manifest contains captured required product states
3. fix-cycle report includes causes, exact fixes, run_ids, and affected files
4. no side work outside bounded scope

## Canonical Prohibitions For This Step

1. no platform rebuild
2. no new module overhauls
3. no cross-project refactors
4. no non-requested artifacts
5. no scope expansion beyond GameRuAI fix cycle

## Rejection Condition

Any task request that conflicts with this step must be rejected as:

```text
STATUS: REJECTED
REASON: non-canonical
NO EXECUTION
```