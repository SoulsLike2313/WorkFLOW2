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

## Hard Rule

No repo-visible result = no completion.

## Mandatory Status Mapping

- all gate checks pass => `COMPLETED`
- one or more gate checks fail => `NOT_COMPLETED`

## Evidence Contract

Final completion must include:

1. commit hash
2. branch
3. `HEAD` and `origin/main` comparison result
4. verified repo-visible paths
5. executed validation steps and run ids
