# GitHub Sync Policy

## Privacy Boundary

Repository workflow is public-audit-safe.

Forbidden in tracked state:

1. public mirror workflows
2. tunnel/public endpoint scripts and credentials
3. router/WAN/LAN exposure diagnostics
4. local publication runtime logs

GitHub visibility is public for audit readability. Public mirror/tunnel publication flows remain non-canonical.

ChatGPT reading is request-scoped via targeted local bundle export:

- `python scripts/export_chatgpt_bundle.py <mode> ...`

Full repository exposure is not required for ChatGPT task execution.

## Mandatory Rule

No task is complete unless the result is visible in GitHub on `origin/main`.

Local preparation rule:

1. all sanitation and publication-safe validation are executed in local root (`E:\CVVCODEX`)
2. only approved safe state is synchronized to GitHub
3. safe mirror state proof is required (`workspace_config/SAFE_MIRROR_MANIFEST.json`)

## Mandatory Post-Task Git Finalization

After every completed task, this exact sequence is mandatory:

1. `git add <allowed_task_paths>`
2. `git commit -m "<task-scoped message>"`
3. `git push origin <active_branch>`

If sequence is not completed, task status is `NOT_COMPLETED`.

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

Mandatory proof:

5. commit for current task exists in branch history.
6. pushed commit is visible on `origin/<active_branch>`.

## Required Verification Commands

1. `git rev-parse HEAD`
2. `git rev-parse origin/main`
3. `git status -sb`
4. `git ls-tree --name-only -r origin/main`
5. `git log --oneline -n 1`
6. `git rev-list --left-right --count origin/<active_branch>...HEAD`

## Enforcement

- no GitHub-visible output => no completion
- no push confirmation => no completion
- no repo-visible path verification => no completion
- no post-task `git add` => no completion
- no post-task `git commit` => no completion
- no post-task `git push` => no completion
