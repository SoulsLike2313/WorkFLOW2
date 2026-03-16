# EVOLUTION READINESS POLICY

Policy class: Level 3 evolution control policy.

Authority inputs:

- `docs/governance/FIRST_PRINCIPLES.md`
- `docs/governance/GOVERNANCE_HIERARCHY.md`
- `docs/governance/DEVIATION_INTELLIGENCE_POLICY.md`
- `docs/governance/GOVERNANCE_EVOLUTION_POLICY.md`
- `docs/governance/ADMISSION_GATE_POLICY.md`

## 1) What qualifies as evolution

Evolution is accepted only when governance and execution capability increase measurably.

Accepted evolution targets:

1. stronger control gates
2. better contradiction/drift detection
3. higher sync/admission discipline
4. better machine-readability and deterministic routing
5. proven reduction of repeated failures

## 2) Promotion eligibility

Generation transition (for example `V1 -> V2`) is allowed only if all are true:

1. sync discipline stable (`HEAD == safe_mirror/main`, divergence `0/0` over repeated cycles)
2. no unresolved critical contradiction
3. no hidden blockers
4. self-verification cycles consistently completed
5. governance stack complete and operational
6. evolution signals and evidence pass threshold from `EVOLUTION_SIGNAL_REGISTRY.md`

## 3) Mandatory evidence

Promotion claims must include:

1. run IDs and command evidence from `repo_control_center.py`
2. trust/sync/governance/admission/evolution verdict history
3. contradiction and drift trend
4. policy-gap closure evidence
5. clear blocker register (or explicit `none`)

Without evidence package, promotion is invalid.

## 4) Initiation authority

Readiness can be initiated by:

1. Repo Control Center `evolution`/`full-check` run
2. explicit governance hardening task
3. self-audit cycle with required checks complete

Informal narrative requests cannot trigger promotion.

## 5) Promotion blockers

Hard blockers:

1. false PASS incident unresolved
2. unresolved critical contradiction
3. hidden blocker or omitted risk
4. repeated drift without hardening
5. broken sync discipline
6. cosmetic churn replacing operational change

If any blocker exists, verdict must be `BLOCKED` or `HOLD`.

## 6) Readiness notification contract

Every readiness notification must include:

1. `current_level`
2. `candidate_level`
3. `readiness`
4. `signals_gained`
5. `blocking_signals`
6. `policy_changes_proposed`
7. recommendation: `HOLD | PREPARE | PROMOTE`

Notification artifacts:

- `runtime/repo_control_center/evolution_status.json`
- `runtime/repo_control_center/evolution_report.md`