# Next Canonical Step

- step_id: `next-step-operator-command-execution-layer-v1`
- effective_date_utc: `2026-03-17`
- previous_accepted_stage: `operator-query-layer-command-surface-accepted`

## What Do We Do Next

Canonical next execution step is:

`operator command execution layer v1`

This means:

1. classify operator commands deterministically
2. enforce authority/policy/precondition checks before execution
3. execute only policy-allowed actions by wave (`1A`, `1B`, `1C`)
4. return unified execution contract with artifacts/state-change tracking
5. freeze readiness only after consistency + creator-grade validation

## Canonical Goal

Make operator commands executable without relaxing governance boundaries:

1. no free-form uncontrolled execution
2. creator-only operations remain creator-only
3. mutable commands stay guarded and dry-run by default
4. every command run leaves repo-visible runtime evidence

## Canonical Scope

- target layer:
  - `docs/governance/OPERATOR_COMMAND_*`
  - `workspace_config/operator_command_registry.json`
  - `scripts/operator_command_surface.py`
  - `runtime/operator_command_layer/*`
  - `docs/review_artifacts/OPERATOR_COMMAND_*`
  - root context docs/manifests integration
- forbidden scope:
  - product feature development
  - governance baseline rewrite
  - authority model weakening
  - UI expansion

## Canonical Acceptance Criteria

1. Wave `1A/1B/1C` command classes implemented
2. unified registry and execution contract are active
3. command routing consistency check passes on golden pack
4. creator-grade chain remains green after integration
5. sync parity with `safe_mirror/main` remains `0/0` and worktree clean

## Canonical Prohibitions For This Step

1. no command may bypass policy checks
2. no command may bypass authority checks
3. no mutable execution without guard (`dry_run` or explicit `--allow-mutation`)
4. no completion claim when command layer evidence is missing

## Rejection Condition

Any request that requires policy/authority override must be rejected:

```text
STATUS: REJECTED
REASON: non-canonical
NO EXECUTION
```
