# NOTIFICATION AND ESCALATION POLICY

Policy class: Governance v1.1 hardening notification control.

Authority inputs:

- `docs/governance/ADMISSION_GATE_POLICY.md`
- `docs/governance/INCIDENT_AND_ROLLBACK_POLICY.md`
- `docs/governance/SECURITY_AND_EXPOSURE_INCIDENT_POLICY.md`

## 1) Mandatory notification conditions

System must notify user when any of the following occurs:

1. trust verdict is `NOT_TRUSTED`
2. sync verdict is not `IN_SYNC`
3. admission verdict is `REJECTED`
4. evolution verdict is `BLOCKED`
5. security/exposure incident detected

## 2) Mandatory escalation conditions

Escalation is mandatory for:

1. critical contradiction
2. false PASS incident
3. hidden blocker detection
4. exposure/security incident
5. repeated drift without hardening

## 3) Silence-forbidden rule

Silence is forbidden when blocker exists.

Required output must include:

1. blocker type
2. evidence
3. impact
4. required next step

## 4) Evolution readiness notifications

For each evolution run, report:

1. current level
2. candidate level
3. readiness
4. signals gained
5. blocking signals
6. recommendation (`HOLD|PREPARE|PROMOTE`)

## 5) Blocker escalation rules

1. unresolved critical blocker -> immediate escalation
2. unresolved major blocker in two cycles -> escalation
3. unresolved blocker at completion boundary -> verdict cannot be `PASS`

## 6) Security escalation rules

1. immediate escalation on detection
2. freeze notice
3. rollback/remediation notice
4. trusted-restore notice only after revalidation

## 7) Contradiction escalation rules

1. critical contradiction -> immediate escalation
2. major contradiction unresolved at completion -> conditional/rejected outcome

## 8) Promotion review notifications

Before any `PROMOTE` claim, send promotion review notice with:

1. evidence threshold status
2. observation window status
3. blocking signal status
4. explicit recommendation