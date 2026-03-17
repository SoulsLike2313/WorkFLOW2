# Next Canonical Step

- step_id: `next-step-operator-task-program-layer-v1`
- effective_date_utc: `2026-03-17`
- previous_accepted_stage: `operator-command-execution-layer-v1-accepted`

## What Do We Do Next

Canonical next execution step is:

`operator task / program layer v1`

This means:

1. map operator task/program requests to deterministic `program_class` and `program_id`
2. enforce authority/policy/precondition checks before step execution
3. execute step plans through accepted operator command execution layer
4. emit checkpoint, step-level evidence, and final program contract
5. freeze readiness only after golden consistency + creator-grade validation

## Canonical Goal

Make repeatable operator programs executable without relaxing governance boundaries:

1. no uncontrolled autonomous planning
2. creator-only program flows remain creator-only
3. mutable program steps stay guarded and dry-run by default
4. every run leaves repo-visible runtime evidence and deterministic next step

## Canonical Scope

- target layer:
  - `docs/governance/OPERATOR_PROGRAM_*`
  - `workspace_config/operator_program_registry.json`
  - `scripts/operator_program_surface.py`
  - `runtime/operator_program_layer/*`
  - `docs/review_artifacts/OPERATOR_PROGRAM_*`
  - root context docs/manifests integration
- forbidden scope:
  - product feature development
  - governance baseline rewrite
  - authority model weakening
  - UI expansion

## Canonical Acceptance Criteria

1. Wave `2A/2B/2C` program classes implemented
2. unified registry and execution contract are active
3. program routing consistency check passes on golden pack
4. creator-grade chain remains green after integration
5. sync parity with `safe_mirror/main` remains `0/0` and worktree clean

## Canonical Prohibitions For This Step

1. no program may bypass policy checks
2. no program may bypass authority checks
3. no mutable execution without guard (`dry_run` or explicit `--allow-mutation` + confirmation)
4. no completion claim when program layer evidence is missing

## Rejection Condition

Any request that requires policy/authority override must be rejected:

```text
STATUS: REJECTED
REASON: non-canonical
NO EXECUTION
```
