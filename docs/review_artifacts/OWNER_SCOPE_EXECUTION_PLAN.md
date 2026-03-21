# OWNER_SCOPE_EXECUTION_PLAN

## Input Surfaces Re-read
- `docs/review_artifacts/OWNER_DECISION_SCOPE_CLOSURE_MATRIX.md`
- `docs/review_artifacts/DIRTY_TREE_GROUND_TRUTH_INVENTORY.md`
- `docs/review_artifacts/REMAINING_MANUAL_BLOCKERS_FOR_ALL_GREEN.md`
- `docs/review_artifacts/TRACKED_STATUS_SURFACES_FORENSIC_AUDIT.md`
- `docs/review_artifacts/STATUS_SURFACES_REMEDIATION_IMPLEMENTATION_REPORT.md`

## Execution Policy (current step)
- [OBSERVED] Rank/mode, env hygiene, and status-surface remediation are out of scope for edits except consistency use.
- [OBSERVED] Status-surface paradox already closed; target now is residual owner dirty scope.

## Exact Groups To Commit
- [OBSERVED] `KEEP_FOR_CURRENT_PHASE` tracked canonical surfaces:
  - root canonical docs (`README.md`, `MACHINE_CONTEXT.md`, `REPO_MAP.md`)
  - tracked governance docs in `docs/governance/*` (except owner-manual-only cluster not in this folder)
  - tracked review artifacts explicitly marked keep/commit
  - tracked scripts (`scripts/detect_machine_mode.py`, `scripts/repo_control_center.py`, validators)
  - tracked workspace contracts (`workspace_config/*.json` modified set)
- [OBSERVED] `KEEP_FOR_CURRENT_PHASE` untracked source surfaces:
  - `docs/governance/*.md` new doctrine files
  - `scripts/*.py` new helper scripts
  - `workspace_config/*.json` new contracts/manifests
- [OBSERVED] Keep-and-commit review surfaces for this closure cycle:
  - `TRACKED_STATUS_SURFACES_FORENSIC_AUDIT.*`
  - `STATUS_SURFACES_POLICY_DECISION_PAPER.md`
  - `STATUS_SURFACES_REMEDIATION_IMPLEMENTATION_REPORT.md`
  - `OWNER_DECISION_SCOPE_CLOSURE_MATRIX.md`
  - `TARGETED_CLEANUP_AND_RECHECK_REPORT.md`
  - `ALL_GREEN_RECHECK_AFTER_STATUS_POLICY.md`
  - `EXACT_RESIDUAL_ALL_GREEN_PARADOX_REPORT.md`
  - `DIRTY_TREE_GROUND_TRUTH_INVENTORY.*`
  - `OWNER_DECISION_MATRIX_FOR_ALL_GREEN.md`
  - `REMAINING_MANUAL_BLOCKERS_FOR_ALL_GREEN.md`
  - `OWNER_SCOPE_EXECUTION_PLAN.md`

## Exact Groups To Archive/Move
- [OBSERVED] `ARCHIVE_AS_EVIDENCE` untracked review artifact bulk (`docs/review_artifacts/*.md|*.json`) not in keep-and-commit allowlist.
- [OBSERVED] Archive destination (outside repo): `E:\CVVCODEX_OWNER_ARCHIVE\owner_scope_cleanup_<timestamp>\docs_review_artifacts\`

## Exact Groups To Discard
- [OBSERVED] None in this step (to avoid false deletion of potentially load-bearing evidence).

## Exact Groups To Ignore/Reclassify
- [OBSERVED] No ignore-policy mutation executed in this step.
- [OBSERVED] No reclassification beyond already-applied status-surface write policy.

## Exact Groups Still Owner-Manual-Only
- [OBSERVED] `integration/review_queue/20260317T094958Z_TASK-PLATFORM_TEST_AGENT-001_helper-node-audit/review_result.json`
- [OBSERVED] `integration/review_queue/20260317T094958Z_TASK-PLATFORM_TEST_AGENT-001_helper-node-audit/review_result.md`
- [OBSERVED] Reason: matrix explicitly marked this cluster as owner decision (commit/archive/revert ambiguous without owner intent).

## What Codex Executes Now
1. Archive untracked review-artifact bulk outside repo (allowlist-preserving).
2. Stage commit groups.
3. Exclude owner-manual-only integration cluster from staging.
4. Commit closure package.
5. Produce post-clean snapshot and residual exact blocker report.

## What Codex Will Not Touch
- [OBSERVED] No changes to rank/mode model logic.
- [OBSERVED] No changes to env hygiene model.
- [OBSERVED] No changes to status-surface remediation semantics.
- [OBSERVED] No autonomous decision on owner-manual-only integration review_result files.
