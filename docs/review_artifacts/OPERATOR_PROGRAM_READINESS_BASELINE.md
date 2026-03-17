# OPERATOR_PROGRAM_READINESS_BASELINE

## Baseline Intent
Task/Program Layer executes repeatable operator programs over accepted governance/query/command baselines.

## Required Components
- governance docs:
  - `docs/governance/OPERATOR_PROGRAM_EXECUTION_BASELINE.md`
  - `docs/governance/OPERATOR_PROGRAM_CATALOG.md`
  - `docs/governance/OPERATOR_PROGRAM_EXECUTION_CONTRACT.md`
  - `docs/governance/OPERATOR_PROGRAM_INTENT_ROUTING.md`
- registry + script:
  - `workspace_config/operator_program_registry.json`
  - `scripts/operator_program_surface.py`
- golden acceptance pack:
  - `docs/review_artifacts/OPERATOR_PROGRAM_GOLDEN_PACK.json`

## Runtime Artifacts
- `runtime/operator_program_layer/last_execution.json`
- `runtime/operator_program_layer/program_execution_log.jsonl`
- `runtime/operator_program_layer/program_surface_status.json`
- `runtime/operator_program_layer/program_surface_report.md`
- `runtime/operator_program_layer/operator_program_consistency_check.json`
- `runtime/operator_program_layer/operator_program_registry_snapshot.json`

## Hard Constraints
- No program bypasses authority checks.
- No program bypasses policy checks.
- Creator-guarded programs require creator authority.
- Mutation defaults to dry-run unless explicit `--allow-mutation` plus confirmation.
- Program execution must produce checkpoint and evidence-bearing contract output.
