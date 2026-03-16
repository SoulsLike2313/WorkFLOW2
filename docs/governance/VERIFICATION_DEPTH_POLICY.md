# VERIFICATION DEPTH POLICY

Policy class: Governance v1.1 hardening verification control.

Authority inputs:

- `docs/governance/SELF_VERIFICATION_POLICY.md`
- `docs/governance/ADMISSION_GATE_POLICY.md`
- `docs/governance/ANTI_DRIFT_POLICY.md`

## 1) Verification depth matrix by change type

| Change type | Minimum depth | Required checks |
| --- | --- | --- |
| docs (non-policy) | smoke + contradiction scan | file existence, link/read-order coherence |
| policy docs | self-audit mandatory | contradiction scan, admission checks, sync checks |
| manifests | self-audit mandatory | JSON validity, read-order validity, contradiction scan |
| scripts/tooling | full validation mandatory | compile/run checks + self-audit + sync checks |
| architecture model changes | full audit mandatory | hierarchy impact review + full-check + explicit approval |
| public mirror exposure controls | full audit mandatory | security/exposure checks + sync + rollback readiness |

## 2) Smoke-check sufficient conditions

Smoke-check is sufficient only when all are true:

1. no policy semantics changed
2. no manifest semantics changed
3. no gate behavior changed
4. no exposure/security impact

## 3) Self-audit mandatory conditions

Self-audit is mandatory for:

1. any policy change
2. any manifest change
3. any completion claim
4. any sync-state affecting change
5. any evolution recommendation change

## 4) Full audit mandatory conditions

Full audit is mandatory for:

1. hierarchy or first-principles changes
2. admission/sync gate behavior changes
3. security/exposure incident remediation
4. promotion threshold changes

## 5) Completion forbidden due to insufficient depth

Completion is forbidden when:

1. required depth is not reached for changed type
2. mandatory checks not executed
3. executed checks do not match declared depth
4. blocker found but depth not escalated

Required report line:

- `verification_depth: <smoke|self-audit|full-audit>`