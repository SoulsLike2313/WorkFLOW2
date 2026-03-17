# Repository Publication Policy

## Canonical Publication Model

- Working source of truth for development: `E:\CVVCODEX`
- Public safe mirror only: `WorkFLOW2` via `safe_mirror/main`
- `WorkFLOW2` is not a full working repository
- Official ChatGPT reading path: targeted bundle export (`scripts/export_chatgpt_bundle.py`)

## Governance Requirement

Publication and sharing decisions must follow governance brain stack:

- `docs/governance/FIRST_PRINCIPLES.md`
- `docs/governance/GOVERNANCE_HIERARCHY.md`
- `docs/governance/ADMISSION_GATE_POLICY.md`
- `docs/governance/SELF_VERIFICATION_POLICY.md`
- `docs/governance/CONTRADICTION_CONTROL_POLICY.md`
- `docs/governance/ANTI_DRIFT_POLICY.md`
- `docs/governance/OPERATOR_COMMAND_EXECUTION_CONTRACT.md`

## What Is Allowed In WorkFLOW2

- root architecture docs (`README.md`, `REPO_MAP.md`, `MACHINE_CONTEXT.md`)
- governance/policy/manifests in `workspace_config/`
- `docs/` needed for machine-readable audit context
- operator command execution layer artifacts (`docs/governance/OPERATOR_COMMAND_*`, `workspace_config/operator_command_registry.json`)
- project/source files approved by safe state policy

## What Is Forbidden In WorkFLOW2

- secrets (`.env*`, keys, tokens, credentials, cookies, sessions)
- network/tunnel/router/publication artifacts
- runtime dumps, logs, tmp/cache artifacts
- local machine-only traces and diagnostics
- legacy publication tooling (`tools/public_mirror/*`)

## Publication-Safe Workflow

1. perform work and validation in `E:\CVVCODEX`
2. reconcile docs/manifests/policy with repo reality
3. run Repo Control Center checks (`status`, `trust`, `sync`, `evolution`, `full-check`)
4. run sync and self-verification gates
5. push approved safe state to `safe_mirror/main`
6. export request-scoped bundle for ChatGPT when needed

## Evolution Readiness Governance

Publication governance must include:

- `docs/governance/EVOLUTION_READINESS_POLICY.md`
- `docs/governance/MODEL_MATURITY_MODEL.md`
- `docs/governance/EVOLUTION_SIGNAL_REGISTRY.md`
- `docs/governance/POLICY_EVOLUTION_LOG.md`
- `docs/governance/NEXT_EVOLUTION_CANDIDATE.md`

## Completion Gate

Completion is forbidden without all three:

- repo-visible truth
- sync integrity (`HEAD == safe_mirror/main`, divergence `0/0`)
- self-verification pass

## Legacy Note

- Remote `origin` (`WorkFLOW`) is legacy/non-canonical for this architecture.
