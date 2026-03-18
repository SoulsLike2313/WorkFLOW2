# CONSTITUTION_PHASE_HYGIENE_CHECKLIST_V1

## Scope
Minimal pre-completion/pre-certification checklist for Constitution-first phase.

## Checklist
1. Canonical phase coherent
- `CURRENT_PLATFORM_STATE`, `NEXT_CANONICAL_STEP`, `README`, `REPO_MAP`, `MACHINE_CONTEXT`, `INSTRUCTION_INDEX` align on `constitution-first`.

2. Next step coherent
- no stale route to pre-constitution implementation step.

3. Truth-state usage valid
- terms use canonical enum from:
  - `workspace_config/schemas/truth_state_schema.json`
  - `docs/governance/TRUTH_STATE_MODEL_V1.md`

4. Contradiction scan status known
- run `python scripts/validation/scan_canonical_contradictions.py`
- record verdict (`PASS|WARNING|FAIL`).

5. Registry-doc drift status known
- run `python scripts/validation/check_registry_doc_drift.py`
- record verdict (`PASS|WARNING|FAIL`).

6. Runtime truth pointer present
- mission/program/repo-control runtime truth paths are available and referenced.

7. Sync / trust / governance status known
- run `python scripts/repo_control_center.py bundle`
- run `python scripts/repo_control_center.py full-check`
- verify `sync`, `trust`, `governance`, `governance_acceptance`, `admission`.

8. No fake completion claims
- do not claim completion if unresolved contradiction or gate blocker exists.

## Use
- This checklist is operational guardrail, not a new governance layer.
- If any item is unknown, status is at most `PARTIAL`.
