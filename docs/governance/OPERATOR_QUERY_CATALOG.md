# OPERATOR_QUERY_CATALOG

## Purpose
Formal catalog of operator query classes and expected handling scope.

## Query Classes

### 1) mode_query
- Purpose: resolve current machine mode.
- Scope: runtime mode identity (`creator` / `helper` / `integration`).
- Canonical evidence: `one_screen_status.json`, `creator_detect_machine_mode_output.json`.
- Response shape: contract core + mode-specific `current_state`.

### 2) authority_query
- Purpose: resolve authority presence and creator-level acceptance eligibility.
- Scope: authority contract state and authority-bound rights.
- Canonical evidence: `one_screen_status.json`, `creator_authority_env_output.txt`.
- Response shape: contract core + `authority` + optional `escalation_requirement`.

### 3) workspace_health_query
- Purpose: report current technical control health state.
- Scope: workspace integrity, sync, blocking factors.
- Canonical evidence: `one_screen_status.json`, `repo_control_status.json`.
- Response shape: contract core + health-focused `current_state`.

### 4) governance_query
- Purpose: report governance compliance and governance acceptance status.
- Scope: governance verdict chain and gate readiness.
- Canonical evidence: `one_screen_status.json`, `repo_control_status.json`.
- Response shape: contract core + governance-focused `verdict`.

### 5) admission_query
- Purpose: report admission gate availability.
- Scope: admission verdict and admission status layer.
- Canonical evidence: `one_screen_status.json`, `repo_control_status.json`.
- Response shape: contract core + admission-focused `verdict`.

### 6) capability_query
- Purpose: report allowed/forbidden action surface.
- Scope: machine capabilities, authority-bound operations, forbidden actions.
- Canonical evidence: `MACHINE_CAPABILITIES_SUMMARY.md`, `federation_mode_contract.json`.
- Response shape: contract core + `capability_scope`.

### 7) blocker_query
- Purpose: report active blockers and category.
- Scope: blocker category, blocker detail, escalation requirement.
- Canonical evidence: `one_screen_status.json`, `repo_control_status.json`.
- Response shape: contract core + `blocking_factors`.

### 8) next_step_query
- Purpose: report canonical next operational step.
- Scope: next canonical step routing only.
- Canonical evidence: `one_screen_status.json`, `docs/NEXT_CANONICAL_STEP.md`.
- Response shape: contract core + `next_step`.

### 9) policy_reference_query
- Purpose: resolve policy basis for a verdict/restriction.
- Scope: policy mapping and gate ownership.
- Canonical evidence: `POLICY_DIGEST.md`, governance policy docs.
- Response shape: contract core + `policy_basis`.

## Class-to-Evidence Priority
1. Runtime one-screen snapshot for current state.
2. Full runtime status for detailed evidence.
3. Governance policy docs for basis references.
4. Capability and operator guide docs for action surface interpretation.

## Stability Rule
Similar query wording must resolve to the same request class unless scope truly changes.
