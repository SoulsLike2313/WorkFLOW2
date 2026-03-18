# CONSTITUTIONAL_ADMISSION_FLOW_V1

## Purpose
Lightweight admission/completion integration path for constitutional checks without introducing a new orchestration layer.

## Checks In Scope
- `python scripts/validation/scan_canonical_contradictions.py`
- `python scripts/validation/check_registry_doc_drift.py`
- `python scripts/validation/run_constitution_checks.py`

## Recommended Invocation Order
1. Refresh core operational state:
- `python scripts/repo_control_center.py bundle`
- `python scripts/repo_control_center.py full-check`

2. Execute constitutional validation chain:
- `python scripts/validation/scan_canonical_contradictions.py`
- `python scripts/validation/check_registry_doc_drift.py`

3. Aggregate constitution status surface:
- `python scripts/validation/run_constitution_checks.py`

4. Optional single-command path:
- `python scripts/validation/run_constitution_checks.py --run-repo-control`

## Discipline Points
Run constitutional checks:
- before completion claim;
- before certification;
- before safe-mirror evidence refresh;
- before canonical phase transition claim.

## Verdict Handling
- `scan_canonical_contradictions.py`:
  - `FAIL`: completion/certification blocked.
  - `WARNING`: completion allowed only with explicit note and no unresolved critical contradictions.
  - `PASS`: no contradiction blocker.

- `check_registry_doc_drift.py`:
  - `FAIL`: completion/certification blocked.
  - `WARNING`: admission allowed with declared drift debt and next action.
  - `PASS`: no registry-doc drift blocker.

- `run_constitution_checks.py` overall:
  - `BLOCKED`: completion/certification blocked.
  - `PARTIAL`: admission allowed only with explicit debt declaration.
  - `PASS`: admission-grade constitutional health satisfied.

## Artifacts Produced
- `runtime/repo_control_center/validation/canonical_contradiction_scan.json`
- `runtime/repo_control_center/validation/registry_doc_drift_report.json`
- `runtime/repo_control_center/constitution_status.json`
- `runtime/repo_control_center/constitution_status.md`

## Non-Goals
- No replacement of existing governance engine.
- No heavy admission framework.
- No automatic policy mutation.
