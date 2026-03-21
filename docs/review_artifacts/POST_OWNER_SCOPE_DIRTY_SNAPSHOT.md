# POST_OWNER_SCOPE_DIRTY_SNAPSHOT

- [OBSERVED] branch: `main`
- [OBSERVED] divergence vs `safe_mirror/main`: `ahead 1, behind 0`
- [OBSERVED] tracked dirty count: `2`
- [OBSERVED] untracked count: `0`
- [OBSERVED] total dirty count: `2`

## Exact Residual Groups

### `owner_manual_integration_review_result_pair`
- [OBSERVED] paths:
  - `integration/review_queue/20260317T094958Z_TASK-PLATFORM_TEST_AGENT-001_helper-node-audit/review_result.json`
  - `integration/review_queue/20260317T094958Z_TASK-PLATFORM_TEST_AGENT-001_helper-node-audit/review_result.md`
- [OBSERVED] still blocks all-green: `yes`
- [OBSERVED] blocker mechanism: tracked dirty -> `worktree_clean=false`
- [OBSERVED] owner-only reason: commit/archive/revert intent is not inferable safely by Codex from current policy matrix.

## Residual Scope Verdict
- [OBSERVED] residual scope is zero: `no`
