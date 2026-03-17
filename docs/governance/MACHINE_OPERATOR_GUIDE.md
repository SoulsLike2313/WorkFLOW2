# MACHINE_OPERATOR_GUIDE

## Scope
Engineering operator guide for WorkFLOW2 governance/control runtime.
This document defines operating semantics, not product features.

## System Role
- Control plane for repo truth, policy compliance, and admission gating.
- Canonical source: local `E:\CVVCODEX`.
- Public safe mirror: `safe_mirror/main` (`WorkFLOW2`) only.

## Machine Modes
- `creator`: creator authority detected; canonical acceptance operations allowed.
- `helper`: creator authority absent; block execution only; no canonical acceptance.
- `integration`: canonical review path for external handoff packages.

## Authority Contract
- Detection input: `CVVCODEX_CREATOR_AUTHORITY_DIR` + `creator_authority.json` marker.
- Authority state is external to tracked repo.
- Full repo copy without valid marker resolves to `helper` mode.

## Gate Chain
Execution order for decision quality:
1. `sync` (`IN_SYNC` required for canonical completion)
2. `trust` (`TRUSTED` required for clean admission)
3. `governance` (`COMPLIANT` required)
4. `governance_acceptance` (`PASS` required)
5. `admission` (`ADMISSIBLE` required)
6. `evolution` (progression signal; not a replacement for admission)

## Verdict Semantics
- `PASS` / `TRUSTED` / `IN_SYNC` / `ADMISSIBLE`: gate condition satisfied.
- `WARNING`: condition is operational but contains non-fatal risk.
- `BLOCKED`: gate cannot proceed due to hard blocker.
- `REJECTED`: admission gate denied.

## Health Model
- `workspace_health`: technical integrity of current workspace checks.
- `authority_status`: current role authority state (creator/helper/integration).
- `governance_status`: governance compliance + acceptance state.
- `admission_status`: admission gate state.
- `repo_health`: summary health derived from workspace control checks.

## Operator Runbook
1. `python scripts/repo_control_center.py bundle`
2. `python scripts/repo_control_center.py full-check`
3. Review:
   - `runtime/repo_control_center/one_screen_status.json`
   - `runtime/repo_control_center/plain_status.md`
4. If blocked, route by:
   - `blocking_reason_category`
   - `blocking_reason_detail`
5. Proceed only when target gate set is satisfied for intended operation.

## Non-Overridable Constraints
- No canonical completion in `helper` mode.
- No completion with sync drift or dirty worktree.
- No completion with unresolved critical contradictions.
- No bypass of governance acceptance gate.
