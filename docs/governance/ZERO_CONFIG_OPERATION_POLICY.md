# ZERO CONFIG OPERATION POLICY

Policy class: operational readiness contract for new machine startup.

## 1) Objective

A new machine must reach trusted execution state from repository artifacts and standard tooling, without hidden human-only setup logic.

## 2) Required baseline

Mandatory local baseline:

1. repository cloned to `E:\CVVCODEX` (or equivalent path resolved by policy updates)
2. Python available for `scripts/*.py`
3. Git available with configured remotes
4. required policy/docs/manifests present and readable

## 3) Zero-config gate checks

Minimum pass set:

1. `python scripts/validate_workspace.py`
2. `python scripts/check_repo_sync.py --remote safe_mirror --branch main`
3. `python scripts/repo_control_center.py status`
4. `python scripts/repo_control_center.py trust`
5. `python scripts/repo_control_center.py full-check`

If any check fails, state is not zero-config ready.

## 4) Hidden dependency prohibition

Forbidden hidden dependencies:

1. oral-only setup steps not described in repo docs
2. implicit remote naming assumptions without documented fallback
3. completion claims requiring undocumented local machine state
4. “works on my machine” acceptance without reproducible command path

## 5) Required fallback disclosure

If automatic zero-config startup is blocked, response must include:

1. exact blocker
2. exact one-step or minimal-step recovery command sequence
3. verification command to confirm recovery

## 6) Completion prohibition

Completion is forbidden when:

1. zero-config gate checks are not executed
2. hidden setup dependency remains unresolved
3. repository state cannot be trusted by new machine without extra oral context
