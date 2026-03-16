# Completion Gate Rules

## Gate Definition

A task is complete only when all conditions below are `PASS`.

1. outputs are created
2. outputs are validated
3. outputs are committed
4. outputs are pushed
5. outputs are readable by repo-relative paths in GitHub
6. acceptance criteria are confirmed
7. validation steps are executed
8. post-task git finalization sequence is completed (`git add` -> `git commit` -> `git push`)

## Hard Rule

No repo-visible result = no completion.

No post-task git add/commit/push = no completion.

## Mandatory Status Mapping

- all gate checks pass => `COMPLETED`
- one or more gate checks fail => `NOT_COMPLETED`

## Evidence Contract

Final completion must include:

1. commit hash
2. branch
3. `HEAD` and `safe_mirror/main` comparison result
4. verified repo-visible paths
5. executed validation steps and run ids
6. proof of post-task git finalization:
   - `git add` performed on task scope
   - `git commit` created
   - `git push` completed to `safe_mirror`

## Mandatory Finalization Order

Order is strict and cannot be skipped:

1. `git add`
2. `git commit`
3. `git push`
4. sync verification (`HEAD == safe_mirror/<branch>`, clean worktree)

Any order violation => `NOT_COMPLETED`.
