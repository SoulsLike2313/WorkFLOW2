# GOVERNANCE ACCEPTANCE GATE

Policy class: transition gate for governance foundation closure.

## 1) Purpose

This gate decides whether governance foundation is accepted for moving to the next stage.

Moving to optimization or new architecture branch is forbidden until this gate is `PASS`.

## 2) Required PASS conditions

All conditions must be true:

1. `git` sync discipline is clean:
   - `HEAD == safe_mirror/main`
   - divergence `0/0`
   - clean worktree
2. Repo Control Center verdict chain:
   - trust = `TRUSTED`
   - sync = `IN_SYNC`
   - governance = `COMPLIANT`
   - bootstrap enforcement = `PASS`
   - mirror evidence = `PASS`
   - bundle readiness = `READY`
3. No unresolved critical contradiction.
4. `docs/NEXT_CANONICAL_STEP.md` routes to governance acceptance closure.
5. Governance acceptance verdict is repo-visible in runtime RCC reports.

## 3) Blocking conditions

Any one condition blocks acceptance:

1. dirty worktree or non-zero divergence
2. stale or blocked safe mirror evidence
3. bootstrap contract failure/warning
4. unresolved critical contradiction
5. hidden blocker in trust/admission chain
6. stale non-canonical next-step routing

## 4) Declaration authority

Gate may be declared `PASS` only by evidence-backed run:

1. `python scripts/repo_control_center.py full-check`
2. `python scripts/check_repo_sync.py --remote safe_mirror --branch main`

Narrative claims without command evidence are invalid.

## 5) Mandatory prohibition

Until gate is `PASS`:

1. next-stage transition is forbidden
2. completion for transition tasks is forbidden
3. evolution promotion claims beyond current maturity are forbidden

## 6) Evidence artifacts

Required repo-visible evidence:

1. `runtime/repo_control_center/repo_control_status.json`
2. `runtime/repo_control_center/repo_control_report.md`
3. `runtime/repo_control_center/evolution_status.json`
4. `runtime/repo_control_center/evolution_report.md`
5. sync check output from `scripts/check_repo_sync.py`
