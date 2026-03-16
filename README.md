# CVVCODEX Workspace

## Canonical Architecture

- Working source of truth: `E:\CVVCODEX`.
- Public safe mirror only: `WorkFLOW2` (`safe_mirror/main`, `https://github.com/SoulsLike2313/WorkFLOW2.git`).
- `WorkFLOW2` is not the full working repository and must receive only approved safe state.
- Official external reading channel for ChatGPT: targeted bundle export (`scripts/export_chatgpt_bundle.py`).
- Governance brain stack is mandatory interpretation layer for all machine/agent execution.

## Active Project

- Active project slug: `platform_test_agent`
- Active path: `projects/platform_test_agent`
- Canonical project registry source: `workspace_config/workspace_manifest.json`

## Canonical Workflow

1. Local work and validation in `E:\CVVCODEX`.
2. Reconcile docs/manifests/policy against repo reality.
3. Run sync and self-verification gates.
4. Push approved safe state to `safe_mirror/main` (`WorkFLOW2`).
5. For ChatGPT reading, export targeted bundle instead of exposing full repo.

## Governance Brain Stack (Mandatory)

### Level 0

- `docs/governance/FIRST_PRINCIPLES.md`

### Level 1-4 Integration Anchor

- `docs/governance/GOVERNANCE_HIERARCHY.md`
- `docs/governance/SELF_VERIFICATION_POLICY.md`
- `docs/governance/CONTRADICTION_CONTROL_POLICY.md`
- `docs/governance/ADMISSION_GATE_POLICY.md`
- `docs/governance/ANTI_DRIFT_POLICY.md`
- `docs/governance/DEVIATION_INTELLIGENCE_POLICY.md`
- `docs/governance/GOVERNANCE_EVOLUTION_POLICY.md`
- `docs/governance/CREATIVE_REASONING_POLICY.md`
- `docs/governance/AGENT_CHARACTER_PROFILE.md`
- `docs/governance/EVOLUTION_READINESS_POLICY.md`
- `docs/governance/MODEL_MATURITY_MODEL.md`
- `docs/governance/EVOLUTION_SIGNAL_REGISTRY.md`
- `docs/governance/POLICY_EVOLUTION_LOG.md`
- `docs/governance/NEXT_EVOLUTION_CANDIDATE.md`

### Governance v1.1 Hardening Layer

- `docs/governance/POLICY_CHANGE_AUTHORITY_POLICY.md`
- `docs/governance/INCIDENT_AND_ROLLBACK_POLICY.md`
- `docs/governance/VERIFICATION_DEPTH_POLICY.md`
- `docs/governance/EVIDENCE_RETENTION_POLICY.md`
- `docs/governance/PROMOTION_THRESHOLD_POLICY.md`
- `docs/governance/SECURITY_AND_EXPOSURE_INCIDENT_POLICY.md`
- `docs/governance/DEPRECATION_AND_RETIREMENT_POLICY.md`
- `docs/governance/OPERATIONAL_METRICS_POLICY.md`
- `docs/governance/NOTIFICATION_AND_ESCALATION_POLICY.md`
- `docs/governance/GOVERNANCE_SCHEMA_VERSIONING_POLICY.md`
- `docs/governance/MACHINE_BOOTSTRAP_CONTRACT.md`
- `docs/governance/CANONICAL_SOURCE_PRECEDENCE.md`
- `docs/governance/ZERO_CONFIG_OPERATION_POLICY.md`

## Repo Control Center V1 (CLI-First)

Canonical control entrypoint:

```powershell
python scripts/repo_control_center.py <mode>
```

Supported modes:

- `status`
- `audit`
- `trust`
- `sync`
- `mirror`
- `bundle`
- `evolution`
- `full-check`

Core verdicts:

- TRUST VERDICT: `TRUSTED | WARNING | NOT_TRUSTED`
- SYNC VERDICT: `IN_SYNC | DRIFTED | BLOCKED`
- GOVERNANCE VERDICT: `COMPLIANT | PARTIAL | NON_COMPLIANT`
- ADMISSION VERDICT: `ADMISSIBLE | CONDITIONAL | REJECTED`
- EVOLUTION VERDICT: `HOLD | PREPARE | V2_CANDIDATE | V2_READY | PROMOTE | BLOCKED`

Runtime artifacts:

- `runtime/repo_control_center/repo_control_status.json`
- `runtime/repo_control_center/repo_control_report.md`
- `runtime/repo_control_center/evolution_status.json`
- `runtime/repo_control_center/evolution_report.md`

## Completion Gate (Hard)

Completion is forbidden if any of the following is missing:

- repo-visible truth in tracked files,
- sync parity with `safe_mirror/main`,
- mandatory self-verification pass.

Required checks:

- `git status --short --branch`
- `git rev-parse HEAD`
- `git rev-parse safe_mirror/main`
- `git rev-list --left-right --count HEAD...safe_mirror/main`
- `python scripts/check_repo_sync.py --remote safe_mirror --branch main`

## Targeted ChatGPT Bundle Export

Canonical command:

```powershell
python scripts/export_chatgpt_bundle.py <mode> [options]
```

Modes:

- `context`
- `files --include ...`
- `paths --include ...`
- `project --slug <slug>`
- `request --request-file <file>`

Protocol reference:

- `docs/CHATGPT_BUNDLE_EXPORT.md`

## Root Map

- `projects/` - project roots.
- `shared_systems/` - reusable systems.
- `workspace_config/` - governance/manifests/policies.
- `scripts/` - execution and validation scripts.
- `docs/` - governance and review artifacts.
- `runtime/` - generated runtime outputs (non-authoritative).

## Source-of-Truth Order

1. `docs/governance/FIRST_PRINCIPLES.md`
2. `docs/governance/GOVERNANCE_HIERARCHY.md`
3. `workspace_config/workspace_manifest.json`
4. `workspace_config/codex_manifest.json`
5. project `PROJECT_MANIFEST.json`
6. this `README.md`
7. review artifacts as evidence only

## Legacy Note

- `origin` (`WorkFLOW`) is legacy/non-canonical for completion and safe mirror sync.
