# NODE_RANK_CHECK_CHAIN_INTEGRATION_REPORT

- generated_at_utc: `2026-03-18T13:56:00Z`
- scope: `integration of node-rank and sovereign-claim gates into constitutional check chain`

## 1) Integrated Components

Updated:
1. `scripts/validation/run_constitution_checks.py`
2. `docs/governance/CONSTITUTIONAL_ADMISSION_FLOW_V1.md`
3. `docs/governance/CONSTITUTION_GATE_SEVERITY_MODEL_V1.md`
4. `docs/governance/CONSTITUTION_OPERATOR_RESPONSE_GUIDE_V1.md`

Added validators:
1. `scripts/validation/detect_node_rank.py`
2. `scripts/validation/check_sovereign_claim_denial.py`

## 2) New Constitution Status Surfaces

`run_constitution_checks.py` now emits:

1. `node_rank_detection_status`
2. `detected_node_rank`
3. `sovereign_proof_status`
4. `sovereign_proof_present`
5. `primarch_authority_path_valid`
6. `canonical_root_validity`
7. `sovereign_claim_denial_status`
8. `sovereign_claim_denial_reason`
9. `sovereign_claim_denial_severity`

## 3) Fail-Closed Guarantees Added

1. unknown node-rank status is treated as degraded constitutional state;
2. invalid canonical root validity is hard-fail for sovereign confidence;
3. Emperor rank without sovereign proof is hard-fail;
4. sovereign-claim denial outcomes feed into constitutional severity.

## 4) Operator Guidance Hardened

Operator response guide now includes explicit handling for:

1. failed Emperor proof;
2. invalid Primarch path;
3. unauthorized sovereign claim;
4. unsigned/invalid inter-node document;
5. canonical root mismatch.

## 5) Current Runtime Observation

Current post-integration run produced:
1. rank detection active (`detected_node_rank=ASTARTES`, with fail-closed fallback because primarch authority env path is not set in this runtime);
2. root validity surfaced (`VALID`);
3. claim denial surface active (`ALLOW` for rank-appropriate non-sovereign claim inputs).

Overall constitutional verdict remained blocked by existing sync/trust/governance gates (`DRIFTED/NOT_TRUSTED/FAIL`) from current working state, not by integration failure.

## 6) Integration Status

`PARTIAL`

Rationale:
1. rank/claim/root checks are now in constitutional chain;
2. full end-state depends on broader repo sync/trust green state and future signature hardening.
