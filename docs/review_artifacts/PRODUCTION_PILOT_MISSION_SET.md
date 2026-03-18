# PRODUCTION_PILOT_MISSION_SET

## Selection Rule
- only registry-backed real missions
- bounded scope
- explicit evidence value per mission
- no synthetic showcase mission

## Mission 1: successful bounded engineering mission
- mission_id: `mission.wave3a.status_consolidation.complete.v1`
- mission_class: `status_consolidation_mission`
- purpose: produce refreshed status truth surface and mission-level consolidation report.
- expected risk profile: `LOW`
- expected proof value: validates stable success path with refresh/report discipline.
- why included: gives low-risk baseline execution signal for pilot.

## Mission 2: guarded/controlled state-change mission
- mission_id: `mission.wave3c.creator_only_certification.v1`
- mission_class: `creator_only_certification_mission`
- purpose: validate creator-gated controlled transition with certification semantics.
- expected risk profile: `MEDIUM`
- expected proof value: confirms guarded success path with explicit authority and policy gates.
- why included: mandatory representative proof of allowed guarded execution under Constitution V1.

## Mission 3: intentionally blocked/denied mission
- mission_id: `mission.wave3c.blocked_mutation.policy.v1`
- mission_class: `blocked_mutation_mission`
- purpose: verify blocked transition behavior when policy gate denies execution.
- expected risk profile: `LOW`
- expected proof value: confirms denial path discipline and anti-fake-completion behavior.
- why included: pilot must prove not only success paths but also explicit constitutional denial.

## Mission 4 (optional closure-heavy): review/closure mission
- mission_id: `mission.wave3b.evidence_consolidation.chain.v1`
- mission_class: `evidence_consolidation_mission`
- purpose: validate multi-program consolidation and closure-oriented evidence chain.
- expected risk profile: `MEDIUM`
- expected proof value: strengthens closure-path confidence before broader production use.
- why included: adds review/closure depth without introducing new architecture.

## Balance Assessment
- coverage balance: `GOOD`
- success path: covered
- guarded success path: covered
- denied path: covered
- closure-heavy path: covered (optional but recommended)
