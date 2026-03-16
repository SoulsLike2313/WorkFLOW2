# GOVERNANCE HIERARCHY

Authoritative governance stack for this repository.

Design inputs applied:

- `docs/governance/GOVERNANCE_GAP_AUDIT.md`
- `docs/governance/GOVERNANCE_STACK_PLAN.md`

Global rules:

1. Higher level always wins over lower level.
2. Evidence artifacts never override policy/manifests.
3. Legacy references are non-authoritative unless explicitly marked canonical.
4. Any stale artifact conflicting with higher-level truth is invalid until refreshed.

## Level 0: First Principles

Purpose:

- immutable law layer defining non-negotiable constraints for execution and reporting

What it can override:

- all lower levels (L1-L4) when conflict exists

What it cannot override:

- repository physical reality (actual files, git state, command outcomes)

Expected documents:

- `docs/governance/FIRST_PRINCIPLES.md`

Conflict resolution rule:

- if any lower rule conflicts with L0 law, lower rule is invalid

## Level 1: Core Operating Policies

Purpose:

- enforce admission, scope, execution boundaries, and mandatory behavior

What it can override:

- L2-L4 procedural details that violate core execution law

What it cannot override:

- Level 0 laws

Expected documents:

- `workspace_config/TASK_RULES.md`
- `workspace_config/EXECUTION_ADMISSION_POLICY.md`
- `workspace_config/TASK_SOURCE_POLICY.md`
- `workspace_config/AGENT_EXECUTION_POLICY.md`

Conflict resolution rule:

- when L1 documents conflict, stricter executable constraint wins; ambiguity is resolved by refusal (`REJECTED`) not by assumption

## Level 2: Control & Audit Policies

Purpose:

- enforce deterministic reading order, sync/completion gates, publication boundaries, and external sharing controls

What it can override:

- L3-L4 operational shortcuts that weaken control or auditability

What it cannot override:

- Level 0 and Level 1 constraints

Expected documents:

- `workspace_config/MACHINE_REPO_READING_RULES.md`
- `workspace_config/GITHUB_SYNC_POLICY.md`
- `workspace_config/COMPLETION_GATE_RULES.md`
- `docs/repo_publication_policy.md`
- `docs/CHATGPT_BUNDLE_EXPORT.md`
- `docs/governance/MACHINE_BOOTSTRAP_CONTRACT.md`
- `docs/governance/CANONICAL_SOURCE_PRECEDENCE.md`
- `docs/governance/ZERO_CONFIG_OPERATION_POLICY.md`
- `scripts/repo_control_center.py`

Conflict resolution rule:

- if control/safety rule conflicts with productivity shortcut, control/safety rule wins

## Level 3: Adaptive / Evolution Policies

Purpose:

- govern system evolution, self-audit loops, stale-artifact control, and policy hardening sequence

What it can override:

- L4 project-specific process choices when repo-wide governance evolution requires normalization

What it cannot override:

- Level 0-2 constraints

Expected documents:

- `docs/governance/GOVERNANCE_GAP_AUDIT.md`
- `docs/governance/GOVERNANCE_STACK_PLAN.md`
- `docs/governance/DEVIATION_INTELLIGENCE_POLICY.md`
- `docs/governance/GOVERNANCE_EVOLUTION_POLICY.md`
- `docs/governance/CREATIVE_REASONING_POLICY.md`
- `docs/governance/EVOLUTION_READINESS_POLICY.md`
- `docs/governance/MODEL_MATURITY_MODEL.md`
- `docs/governance/EVOLUTION_SIGNAL_REGISTRY.md`
- `docs/governance/POLICY_EVOLUTION_LOG.md`
- `docs/governance/NEXT_EVOLUTION_CANDIDATE.md`

Conflict resolution rule:

- if adaptive change proposal conflicts with active L0-L2 law, proposal is blocked until higher-level law is updated explicitly

## Level 4: Project-Specific Policies

Purpose:

- define per-project execution contracts, manifests, and project-local rules under global governance

What it can override:

- only project-local defaults that do not conflict with L0-L3

What it cannot override:

- any repository-level governance constraint from L0-L3

Expected documents:

- `projects/*/PROJECT_MANIFEST.json`
- `projects/*/README.md`
- `projects/*/CODEX.md` (if present)
- project-local policy docs

Conflict resolution rule:

- project rule is valid only if it passes all higher-level gates; otherwise higher-level policy prevails and project rule is treated as non-canonical

## Cross-Level Conflict Algorithm

1. Identify all conflicting sources.
2. Sort by level priority (L0 highest, L4 lowest).
3. Keep highest-level valid source as authority.
4. Mark lower conflicting source as stale/non-canonical.
5. Require explicit update to restore consistency.

## Mandatory Anti-False-Completion Enforcement

A completion claim is valid only if all are true:

- required outputs exist at declared paths
- outputs pass declared validation
- worktree is clean
- `HEAD == safe_mirror/main`
- divergence is `0/0`
- final status is backed by command evidence

If any item fails:

- status must be `NOT_COMPLETED` or `FAIL`
