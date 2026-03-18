# CONSTITUTION_V1_STABILIZATION_CRITERIA

## Scope
Admission-grade criteria for declaring Constitution V1 stabilized, using lightweight enforceable checks.

## Criteria Matrix
| criterion | evidence | pass condition | current status |
|---|---|---|---|
| canonical vocabulary frozen and referenced | `docs/governance/WORKFLOW2_CANONICAL_VOCABULARY_V1.md`, manifest anchors | vocabulary doc exists and is referenced in canonical manifests | PASS |
| truth-state schema active | `workspace_config/schemas/truth_state_schema.json`, `docs/governance/TRUTH_STATE_MODEL_V1.md` | schema exists and contains canonical truth-state enum | PASS |
| contradiction scan operational | `scripts/validation/scan_canonical_contradictions.py`, runtime contradiction report | script exits cleanly and emits machine-readable verdict | PASS |
| registry-doc drift guard operational | `scripts/validation/check_registry_doc_drift.py`, runtime drift report | script exits cleanly and emits machine-readable verdict | PASS |
| proof-output naming policy fixed | `docs/governance/PROOF_OUTPUT_NAMING_POLICY_V1.md` | policy exists and is referenced by admission discipline | PASS |
| hygiene checklist active | `docs/governance/CONSTITUTION_PHASE_HYGIENE_CHECKLIST_V1.md` | checklist exists and is used before completion/certification | PASS |
| current/next/canonical surfaces aligned | contradiction scan output | no FAIL contradiction class in canonical surfaces | PASS |
| no unresolved critical contradiction | contradiction scan output + governance full-check | contradiction scan verdict != FAIL | PASS |
| no fake completion path | admission flow + governance gates + trust/sync checks | completion requires trust/sync/governance acceptance + constitution checks | PASS |
| stable admission-grade integration of lightweight checks | `docs/governance/CONSTITUTIONAL_ADMISSION_FLOW_V1.md`, `scripts/validation/run_constitution_checks.py`, constitution status artifacts | checks are documented, repeatable, and produce consolidated constitutional status surface | PARTIAL (invocation-driven, not hard-wired gate) |

## Interpretation
- A criterion is `PASS` only when evidence is repo-visible and executable where applicable.
- Criteria can stay `PARTIAL` if evidence is manual/doctrine-only.
- Constitution V1 stabilization is satisfied when no criterion is `FAIL` and no unresolved critical contradiction exists.
