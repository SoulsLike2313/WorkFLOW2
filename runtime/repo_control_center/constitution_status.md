# CONSTITUTION STATUS

- constitution_phase: `constitution-v1-finalized`
- constitution_version: `WORKFLOW2_CONSTITUTION_V1`
- vocabulary_freeze_status: `PASS`
- truth_state_schema_status: `PASS`
- contradiction_scan_status: `PASS`
- registry_doc_drift_status: `PASS`
- proof_output_naming_policy_status: `PASS`
- hygiene_checklist_status: `PASS`
- canonical_node_root_policy_status: `PASS`
- sovereign_rank_proof_model_status: `PASS`
- sovereign_claim_denial_policy_status: `PASS`
- inter_node_document_architecture_status: `PASS`
- inter_node_document_schema_status: `PASS`
- node_rank_detection_status: `PASS`
- detected_node_rank: `PRIMARCH`
- sovereign_proof_status: `MISSING_OR_INVALID`
- canonical_root_validity: `VALID`
- sovereign_claim_denial_status: `ALLOW`
- repo_control_status_freshness: `FRESH`
- sync_status: `IN_SYNC`
- trust_status: `WARNING`
- governance_acceptance: `FAIL`
- overall_verdict: `FAIL`
- last_checked_at: `2026-03-18T18:39:54.205006+00:00`

## Gate Actions
- completion_claim: `BLOCK`
- certification_claim: `BLOCK`
- mirror_refresh: `BLOCK`
- phase_transition: `BLOCK`

## Severity Counts
- INFO: `19`
- WARNING: `0`
- SOFT_FAIL: `1`
- HARD_FAIL: `1`

## Blockers
- governance_acceptance: FAIL

## Warnings
- trust_status: WARNING

## Unknown Critical Dependencies
- none

## Notes
- none

## Sources
- `docs/governance/WORKFLOW2_CONSTITUTION_V1.md`
- `docs/governance/WORKFLOW2_CONSTITUTION_V0.md`
- `docs/governance/WORKFLOW2_CANONICAL_VOCABULARY_V1.md`
- `docs/governance/TRUTH_STATE_MODEL_V1.md`
- `workspace_config/schemas/truth_state_schema.json`
- `docs/governance/PROOF_OUTPUT_NAMING_POLICY_V1.md`
- `docs/governance/CONSTITUTION_PHASE_HYGIENE_CHECKLIST_V1.md`
- `docs/governance/CANONICAL_NODE_ROOT_POLICY_V1.md`
- `docs/governance/SOVEREIGN_RANK_PROOF_MODEL_V1.md`
- `docs/governance/SOVEREIGN_CLAIM_DENIAL_POLICY_V1.md`
- `docs/governance/INTER_NODE_DOCUMENT_ARCHITECTURE_V1.md`
- `docs/governance/INTER_NODE_DOCUMENT_SCHEMA_V1.md`
- `scripts/validation/detect_node_rank.py`
- `scripts/validation/check_sovereign_claim_denial.py`
- `runtime/repo_control_center/validation/canonical_contradiction_scan.json`
- `runtime/repo_control_center/validation/registry_doc_drift_report.json`
- `runtime/repo_control_center/repo_control_status.json`
