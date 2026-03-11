# WORKSPACE_NORMALIZATION_RATIONALE

## Why normalization was necessary
A workspace with multiple projects needs explicit, machine-readable boundaries. README-only governance is insufficient for strict verification and repeatable onboarding.

## What normalization introduces
1. Single source of truth for project registry:
- `workspace_config/workspace_manifest.json`

2. Codex onboarding contract:
- `workspace_config/codex_manifest.json`
- `workspace_config/codex_bootstrap.md`

3. Future project standard:
- `workspace_config/PROJECT_RULES.md`
- templates + generator + validator

4. Proof-first verification model:
- artifacts must be present and populated, not only documented.

## Resulting properties
- stronger project isolation,
- explicit active project targeting,
- reduced ambiguity for new devices,
- auditable claims of readiness.
