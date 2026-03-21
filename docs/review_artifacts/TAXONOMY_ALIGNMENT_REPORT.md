# TAXONOMY_ALIGNMENT_REPORT

Status:
- report_version: `v1`
- scope: `policy-doc and machine-enforced taxonomy alignment`
- execution_mode: `bounded hardening`

## 1) Load-Bearing Sources

Policy anchors:
1. `docs/governance/NODE_AUTHORITY_RANK_POLICY_V1.md`
2. `docs/governance/SOVEREIGN_CLAIM_DENIAL_POLICY_V1.md`
3. `docs/governance/SOVEREIGN_RANK_PROOF_MODEL_V1.md`
4. `docs/governance/FEDERATION_ARCHITECTURE.md`

Machine-enforced anchors:
1. `scripts/validation/detect_node_rank.py`
2. `scripts/validation/check_sovereign_claim_denial.py`
3. `workspace_config/federation_mode_contract.json`
4. `workspace_config/delegation_registry.json`
5. `workspace_config/claim_taxonomy_contract.json`

## 2) Drift Detection

| taxonomy area | policy wording | runtime/script wording (before) | drift status |
|---|---|---|---|
| sovereign claim classes | `canonical_acceptance_claim`, `sovereign_policy_change_claim`, `emperor_rank_claim`, `unrestricted_structural_mutation_claim` | `sovereign_acceptance_claim`, `sovereign_transition_claim`, `sovereign_rank_assertion` | `DRIFT_DETECTED` |
| primarch non-sovereign classes | `bounded_engineering_proposal`, `execution_report_claim`, `denial_as_expected_claim` | `primarch_reintegration_claim`, `bounded_acceptance_recommendation`, `denial_as_expected_claim` | `DRIFT_DETECTED` |
| astartes non-sovereign classes | `execution_report_claim`, `denial_as_expected_claim` | `bounded_review_claim`, `denial_as_expected_claim` | `DRIFT_DETECTED` |
| signature assurance names | `locally_verifiable`, `emperor_local_only_verifiable` (+ bounded structural minimum) | `structurally_bound`/`cryptographically_bound` only | `PARTIAL_DRIFT` |
| rank labels | `EMPEROR`, `PRIMARCH`, `ASTARTES` | `EMPEROR`, `PRIMARCH`, `ASTARTES` | `ALIGNED` |

## 3) Alignment Actions Applied

1. `scripts/validation/check_sovereign_claim_denial.py` now uses canonical claim classes as primary enforcement taxonomy.
2. Legacy claim names are retained as explicit compatibility aliases and are normalized before evaluation.
3. Signature assurance gates now align to policy tiers:
   - sovereign claim classes require at least `locally_verifiable`;
   - `bounded_engineering_proposal` requires at least `structurally_bound`;
   - `execution_report_claim` denies `unsigned`/`unknown` assurance.
4. Claim output now records both `claim_class_input` and `claim_class_normalized` for audit clarity.
5. `workspace_config/delegation_registry.json` codifies claim-class boundaries and legacy alias mapping for machine-readable reuse.
6. `workspace_config/claim_taxonomy_contract.json` defines shared claim/rank/alias/denial-reason vocabulary for cross-validator reuse.
7. `scripts/validation/detect_node_rank.py` consumes shared rank labels from `workspace_config/shared_taxonomy_contract.json`.

## 4) Current Alignment State

Strongly aligned now:
1. rank labels;
2. sovereign vs non-sovereign claim class names;
3. constitutional mutation claim is explicit (`constitutional_mutation_claim`) and Emperor-only;
4. basic signature assurance gate semantics;
5. federation command terminology split (sovereign vs operational vs delegated).

Still open:
1. taxonomy contract is not yet consumed by all validators directly (partial adoption);
2. no centralized schema-enforced validator for contract/document drift;
3. no department-specific claim override model beyond current single-department stage (intentionally out of scope).

## 5) Formalization Limits

Machine-readable formalized:
1. rank/authority/delegation baseline (`workspace_config/delegation_registry.json`);
2. department escalation baseline (`docs/governance/FEDERATION_DEPARTMENT_ESCALATION_MATRIX.md`);
3. canonical claim taxonomy in enforcement script with legacy normalization;
4. shared claim taxonomy contract (`workspace_config/claim_taxonomy_contract.json`);
5. unified cross-layer shared taxonomy contract (`workspace_config/shared_taxonomy_contract.json`).

Document-only formalized:
1. current single-department escalation semantics are governance-documented but not fully machine-validated per mission/program run.

Draft/inferred only:
1. permanent oversight ownership by named operator;
2. exception policy for sovereign-signoff shortcuts in any future multi-department expansion.

Intentionally open:
1. deep ownership empire model;
2. full hard-gated command architecture for every department edge-case.
