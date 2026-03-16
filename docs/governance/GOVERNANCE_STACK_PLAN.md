# GOVERNANCE STACK PLAN

Current plan state for governance brain stack and control/evolution layers.

## Implemented layers

### Layer 0: First Principles

- `docs/governance/FIRST_PRINCIPLES.md`

### Layer 1: Core Operating Policies

- `workspace_config/TASK_RULES.md`
- `workspace_config/EXECUTION_ADMISSION_POLICY.md`
- `workspace_config/TASK_SOURCE_POLICY.md`
- `workspace_config/AGENT_EXECUTION_POLICY.md`

### Layer 2: Control & Audit

- `workspace_config/MACHINE_REPO_READING_RULES.md`
- `workspace_config/GITHUB_SYNC_POLICY.md`
- `workspace_config/COMPLETION_GATE_RULES.md`
- `docs/repo_publication_policy.md`
- `docs/CHATGPT_BUNDLE_EXPORT.md`
- `scripts/repo_control_center.py`

### Layer 3: Adaptive & Evolution

- `docs/governance/DEVIATION_INTELLIGENCE_POLICY.md`
- `docs/governance/GOVERNANCE_EVOLUTION_POLICY.md`
- `docs/governance/CREATIVE_REASONING_POLICY.md`
- `docs/governance/EVOLUTION_READINESS_POLICY.md`
- `docs/governance/MODEL_MATURITY_MODEL.md`
- `docs/governance/EVOLUTION_SIGNAL_REGISTRY.md`
- `docs/governance/POLICY_EVOLUTION_LOG.md`
- `docs/governance/NEXT_EVOLUTION_CANDIDATE.md`

### Layer 4: Project-Specific

- `projects/*/PROJECT_MANIFEST.json`
- project-local `README.md`/`CODEX.md` where present

## Current execution order

1. local work in `E:\CVVCODEX`
2. run Repo Control Center checks
3. run sync and self-verification gates
4. push approved safe state to `safe_mirror/main`
5. generate targeted ChatGPT bundle when needed

## Next implementation order

1. keep evolution signal evidence updated per run
2. keep policy evolution log synchronized with accepted/rejected changes
3. keep safe mirror artifact freshness in each completion cycle
4. maintain contradiction-free read order across docs/manifests