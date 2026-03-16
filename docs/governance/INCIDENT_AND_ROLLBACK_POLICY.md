# INCIDENT AND ROLLBACK POLICY

Policy class: Governance v1.1 hardening incident control.

Authority inputs:

- `docs/governance/SELF_VERIFICATION_POLICY.md`
- `docs/governance/ADMISSION_GATE_POLICY.md`
- `docs/governance/DEVIATION_INTELLIGENCE_POLICY.md`

## 1) Governance incident definition

Governance incident is any event where control truth is violated, including:

1. false completion claim
2. unresolved critical contradiction at completion
3. hidden blocker in final report
4. sync gate bypass
5. unsafe publication state accepted as trusted

## 2) False PASS incident definition

False PASS incident occurs when reported `PASS` is contradicted by factual checks:

1. dirty worktree
2. divergence not `0/0`
3. missing required artifact
4. failed mandatory validation check

## 3) Rollback trigger conditions

Immediate rollback trigger if any is true:

1. false PASS incident confirmed
2. critical security/exposure incident
3. broken canonical source-of-truth mapping
4. incorrect policy relaxation pushed to mirror

## 4) Rollback scope

Rollback scope must be minimal but sufficient:

1. affected files only for isolated policy/doc defect
2. full governance layer rollback for hierarchy/law breach
3. mirror rollback to last trusted SHA for exposure incident

## 5) Freeze conditions

Freeze required for:

1. unresolved critical incident
2. repeated incident pattern in same layer
3. uncertain blast radius

Freeze means:

- no promotion
- no completion verdicts above `REJECTED`/`FAIL`
- only incident remediation work allowed

## 6) Recovery sequence

1. detect and classify incident
2. freeze affected scope
3. identify last trusted commit
4. apply rollback/fix
5. rerun mandatory checks
6. clear freeze only with evidence package

## 7) Post-incident hardening requirements

After incident closure, mandatory actions:

1. add deviation record in policy evolution log
2. add or tighten rule that would have prevented incident
3. run self-audit cycle and report outcome
4. confirm sync parity and trusted state restoration