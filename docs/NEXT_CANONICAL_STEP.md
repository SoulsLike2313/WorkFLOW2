# Next Canonical Step

- step_id: `next-step-operator-mission-layer-v1`
- effective_date_utc: `2026-03-17`
- previous_accepted_stage: `operator-task-program-layer-v1-accepted`

## What Do We Do Next

Canonical next execution step is:

`work package / mission layer v1`

This means:

1. map mission-level requests to deterministic `mission_class` and `mission_id`
2. decompose mission into registered program plans only
3. enforce authority/policy/precondition checks before mission execution
4. execute mission plans through accepted task/program layer
5. emit mission checkpoints, evidence aggregation, and completion verdict

## Canonical Goal

Make repeatable operator missions executable without relaxing governance boundaries:

1. no uncontrolled autonomous mission planning
2. creator-only missions remain creator-only
3. guarded state changes stay blocked unless explicit guard conditions are met
4. every mission run leaves repo-visible runtime evidence and deterministic next step

## Canonical Scope

- target layer:
  - `docs/governance/OPERATOR_MISSION_*`
  - `workspace_config/operator_mission_registry.json`
  - `scripts/operator_mission_surface.py`
  - `runtime/repo_control_center/operator_mission_*`
  - `docs/review_artifacts/OPERATOR_MISSION_*`
  - root context docs/manifests integration
- forbidden scope:
  - product feature development
  - governance baseline rewrite
  - authority model weakening
  - UI expansion

## Canonical Acceptance Criteria

1. Wave `3A/3B/3C` mission classes implemented
2. unified mission registry and execution contract are active
3. mission routing consistency check passes on final golden pack
4. creator-grade chain remains green after integration
5. sync parity with `safe_mirror/main` remains `0/0` and worktree clean

## Canonical Prohibitions For This Step

1. no mission may bypass policy checks
2. no mission may bypass authority checks
3. no guarded mutation without explicit guard and policy basis
4. no completion claim when mission-layer evidence is missing

## Rejection Condition

Any request that requires policy/authority override must be rejected:

```text
STATUS: REJECTED
REASON: non-canonical
NO EXECUTION
```
