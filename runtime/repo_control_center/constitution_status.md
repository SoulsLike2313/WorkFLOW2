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
- emperor_local_proof_contract_status: `PASS`
- shared_taxonomy_contract_status: `PASS`
- claim_denial_probe_claim_class: `denial_as_expected_claim`
- node_rank_detection_status: `PASS`
- detected_node_rank: `EMPEROR`
- sovereign_proof_status: `VALID`
- canonical_root_validity: `VALID`
- sovereign_claim_denial_status: `ALLOW`
- repo_control_status_freshness: `FRESH`
- sync_status: `IN_SYNC_CLASSIFIED`
- trust_status: `TRUSTED`
- governance_acceptance: `PASS`
- overall_verdict: `PASS`
- last_checked_at: `2026-03-28T00:05:13.964896+00:00`

## Gate Actions
- completion_claim: `ALLOW`
- certification_claim: `ALLOW`
- mirror_refresh: `ALLOW`
- phase_transition: `ALLOW`

## Severity Counts
- INFO: `23`
- WARNING: `0`
- SOFT_FAIL: `0`
- HARD_FAIL: `0`

## Blockers
- none

## Warnings
- none

## Unknown Critical Dependencies
- none

## Notes
- primarch_authority_path_valid is kept as compatibility alias; status model v2 uses primarch_genome_bundle_valid as load-bearing indicator

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
- `workspace_config/emperor_local_proof_contract.json`
- `workspace_config/shared_taxonomy_contract.json`
- `scripts/validation/detect_node_rank.py`
- `scripts/validation/check_sovereign_claim_denial.py`
- `runtime/repo_control_center/validation/canonical_contradiction_scan.json`
- `runtime/repo_control_center/validation/registry_doc_drift_report.json`
- `runtime/repo_control_center/repo_control_status.json`
