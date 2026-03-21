# TEST_PRODUCT_INTAKE_MODEL

Status:
- model_version: `v1`
- scope: `current-stage test product intake and routing`
- non_goal: `no automatic multi-department expansion`

## 1) Definition

`Test product` is a non-department operational line entering Analytics intake for evaluation.

Equivalent current framing:
1. `test_product`
2. `intake_subject`
3. `analysis_candidate`

These terms are aligned for current stage and do not imply department status.

## 2) Current Intake Subjects

Current non-department lines:
1. `tiktok_agent_platform`
2. `game_ru_ai`
3. `voice_launcher`
4. `adaptive_trading`

## 3) Intake Entry Conditions

A test product enters intake when at least one is true:
1. operator submits package/request for first-pass analysis;
2. project status is blocked/audit-required/experimental/supporting and needs normalization;
3. new bundle/file set indicates product-under-formation state.

## 4) Primary Intake Flow

1. Receive intake payload.
2. Parse structure and available evidence.
3. Run first-pass audit.
4. Determine `present/missing` capability/evidence map.
5. Produce initial plan + recommendations.
6. Emit routing outcome.

## 5) Routing Outcomes

1. `ROUTE_REMEDIATION`
   - bounded fix path is clear.
2. `ROUTE_READINESS_PREP`
   - readiness/certification path can be prepared.
3. `ROUTE_CONTINUED_ANALYSIS`
   - evidence insufficient or ambiguity unresolved.
4. `ROUTE_BLOCKED_OR_QUARANTINE`
   - policy/authority/precondition failure.

## 6) Promotion / Non-Promotion Rules

A test product may become a separate block/department later only if:
1. explicit doctrine update exists;
2. registry-level formalization is updated;
3. authority/governance acceptance path is explicit.

Otherwise it remains:
1. intake subject,
2. analysis candidate,
3. non-department operational line.

## 7) Evidence Requirements

Minimum intake evidence package:
1. intake identity and source;
2. first-pass audit output;
3. missing-scope map;
4. initial plan;
5. routing outcome with rationale.

## 8) Limits

1. This model is bounded to current single-department stage.
2. It does not claim automatic product-to-department promotion.
3. It does not replace constitutional/admission/rank gates.

## 9) Ownership and Taxonomy Anchors

1. Guardian registry: `workspace_config/department_guardian_registry.json`.
2. Shared taxonomy contract: `workspace_config/shared_taxonomy_contract.json`.
3. Escalation exceptions: `workspace_config/department_exception_escalation_contract.json`.
