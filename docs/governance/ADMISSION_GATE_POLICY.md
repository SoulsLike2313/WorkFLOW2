# ADMISSION GATE POLICY

Policy class: Level 2 control policy.

Authority inputs:

- `docs/governance/FIRST_PRINCIPLES.md`
- `docs/governance/GOVERNANCE_HIERARCHY.md`
- `workspace_config/GITHUB_SYNC_POLICY.md`
- `workspace_config/COMPLETION_GATE_RULES.md`

## 1) Objective

Define hard completion admission criteria for any task result.

No completion admission without repo-visible truth and sync integrity.

## 2) Mandatory completion requirements

All requirements are mandatory:

1. required outputs created at exact declared paths
2. required validation steps executed
3. required checks passed (or explicitly downgraded with allowed warning policy)
4. task-scoped changes committed
5. pushed to canonical mirror remote (`safe_mirror`)
6. local and `safe_mirror/main` parity confirmed
7. unresolved critical contradictions = none

## 3) Mandatory artifact set

At minimum, completion package must include:

1. changed files list
2. commit SHA
3. sync evidence (`HEAD`, `safe_mirror/main`, divergence)
4. validation evidence (run IDs or command outputs)
5. blocker list (or explicit `none`)

Where applicable:

6. regenerated manifests/reports used as state authority
7. export artifacts and verdict manifests for external-sharing tasks

## 4) Mandatory checks

Required commands/checks:

1. `git status --short --branch`
2. `git rev-parse HEAD`
3. `git rev-parse safe_mirror/main`
4. `git rev-list --left-right --count HEAD...safe_mirror/main`
5. `python scripts/check_repo_sync.py --remote safe_mirror --branch main`
6. contradiction scan against canonical sources
7. task-specific validation checks declared in task contract

## 5) Allowed verdict states

Allowed states:

1. `PASS`
2. `PASS_WITH_WARNINGS` (only if warnings are non-critical and explicitly listed)
3. `FAIL`
4. `NOT_COMPLETED`

## 6) Completion-blocking states

Completion is forbidden when any is true:

1. worktree not clean at completion boundary
2. divergence not `0/0`
3. `HEAD != safe_mirror/main`
4. missing required artifact
5. required check not executed
6. unresolved critical contradiction
7. blocker present without explicit disclosure
8. safe-share verdict required but not achieved

## 7) Repo-visible truth rule

Completion claims are valid only for repo-visible state:

1. local-only results are non-admissible
2. uncommitted outputs are non-admissible
3. unpushed commits are non-admissible
4. stale review artifacts cannot substitute current state evidence

## 8) Sync integrity rule

Canonical sync target:

- `safe_mirror/main` (`WorkFLOW2`)

Admission condition:

1. local HEAD equals remote HEAD
2. divergence equals `0/0`
3. sync check tool returns `PASS`

