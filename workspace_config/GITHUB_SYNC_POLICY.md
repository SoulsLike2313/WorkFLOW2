# GitHub Sync Policy

## Mandatory Rule

No task is complete unless the result is visible in GitHub on `origin/main`.

## Hard Requirements

1. A locally created file that is not committed and pushed is treated as non-existent.
2. A final report without repo-visible files is rejected.
3. Runtime-only artifacts are not accepted for review unless duplicated in a repo-visible review area.
4. If a required file path does not open in GitHub, completion status is `REJECTED`.

## Mandatory Pre-Report Sync Gate

Before any final completion claim, the agent must verify:

1. `HEAD` against `origin/main`.
2. push status for the active branch.
3. expected repo-visible paths.
4. completion summary path in repo-visible area.

## Required Verification Commands

1. `git rev-parse HEAD`
2. `git rev-parse origin/main`
3. `git status -sb`
4. `git ls-tree --name-only -r origin/main`

## Enforcement

- no GitHub-visible output => no completion
- no push confirmation => no completion
- no repo-visible path verification => no completion
