# DEPARTMENT_BUNDLE_PROTOCOLS_V1

Status:
- protocol_version: `v1`
- scope: `bundle classes for federated production flow`
- mode: `evidence-first`

Assertion labels:
- `PROVEN`
- `REUSABLE`
- `DESIGNED`
- `NOT YET IMPLEMENTED`

## 1) Bundle classes (mandatory minimum)

1. Intake Bundle
2. Technical Map Bundle
3. Task Bundle
4. Astartes Result Bundle
5. Department Synthesis Bundle
6. Handoff Bundle
7. Blocker / Incident Bundle
8. Completion Bundle
9. Release Bundle

## 2) Protocol table

| Bundle type | Writer | Reader | Mandatory fields | Evidence requirements | Escalation rules | Close condition |
| --- | --- | --- | --- | --- | --- | --- |
| Intake Bundle | Analytics intake owner | Primarch + Analytics team | intake_id, source, goal, constraints, initial artifacts | source references + artifact inventory | missing minimum fields -> blocker queue | intake classified + accepted/rejected for analysis |
| Technical Map Bundle | Analytics | Primarch + downstream departments | architecture map, stack map, risk map, done/not-done map | inspected paths + rationale + uncertainty notes | critical unknowns -> blocker queue | map approved for routing |
| Task Bundle | Primarch | assigned Astartes | task_id, scope, allowed paths, forbidden actions, due, evidence checklist | explicit task boundary + expected validation outputs | out-of-scope request -> immediate return to Primarch | task accepted and bound |
| Astartes Result Bundle | Astartes | Primarch | task_id, changes, checks, unresolved blockers, confidence | command outputs/tests/logs + changed file list | blocker severity high -> blocker queue + Primarch review | Primarch marks result usable or rejected |
| Department Synthesis Bundle | Primarch | Emperor + next department | synthesis summary, merged evidence, residual risks, recommendation | links to all constituent bundles + consistency check | unresolved critical risk -> escalate to Emperor | department stage pass/fail recommendation finalized |
| Handoff Bundle | sending Primarch/department | receiving department | handoff scope, assumptions, dependencies, open risks | source bundle references + acceptance criteria | receiver rejects if assumptions missing | receiver accepts ownership |
| Blocker / Incident Bundle | Astartes or Primarch | Primarch + Emperor (if needed) | blocker_id, severity, impact, attempted mitigations, required decision | reproducible failure evidence | sovereign-boundary blocker -> Emperor escalation | explicit resolution or accepted workaround |
| Completion Bundle | Primarch | Verification/Release + Emperor signoff path | completion claim, gate results, evidence index, known limits | full gate evidence chain; no missing critical proof | any red gate -> reject completion | all required gates pass |
| Release Bundle | Release & Integration role | Emperor + integration targets | release candidate, changelog, verification proof, rollback note | verification reports + integrity checks + package fingerprints | integration mismatch -> blocker queue | release accepted or returned |

## 3) Mandatory metadata for every bundle

1. `bundle_id`
2. `bundle_type`
3. `writer_role`
4. `created_at_utc`
5. `scope_boundary`
6. `claim_set`
7. `evidence_index`
8. `confidence_label`

## 4) Hard trust rules

1. No bundle can claim completion without evidence index.
2. Bundle with unresolved critical blocker cannot be marked PASS.
3. Missing mandatory fields = auto-return, not silent acceptance.

## 5) Current implementation status

1. `REUSABLE`: existing review/integration bundle discipline in repo.
2. `DESIGNED`: unified production bundle taxonomy for multi-department scale.
3. `NOT YET IMPLEMENTED`: one deterministic runtime validator for all bundle classes.

