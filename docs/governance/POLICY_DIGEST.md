# POLICY_DIGEST

Compact governance/policy digest for Repo Control Center verdict chain.
Coverage: documents that directly affect control gates and machine-mode behavior.

## Digest Records

| Document | Purpose | Controlled Gate/Area | Primary Consumer | Bootstrap Required |
| --- | --- | --- | --- | --- |
| `docs/governance/FIRST_PRINCIPLES.md` | Non-overridable operating laws | All gates (foundation) | All modes | Yes |
| `docs/governance/GOVERNANCE_HIERARCHY.md` | Policy precedence and conflict order | Governance consistency | Creator/Integration | Yes |
| `docs/governance/SELF_VERIFICATION_POLICY.md` | Mandatory self-check before PASS claims | Trust/Admission discipline | Repo control cycles | Yes |
| `docs/governance/CONTRADICTION_CONTROL_POLICY.md` | Contradiction detection and escalation | Contradiction gate | Trust/Governance checks | Yes |
| `docs/governance/ADMISSION_GATE_POLICY.md` | Formal admission conditions | Admission verdict | Creator acceptance flow | Yes |
| `docs/governance/ANTI_DRIFT_POLICY.md` | Drift detection and response | Drift/Trust quality | Control cycles | Yes |
| `docs/governance/CREATOR_AUTHORITY_POLICY.md` | Creator authority contract and detection | Machine mode / authority gate | Mode detection + full-check | Yes |
| `docs/governance/HELPER_NODE_POLICY.md` | Helper operation boundaries | Role restrictions | Helper execution flow | Yes |
| `docs/governance/INTEGRATION_INBOX_POLICY.md` | Handoff inbox review state machine | Integration readiness | Integration review flow | Yes |
| `docs/governance/CANONICAL_MACHINE_PROTECTION_POLICY.md` | Protection of creator-only control zones | Canonical acceptance safety | Creator mode operations | Yes |
| `docs/governance/EVOLUTION_READINESS_POLICY.md` | Maturity readiness contract | Evolution readiness | Evolution checks | Yes |
| `docs/governance/PROMOTION_THRESHOLD_POLICY.md` | Formal thresholds for promotion | Evolution promotion guard | Evolution checks | Yes |
| `docs/governance/GOVERNANCE_ACCEPTANCE_GATE.md` | Mandatory gate before next stage | Governance acceptance | Full-check chain | Yes |
| `workspace_config/GITHUB_SYNC_POLICY.md` | Sync parity and completion discipline | Sync verdict | Sync checks / completion gate | Yes |
| `workspace_config/AGENT_EXECUTION_POLICY.md` | Execution boundaries and refusal discipline | Execution governance | Agent runtime behavior | Yes |
| `workspace_config/MACHINE_REPO_READING_RULES.md` | Canonical read order contract | Bootstrap enforcement | New machine onboarding | Yes |

## Role Separation
- `MACHINE_OPERATOR_GUIDE.md`: runbook and gate interpretation.
- `MACHINE_CAPABILITIES_SUMMARY.md`: capability/authority matrix.
- `POLICY_DIGEST.md` (this file): compressed map of policy control responsibilities.
