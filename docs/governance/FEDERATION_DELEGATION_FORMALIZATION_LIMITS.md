# FEDERATION_DELEGATION_FORMALIZATION_LIMITS

Status:
- version: `v1`
- scope: `post-hardening boundary statement`

## Formalized Machine-Readably

1. Rank authority/delegation baseline is formalized in `workspace_config/delegation_registry.json`.
2. Claim-class taxonomy baseline is machine-enforced in `scripts/validation/check_sovereign_claim_denial.py`.
3. Shared taxonomy contract is formalized in `workspace_config/claim_taxonomy_contract.json`.
4. Department guardian/ownership model (rank/layer level) is formalized in `workspace_config/department_guardian_registry.json`.
5. Exception/escalation override contract is formalized in `workspace_config/department_exception_escalation_contract.json`.
6. Unified shared taxonomy is formalized in `workspace_config/shared_taxonomy_contract.json`.

## Formalized Documentarily

1. Department escalation paths are explicit in `docs/governance/FEDERATION_DEPARTMENT_ESCALATION_MATRIX.md`.
2. Primarch/Astartes delegation baseline is explicit in `docs/governance/PRIMARCH_ASTARTES_DELEGATION_MATRIX.md`.
3. Current Federation operational model is explicit in `docs/governance/FEDERATION_OPERATIONAL_MODEL.md` (single real department).
4. Exception/escalation policy is explicit in `docs/governance/DEPARTMENT_EXCEPTION_ESCALATION_HARDENING_V1.md`.

## Still Draft or Inferred

1. Permanent owner/guardian assignment by named operator for `Analytics Department`.
2. Department-specific escalation exceptions and auto-route registry (if introduced later).
3. Full mission-program-task command composition matrix for future multi-department scale.
4. Ownership feasibility is tracked in `docs/review_artifacts/DEPARTMENT_OWNERSHIP_GAP_REPORT.md`.

## Intentionally Open

1. No speculative ownership empire model.
2. No new sovereign layer semantics beyond existing rank policies.
3. No conversion of non-department project lines into departments without explicit doctrine.
4. No broad refactor of governance stack in this phase.
