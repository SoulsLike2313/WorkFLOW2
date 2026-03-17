# POLICY_DIGEST

Digest map of policy documents that directly influence Repo Control Center gate behavior.

## Core Gate-Control Policies

| Document | Primary Function | Gate/Layer Controlled | Bootstrap Required |
| --- | --- | --- | --- |
| `docs/governance/FIRST_PRINCIPLES.md` | Non-overridable operating laws | Global foundation | Yes |
| `docs/governance/GOVERNANCE_HIERARCHY.md` | Precedence and conflict resolution | Governance coherence | Yes |
| `docs/governance/SELF_VERIFICATION_POLICY.md` | Mandatory self-check requirement | Trust/admission discipline | Yes |
| `docs/governance/CONTRADICTION_CONTROL_POLICY.md` | Contradiction detection/escalation | Contradiction gate | Yes |
| `docs/governance/ADMISSION_GATE_POLICY.md` | Admission criteria definition | Admission verdict | Yes |
| `docs/governance/ANTI_DRIFT_POLICY.md` | Drift detection and response rules | Drift/trust quality | Yes |
| `docs/governance/GOVERNANCE_ACCEPTANCE_GATE.md` | Transition gate before next stage | Governance acceptance | Yes |

## Authority / Federation Policies

| Document | Primary Function | Gate/Layer Controlled | Bootstrap Required |
| --- | --- | --- | --- |
| `docs/governance/CREATOR_AUTHORITY_POLICY.md` | Creator authority contract | Machine-mode authority gate | Yes |
| `docs/governance/HELPER_NODE_POLICY.md` | Helper execution boundaries | Role restrictions | Yes |
| `docs/governance/INTEGRATION_INBOX_POLICY.md` | Inbox review state machine | Integration readiness | Yes |
| `docs/governance/CANONICAL_MACHINE_PROTECTION_POLICY.md` | Canonical protection boundaries | Creator-only control zones | Yes |

## Evolution Policies

| Document | Primary Function | Gate/Layer Controlled | Bootstrap Required |
| --- | --- | --- | --- |
| `docs/governance/EVOLUTION_READINESS_POLICY.md` | Evolution readiness contract | Evolution readiness | Yes |
| `docs/governance/PROMOTION_THRESHOLD_POLICY.md` | Formal promotion thresholds | Evolution promotion guard | Yes |
| `docs/governance/MODEL_MATURITY_MODEL.md` | Maturity stage definitions | Evolution interpretation | Yes |

## Operating Policies

| Document | Primary Function | Gate/Layer Controlled | Bootstrap Required |
| --- | --- | --- | --- |
| `workspace_config/GITHUB_SYNC_POLICY.md` | Sync parity discipline | Sync verdict | Yes |
| `workspace_config/AGENT_EXECUTION_POLICY.md` | Execution boundary contract | Execution governance | Yes |
| `workspace_config/MACHINE_REPO_READING_RULES.md` | Canonical read-order contract | Bootstrap enforcement | Yes |

## Role Separation
- `MACHINE_OPERATOR_GUIDE.md`: operational runbook.
- `MACHINE_CAPABILITIES_SUMMARY.md`: capability/authority matrix.
- `POLICY_DIGEST.md`: condensed policy-to-gate mapping.
