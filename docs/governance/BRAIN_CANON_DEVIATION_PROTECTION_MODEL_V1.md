# BRAIN_CANON_DEVIATION_PROTECTION_MODEL_V1

Status:
- model_version: `v1`
- scope: `protection against canonical deviation for Reference Brain V1`
- mode: `fail_closed`

## 1) Purpose

Define the enforced protection layers that prevent silent drift, false authority claims, and rule bypass in WorkFLOW2 governing core.

## 2) Protection Layers

### Layer 1 - Source Precedence
1. stronger canonical sources outrank lower/secondary narrative surfaces.
2. contradiction resolution must follow precedence before any completion claim.

Anchors:
1. `docs/governance/CANONICAL_SOURCE_PRECEDENCE.md`
2. `docs/governance/CONTRADICTION_CONTROL_POLICY.md`

### Layer 2 - Constitutional Mutation Restriction
1. constitutional mutation is Emperor-only.
2. commentary/proposal/candidate are non-binding without sovereign mutation decision.

Anchors:
1. `docs/governance/CONSTITUTION_CHANGE_AUTHORITY_POLICY.md`
2. `docs/governance/CONSTITUTION_AMENDMENT_FLOW.md`
3. `docs/governance/CONSTITUTION_IMMUTABILITY_BOUNDARY.md`

### Layer 3 - Rank and Authority Boundaries
1. creator authority does not equal Emperor sovereignty.
2. rank elevation requires local proof contract checks.
3. mirror/import/portable context cannot elevate sovereign rank.

Anchors:
1. `docs/governance/NODE_AUTHORITY_RANK_POLICY_V1.md`
2. `docs/governance/SOVEREIGN_RANK_PROOF_MODEL_V1.md`
3. `workspace_config/emperor_local_proof_contract.json`
4. `scripts/validation/detect_node_rank.py`

### Layer 4 - Claim Denial Guard
1. unauthorized sovereign claims are denied fail-closed.
2. signature/issuer assurance constraints gate claim allowance.

Anchors:
1. `docs/governance/SOVEREIGN_CLAIM_DENIAL_POLICY_V1.md`
2. `scripts/validation/check_sovereign_claim_denial.py`

### Layer 5 - Document-Class Separation Guard
1. Genome/Gramota/Assignment-binding semantics are separated.
2. status/will/binding conflicts obey strict priority rules.

Anchors:
1. `docs/governance/GENOME_DOCTRINE_V1.md`
2. `docs/governance/GRAMOTA_DOCTRINE_V1.md`
3. `docs/governance/ASSIGNMENT_BINDING_DOCTRINE_V1.md`
4. `workspace_config/genome_gramota_assignment_binding_contract.json`

### Layer 6 - Validation and Gate Discipline
1. sync/trust/governance/admission chain controls closure claims.
2. contradiction and drift scans are explicit pre-claim checks.

Anchors:
1. `scripts/repo_control_center.py`
2. `scripts/validation/run_constitution_checks.py`
3. `scripts/validation/scan_canonical_contradictions.py`
4. `scripts/validation/check_registry_doc_drift.py`

### Layer 7 - Runtime Freshness Control
1. runtime truth surfaces are evidence, not law.
2. stale snapshots must downgrade confidence and block overclaim.

Anchors:
1. `runtime/repo_control_center/repo_control_status.json`
2. `runtime/repo_control_center/constitution_status.json`
3. `docs/governance/CONSTITUTION_PHASE_HYGIENE_CHECKLIST_V1.md`

### Layer 8 - Output Discipline and Safe Transfer
1. large-task details must be bundle-backed.
2. safe-mode exclusions must be explicit.
3. manual safe fallback is canonical when default exporter is insufficient.

Anchors:
1. `docs/governance/CODEX_OUTPUT_DISCIPLINE_V1.md`
2. `docs/governance/MANUAL_SAFE_BUNDLE_STANDARD.md`
3. `workspace_config/bundle_fallback_contract.json`
4. `scripts/export_manual_safe_bundle.py`

## 3) Mandatory Refusal Conditions

System must refuse overreach when:
1. rank/authority proof is missing for requested claim class;
2. claim class is outside rank allowance;
3. constitutional mutation is requested without Emperor-level authority;
4. contradiction/drift hard-fail exists unresolved;
5. stale/unknown critical runtime evidence blocks reliable verdict.

## 4) Federation Under Protection Boundary

1. Federation is an operational block under brain law.
2. current real department is `Analytics Department`.
3. non-department lines remain intake subjects unless formally promoted by doctrine+registry+authority path.
4. Federation cannot override sovereign/constitutional boundaries.

## 5) Current Protection Limits

Still partial:
1. named guardian identity binding not yet formalized.
2. full cross-validator taxonomy consumption not complete.
3. full runtime triad arbitration not complete.
4. stale secondary retirement not fully closed.

These limits must remain explicitly visible; they cannot be masked by narrative.
