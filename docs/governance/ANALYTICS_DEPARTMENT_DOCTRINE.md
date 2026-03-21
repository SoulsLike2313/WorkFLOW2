# ANALYTICS_DEPARTMENT_DOCTRINE

Status:
- doctrine_version: `v1`
- scope: `current single-department operational doctrine`
- stage: `constitution-v1-finalized / bounded federation operation`

## 1) Identity

Current real department:
1. `Analytics Department`
2. implementation carrier: `platform_test_agent` (`projects/platform_test_agent`)

Hard distinction:
1. department identity is doctrinal (`Analytics Department`);
2. implementation carrier is technical/runtime (`platform_test_agent`).

## 2) Mission

Analytics Department mission:
1. accept incoming file/application/bundle/message about application creation;
2. perform primary parsing and first audit pass;
3. determine current state (`what exists / what is missing`);
4. produce initial plan;
5. produce primary recommendations for downstream operational blocks.

## 3) Inputs

Accepted intake inputs:
1. project/application source files;
2. portable bundles and transfer packages (safe-mode bounded);
3. operator mission/program/task requests for analysis;
4. evidence/status artifacts attached to intake subject.

## 4) Outputs

Required output classes:
1. intake classification (`test_product` / `intake_subject` / `analysis_candidate`);
2. first-pass audit result;
3. missing-scope map;
4. initial execution plan;
5. recommendation set with routing signal for next blocks.

## 5) Responsibilities

Analytics Department is responsible for:
1. intake discipline and bounded triage;
2. first audit and evidence extraction;
3. status normalization for intake subjects;
4. recommendation package for next-stage routing;
5. preserving fail-closed boundaries when evidence is insufficient.

## 6) Boundaries

Analytics Department does not:
1. claim sovereign acceptance;
2. perform constitutional mutation;
3. self-promote intake subjects into independent departments without doctrine+registry update;
4. bypass rank/policy/admission gates.

## 7) Federation Relation

1. Analytics Department is the current operational department inside Federation.
2. Other lines are routed to Analytics as intake/analysis subjects in current stage.
3. Federation is operational development block only, not sovereign authority.

## 8) Rank Relation

1. Emperor:
   - sovereign authority and final canonical acceptance boundaries.
2. Primarch:
   - operational oversight and bounded non-sovereign direction for analytics work.
3. Astartes:
   - execution lane for bounded intake/audit/report tasks.

## 9) Downstream Relation

Analytics outputs may route subjects to:
1. remediation/fix block (when blockers are clear and bounded);
2. readiness/certification preparation (when evidence baseline is sufficient);
3. continued analysis state (when data is incomplete);
4. blocked/quarantine path (when policy/authority/preconditions fail).

Routing remains recommendation-grade until accepted through existing governance/admission flow.

## 10) Ownership and Escalation Anchors

1. Guardian model: `workspace_config/department_guardian_registry.json`.
2. Exception/escalation model: `docs/governance/DEPARTMENT_EXCEPTION_ESCALATION_HARDENING_V1.md`.
3. Exception/escalation contract: `workspace_config/department_exception_escalation_contract.json`.
