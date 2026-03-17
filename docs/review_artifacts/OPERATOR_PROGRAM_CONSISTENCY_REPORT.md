# OPERATOR_PROGRAM_CONSISTENCY_REPORT

## Scope
Deterministic routing and response-shape consistency for operator task/program execution layer.

## Coverage
- Registry source: `workspace_config/operator_program_registry.json`
- Golden pack: `docs/review_artifacts/OPERATOR_PROGRAM_GOLDEN_PACK.json`
- Routed classes: `safe_read_validate_report_program`, `operational_handoff_review_program`, `operational_task_routing_program`, `creator_guarded_program`

## Consistency Criteria
1. Same semantic request resolves to same `program_class`.
2. Same semantic request resolves to same `program_id`.
3. Routing precedence follows `creator_guarded > handoff_review > task_routing > safe_read`.
4. `--program-id` override is deterministic and highest priority.
5. Fallback is stable: `program.safe_status_validation_report.v1`.

## Expected Runtime Evidence
- `runtime/operator_program_layer/operator_program_consistency_check.json`
- `runtime/operator_program_layer/operator_program_registry_snapshot.json`

## Acceptance
- `consistency_verdict = PASS`
- `mismatch_count = 0`
- creator-grade chain remains green after consistency run
