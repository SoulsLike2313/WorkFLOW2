# CONSTITUTION_OPERATOR_RESPONSE_GUIDE_V1

## Scope
Operational response guide for common constitutional outcomes in Constitution V1 gate calibration.

## Response Playbook
### 1) Contradiction warning
- Run: `python scripts/validation/scan_canonical_contradictions.py`
- Action: classify warning source, add correction note, schedule immediate doc alignment.
- Completion/certification: do not claim until warning is reviewed and justified.

### 2) Contradiction fail
- Run: `python scripts/validation/scan_canonical_contradictions.py`
- Action: stop protected claims, resolve conflicting canonical surfaces, rerun scan.
- Completion/certification/phase transition: blocked.

### 3) Drift warning
- Run: `python scripts/validation/check_registry_doc_drift.py`
- Action: record drift debt, align docs/registry references, rerun drift guard.
- Completion: allowed only with explicit debt note; certification should wait for cleanup.

### 4) Stale repo-control snapshot
- Run:
  - `python scripts/repo_control_center.py bundle`
  - `python scripts/repo_control_center.py full-check`
  - `python scripts/validation/run_constitution_checks.py`
- Action: refresh runtime truth before protected claims.
- Completion/certification: blocked while stale.

### 5) Partial constitution verdict
- Run: `python scripts/validation/run_constitution_checks.py`
- Action: resolve all `SOFT_FAIL` items and unknown-critical dependencies.
- Protected claims: blocked until upgraded to `PASS`.

### 6) Fail before completion
- Action: treat as hard blocker.
- Required: fix blocker source, rerun full constitutional check chain, then reassess.

### 7) Fail before certification
- Action: same as completion fail, plus verify drift/contradiction closure evidence.
- Required: rerun repo-control and constitutional checks before next certification attempt.

### 8) Fail before mirror refresh
- Action: stop mirror refresh when `HARD_FAIL`.
- If only `SOFT_FAIL`: mirror refresh is review-required and must include explicit note.

## Canonical Minimal Sequence
1. `python scripts/repo_control_center.py bundle`
2. `python scripts/repo_control_center.py full-check`
3. `python scripts/validation/run_constitution_checks.py`
