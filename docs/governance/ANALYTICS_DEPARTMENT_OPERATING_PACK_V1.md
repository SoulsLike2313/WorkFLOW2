# ANALYTICS_DEPARTMENT_OPERATING_PACK_V1

Status:
- pack_version: `v1`
- department: `Analytics Department`
- activation_state: `ACTIVE_NOW`
- implementation_carrier: `projects/platform_test_agent`

Assertion labels:
- `PROVEN`
- `REUSABLE`
- `DESIGNED`
- `NOT YET IMPLEMENTED`

## 1) Mission

Analytics Department is the first active production head.

Mission:
1. принять вход (идея, демка, сырой app, bundle, сообщение о создании app);
2. сделать честный первичный аудит;
3. построить техническую карту;
4. найти дырки и риски;
5. выдать roadmap и routing proposal по следующим блокам.

## 2) Intake rules

### Allowed intake forms

1. `idea_seed` (текстовая/структурная идея)
2. `demo_seed` (демо-репо/архив/ветка)
3. `raw_app_seed` (сырая рабочая версия)
4. `legacy_app_seed` (существующий app с долгом)
5. `message_about_app_creation` (owner task signal)

### Mandatory intake minimum

1. source identity (откуда пришел вход);
2. declared goal (что хотим получить);
3. available artifacts list;
4. known constraints (time, stack, environment).

If minimum missing:
1. intake status = `ROUTE_CONTINUED_ANALYSIS`;
2. explicit missing list is mandatory.

## 3) Product analysis protocol

1. Intake normalization.
2. Project shape detection.
3. Architecture snapshot.
4. Code health snapshot.
5. Testability snapshot.
6. UX/readiness snapshot.
7. Operational risk snapshot.
8. Done/not-done map.
9. Initial route proposal.

Evidence rule: every major claim must link to inspected artifact path or runtime signal.

## 4) Technical mapping protocol

Technical Map Bundle must contain:
1. system topology (modules, boundaries, dependencies);
2. stack map (languages/frameworks/tooling);
3. execution map (build/run/test entrypoints);
4. quality map (coverage gaps, brittle zones, debt zones);
5. release readiness map (what blocks stable release now).

## 5) Defect discovery rules

Analytics must detect and classify:
1. structural defects (broken architecture boundaries);
2. code defects (logic bugs, unsafe behavior, anti-patterns);
3. test defects (missing tests, non-deterministic checks);
4. operational defects (deployment/run fragility);
5. process defects (missing evidence chain, false completion markers).

## 6) Architecture risk mapping

Mandatory risk classes:
1. `R1_CRITICAL` - blocks safe continuation;
2. `R2_HIGH` - likely to break release quality;
3. `R3_MEDIUM` - raises cost/maintenance risk;
4. `R4_LOW` - non-blocking but should be tracked.

Each risk requires:
1. cause;
2. impact;
3. evidence;
4. recommended mitigation owner.

## 7) Roadmap generation rules

Roadmap from analytics must:
1. split work into bounded phases;
2. assign each phase to candidate department path;
3. include gate to pass before next phase;
4. include "do not do now" list (anti-overbuild).

## 8) Department activation proposal rules

Analytics can propose activation of mapped-later departments only when:
1. intake analysis is complete enough;
2. required scope cannot be safely executed by Analytics-only flow;
3. proposal includes evidence and expected outputs.

Analytics cannot self-activate sovereign authority.

## 9) Emitted outputs after intake

Minimum output pack:
1. Intake Bundle (normalized);
2. Technical Map Bundle;
3. Gap Map;
4. Initial Roadmap;
5. Routing Recommendation;
6. Department Activation Proposal (if needed).

## 10) Trustworthiness and anti-hallucination discipline

Analytics is trustworthy only if:
1. claims are evidence-backed;
2. unknowns are explicit;
3. certainty labels are attached (`PROVEN`/`PARTIAL`/`NOT PROVEN`);
4. no PASS claim without gate evidence.

Forbidden fake confidence patterns:
1. "looks fine" without artifact evidence;
2. hidden assumptions not marked as inference;
3. optimistic completion claim while blockers exist.

## 11) Owner outcomes by intake type

### If owner gives a raw idea

Owner receives:
1. feasibility-first technical framing;
2. initial architecture options;
3. minimal build path and risk map.

### If owner gives a demo

Owner receives:
1. what is reusable vs throwaway;
2. what blocks production quality;
3. concrete hardening roadmap.

### If owner gives a working but broken app

Owner receives:
1. defect map by severity;
2. stabilization plan;
3. validation requirements before release.

### If owner gives debt-heavy project

Owner receives:
1. debt inventory;
2. priority repair order by risk;
3. staged modernization route without broad rewrite.

## 12) Evidence anchors

1. `docs/governance/ANALYTICS_DEPARTMENT_DOCTRINE.md` (`PROVEN`)
2. `docs/governance/TEST_PRODUCT_INTAKE_MODEL.md` (`PROVEN`)
3. `workspace_config/test_product_intake_contract.json` (`REUSABLE`)
4. `docs/governance/DEPARTMENT_MAP_V1.md` (`DESIGNED`)

