# ALL_GREEN_RECHECK_AFTER_STATUS_POLICY

## Gate Snapshot (fresh run after status-policy remediation)
- [OBSERVED] `worktree_clean = false`
- [OBSERVED] `sync = DRIFTED`
- [OBSERVED] `trust = NOT_TRUSTED`
- [OBSERVED] `governance_acceptance = FAIL`
- [OBSERVED] `admission = REJECTED`
- [OBSERVED] `constitution overall = FAIL`

## Status-Surface Paradox Check
- [OBSERVED] Tracked status/evidence target files remain clean after chain-run.
- [OBSERVED] `run_constitution_checks.py` reports `status_surface_write_mode = no_write_default`.
- [OBSERVED] Explicit `--write-surfaces` still works and intentionally creates tracked changes (then reversible by restore).

## Interpretation
- [OBSERVED] Status-surface paradox is closed.
- [INFERRED] Remaining red contour is now attributable to unresolved owner dirty scope, not automatic tracked-status rewrites.

## Verdict
- [OBSERVED] all-green after status policy: **NOT REACHED**.
- [OBSERVED] reason: non-target residual dirty/untracked package still blocks `worktree_clean`, cascading into sync/trust/governance/admission failure chain.
