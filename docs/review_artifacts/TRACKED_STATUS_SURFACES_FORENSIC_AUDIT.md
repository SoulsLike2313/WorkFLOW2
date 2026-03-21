# TRACKED_STATUS_SURFACES_FORENSIC_AUDIT

## Scope
- [OBSERVED] Target: tracked status/evidence surfaces that can be rewritten by verification/evidence scripts and can re-dirty the worktree.
- [OBSERVED] Inspected chain:  
  - `python scripts/check_repo_sync.py --remote safe_mirror --branch main`  
  - `python scripts/repo_control_center.py status`  
  - `python scripts/repo_control_center.py full-check`  
  - `python scripts/validation/run_constitution_checks.py`

## Forensic Results (per surface)

### 1) `runtime/repo_control_center/constitution_status.json`
- [OBSERVED] Writer: `scripts/validation/run_constitution_checks.py`
- [OBSERVED] Rewrite trigger now: explicit `--write-surfaces` only.
- [OBSERVED] Tracked: yes.
- [OBSERVED] Deterministic rewrite: no (`last_checked_at` and command snapshots vary).
- [OBSERVED] Blocks `worktree_clean` when rewritten and not committed: yes.
- [OBSERVED] Intended role: canonical persisted constitution evidence snapshot.
- [INFERRED] Better classification: tracked snapshot with explicit write gate (not per-run runtime churn).
- [OBSERVED] Self-dirty paradox status: mitigated by default no-write behavior.

### 2) `runtime/repo_control_center/constitution_status.md`
- [OBSERVED] Writer: `scripts/validation/run_constitution_checks.py`
- [OBSERVED] Rewrite trigger now: explicit `--write-surfaces` only.
- [OBSERVED] Tracked: yes.
- [OBSERVED] Deterministic rewrite: no (timestamp-bearing payload source).
- [OBSERVED] Blocks `worktree_clean` when rewritten and not committed: yes.
- [OBSERVED] Intended role: human-readable constitutional evidence snapshot.
- [INFERRED] Better classification: tracked snapshot with explicit write gate.
- [OBSERVED] Self-dirty paradox status: mitigated by default no-write behavior.

### 3) `workspace_config/SAFE_MIRROR_MANIFEST.json`
- [OBSERVED] Writer: `scripts/build_safe_mirror_manifest.py`
- [OBSERVED] Rewrite trigger: explicit mirror evidence refresh invocation.
- [OBSERVED] Tracked: yes.
- [OBSERVED] Deterministic rewrite: no (`evidence_generated_at` is time-based).
- [OBSERVED] Blocks `worktree_clean` when refreshed and not committed: yes.
- [OBSERVED] Intended role: canonical tracked mirror-evidence contract.
- [INFERRED] Better classification: tracked evidence (refresh-by-intent, not per verification loop).
- [OBSERVED] Self-dirty paradox in default verification chain: no (not rewritten by the chain above).

### 4) `docs/review_artifacts/SAFE_MIRROR_BUILD_REPORT.md`
- [OBSERVED] Writer: `scripts/build_safe_mirror_manifest.py`
- [OBSERVED] Rewrite trigger: explicit mirror evidence refresh invocation.
- [OBSERVED] Tracked: yes.
- [OBSERVED] Deterministic rewrite: no (`evidence_generated_at` included).
- [OBSERVED] Blocks `worktree_clean` when refreshed and not committed: yes.
- [OBSERVED] Intended role: tracked human-readable mirror evidence companion.
- [INFERRED] Better classification: tracked evidence (refresh-by-intent).
- [OBSERVED] Self-dirty paradox in default verification chain: no.

## Reproduction Evidence

### A) No-write chain does not dirty tracked status surfaces
- [OBSERVED] Procedure:
  1. `git restore` all four tracked status/evidence surfaces.
  2. Run verification chain (`check_repo_sync`, `repo_control_center status`, `repo_control_center full-check`, `run_constitution_checks` default).
  3. `git diff --name-only -- <four paths>`
- [OBSERVED] Result: empty diff for all four surfaces.

### B) Explicit write still dirties constitution surfaces (by design)
- [OBSERVED] Procedure:
  1. `git restore runtime/repo_control_center/constitution_status.*`
  2. run `python scripts/validation/run_constitution_checks.py --write-surfaces`
  3. inspect diff on two constitution files
- [OBSERVED] Result: both constitution tracked files become modified.
- [OBSERVED] Final cleanup in this cycle: files restored to keep targeted surfaces clean.

## Conclusion
- [OBSERVED] The self-dirtying paradox caused by default constitution status rewriting is closed.
- [OBSERVED] Remaining all-green failure is no longer caused by these tracked status surfaces.
- [INFERRED] Remaining red state is now dominated by large owner decision dirty scope outside this targeted status-surface set.
