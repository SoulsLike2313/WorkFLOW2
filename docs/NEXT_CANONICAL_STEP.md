# Next Canonical Step

- step_id: `next-step-federation-integration-layer-v1`
- effective_date_utc: `2026-03-17`
- previous_accepted_stage: `governance-acceptance-foundation-closed`

## What Do We Do Next

Canonical next execution step is:

`federation / integration layer v1 hardening`

This means:

1. creator/helper/integration machine modes with external creator authority detection contract
2. task-id block execution workflow for helper nodes
3. integration inbox review flow for external handoff packages
4. canonical acceptance remains creator-only

## Canonical Goal

Make parallel multi-node development operational without losing canonical authority:

1. full repo copy without authority marker resolves to helper mode
2. helper nodes execute only `task_id` blocks
3. external blocks are delivered through integration inbox only
4. canonical creator machine remains final acceptance authority

## Canonical Scope

- target layer:
  - `docs/governance/**` (federation/integration policies)
  - `workspace_config/**` (mode/task/handoff/inbox contracts)
  - `integration/**`
  - `tasks/**`
  - `scripts/detect_machine_mode.py`
  - `scripts/resolve_task_id.py`
  - `scripts/prepare_handoff_package.py`
  - `scripts/review_integration_inbox.py`
  - `scripts/repo_control_center.py` (mode/integration checks only)
  - root context docs/manifests integration
- forbidden scope:
  - product feature development
  - optimization branch work
  - UI work
  - safe_mirror architecture rewrite

## Canonical Acceptance Criteria

1. creator authority contract exists (env + marker schema) without tracked local authority path leakage
2. helper fallback works when authority is absent
3. task-id resolution works for registry tasks
4. handoff package generation works
5. integration inbox review flow returns `ACCEPT_CANDIDATE | REJECT | QUARANTINE`
6. repo control center reports machine mode and integration readiness
7. sync parity with `safe_mirror/main` remains `0/0` and worktree clean

## Canonical Prohibitions For This Step

1. no completion claim from helper mode
2. no governance override from helper mode
3. no direct canonical merge from external handoff package
4. no creator authority path disclosure in tracked repository

## Rejection Condition

Any request that bypasses creator-only canonical acceptance or integration inbox route must be rejected:

```text
STATUS: REJECTED
REASON: non-canonical
NO EXECUTION
```
