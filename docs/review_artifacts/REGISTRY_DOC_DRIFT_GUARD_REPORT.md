# REGISTRY_DOC_DRIFT_GUARD_REPORT

## Scope
Initial low-risk drift guard status for:
- `scripts/validation/check_registry_doc_drift.py`

## What Is Checked Now
1. Registry <-> registry-doc alignment
- `workspace_config/operator_mission_registry.json` vs `docs/governance/OPERATOR_MISSION_REGISTRY.md`
- checks mission classes and mission ids presence.

2. Manifest anchor alignment
- `workspace_config/workspace_manifest.json`
- `workspace_config/codex_manifest.json`
- checks required anchors:
  - constitution path
  - canonical vocabulary path
  - truth-state model path
  - truth-state schema path

3. Mission id example validity
- scans high-value docs for `mission.*` identifiers
- verifies referenced ids exist in mission registry.

## Current Result Snapshot
- verdict: `PASS`
- fails: `0`
- warnings: `0`
- output artifact:
  - `runtime/repo_control_center/validation/registry_doc_drift_report.json`

## Not Covered Yet
- deep semantic markdown interpretation
- full-repo mission-id scan (intentionally bounded to high-value canonical docs)
- non-mission registry families beyond current mission-focused scope

## High-Value Drift Zones
1. mission example ids in `README` and certification artifacts
2. registry summary markdown drift during manual edits
3. manifest anchors after constitutional docs/schema updates

## Expected Operational Benefit
- faster detection of stale mission references
- lower risk of narrative/registry desync
- early warning before completion/certification claims

