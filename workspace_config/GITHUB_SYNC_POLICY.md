# GitHub Sync Policy

## Canonical Sync Identity

- Local working source of truth: `E:\CVVCODEX`
- Canonical public safe mirror remote: `safe_mirror`
- Canonical target branch: `safe_mirror/main`
- Canonical mirror repo: `WorkFLOW2`
- `WorkFLOW2` is public safe mirror only and not the full working repo

## Hard Completion Rule

No task completion is valid unless all are true:

1. result is repo-visible in tracked files
2. changes are committed and pushed to `safe_mirror/main`
3. sync parity is confirmed (`HEAD == safe_mirror/main`, divergence `0/0`)
4. mandatory self-verification completed

If any item fails: `NOT_COMPLETED`.

## Mandatory Post-Task Sequence

1. `git add <allowed_task_paths>`
2. `git commit -m "<task-scoped message>"`
3. `git push safe_mirror <active_branch>`
4. run sync gate checks

## Mandatory Sync Checks

- `git status --short --branch`
- `git rev-parse HEAD`
- `git rev-parse safe_mirror/main`
- `git rev-list --left-right --count HEAD...safe_mirror/main`
- `python scripts/check_repo_sync.py --remote safe_mirror --branch main`

## Repo-Visible Truth Rule

- local-only artifacts are non-existent for completion
- uncommitted files are non-existent for completion
- unpushed commits are non-existent for completion
- stale reports cannot replace current sync evidence

## Governance Linkage

This policy is interpreted together with:

- `docs/governance/FIRST_PRINCIPLES.md`
- `docs/governance/GOVERNANCE_HIERARCHY.md`
- `docs/governance/SELF_VERIFICATION_POLICY.md`
- `docs/governance/ADMISSION_GATE_POLICY.md`

## Legacy Note

- `origin` (`WorkFLOW`) is legacy/non-canonical for completion gate decisions.