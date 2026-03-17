# POLICY_DIGEST

Quick map of the policy/governance layer used by Repo Control Center.

## Core principles and hierarchy
- `docs/governance/FIRST_PRINCIPLES.md`
  - Purpose: non-overridable laws.
  - Gate: all gates (foundation).
  - Used by: all modes.
  - Linked with: hierarchy + control/evolution/creative policies.
  - Bootstrap: yes.

- `docs/governance/GOVERNANCE_HIERARCHY.md`
  - Purpose: precedence and conflict resolution by levels.
  - Gate: governance consistency.
  - Used by: creator/integration operators.
  - Linked with: all policy layers.
  - Bootstrap: yes.

## Control layer
- `docs/governance/SELF_VERIFICATION_POLICY.md`
  - Purpose: mandatory self-check before pass claims.
  - Gate: trust/admission discipline.
  - Used by: repo control cycles.
  - Linked with: admission gate.
  - Bootstrap: yes.

- `docs/governance/CONTRADICTION_CONTROL_POLICY.md`
  - Purpose: detect and escalate contradictions.
  - Gate: contradiction status.
  - Used by: trust/governance checks.
  - Linked with: repo-visible truth.
  - Bootstrap: yes.

- `docs/governance/ADMISSION_GATE_POLICY.md`
  - Purpose: define completion/admission requirements.
  - Gate: admission verdict.
  - Used by: creator acceptance flow.
  - Linked with: sync + trust + governance acceptance.
  - Bootstrap: yes.

- `docs/governance/ANTI_DRIFT_POLICY.md`
  - Purpose: stop scope/cosmetic/architecture drift.
  - Gate: drift and trust quality.
  - Used by: ongoing control cycles.
  - Linked with: self-verification + contradiction control.
  - Bootstrap: yes.

## Federation and authority
- `docs/governance/CREATOR_AUTHORITY_POLICY.md`
  - Purpose: creator authority contract and detection rules.
  - Gate: machine mode and creator-only operations.
  - Used by: detect_machine_mode + full-check.
  - Linked with: helper/integration policies.
  - Bootstrap: yes.

- `docs/governance/HELPER_NODE_POLICY.md`
  - Purpose: helper permissions and restrictions.
  - Gate: role boundaries.
  - Used by: helper operations.
  - Linked with: task-id contract and handoff.
  - Bootstrap: yes.

- `docs/governance/INTEGRATION_INBOX_POLICY.md`
  - Purpose: inbound package review flow.
  - Gate: integration readiness.
  - Used by: integration mode.
  - Linked with: handoff schema and inbox contract.
  - Bootstrap: yes.

- `docs/governance/CANONICAL_MACHINE_PROTECTION_POLICY.md`
  - Purpose: protect creator-only canonical zones.
  - Gate: canonical acceptance safety.
  - Used by: creator mode.
  - Linked with: creator authority policy.
  - Bootstrap: yes.

## Evolution layer
- `docs/governance/EVOLUTION_READINESS_POLICY.md`
  - Purpose: readiness criteria for maturity transitions.
  - Gate: evolution verdict.
  - Used by: evolution checks.
  - Linked with: maturity model and threshold policy.
  - Bootstrap: yes.

- `docs/governance/MODEL_MATURITY_MODEL.md`
  - Purpose: maturity levels and required capabilities.
  - Gate: evolution interpretation.
  - Used by: operator and automation checks.
  - Linked with: readiness + signal registry.
  - Bootstrap: yes.

- `docs/governance/PROMOTION_THRESHOLD_POLICY.md`
  - Purpose: hard thresholds for V1->V2 progression.
  - Gate: evolution promotion guard.
  - Used by: repo_control_center evolution logic.
  - Linked with: policy evolution log.
  - Bootstrap: yes.

## Explainability and operating policies
- `workspace_config/GITHUB_SYNC_POLICY.md`
  - Purpose: sync discipline and canonical parity rules.
  - Gate: sync verdict.
  - Used by: repo control sync checks.
  - Linked with: admission and trust.
  - Bootstrap: yes.

- `workspace_config/AGENT_EXECUTION_POLICY.md`
  - Purpose: operator behavior contract.
  - Gate: execution discipline.
  - Used by: agent/assistant operation.
  - Linked with: machine reading rules.
  - Bootstrap: yes.

- `workspace_config/MACHINE_REPO_READING_RULES.md`
  - Purpose: canonical reading/boot order.
  - Gate: bootstrap enforcement.
  - Used by: new machine onboarding.
  - Linked with: codex manifest bootstrap list.
  - Bootstrap: yes.
