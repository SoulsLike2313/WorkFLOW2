# Repository Publication Policy

## Scope

This repository is maintained as a **public audit/core workspace**.

Canonical public safe mirror state is `safe_mirror/main` (`WorkFLOW2`).

Canonical local preparation root is `E:\CVVCODEX`.

Publication-safe synchronization model:

1. sanitize and validate locally in `E:\CVVCODEX`
2. build safe mirror manifest/report
3. sync approved safe state to GitHub `WorkFLOW2` via `safe_mirror`
4. use targeted bundle export for ChatGPT reading requests

Legacy remote note:

- `origin` (`WorkFLOW`) is non-canonical in this architecture.

## ChatGPT Reading Boundary

ChatGPT reading must be request-scoped via:

- `python scripts/export_chatgpt_bundle.py <mode> ...`

Full repository exposure is non-canonical for task-scoped ChatGPT analysis.

## Published in Public Repository

The public repository intentionally keeps:

1. `README.md`, `REPO_MAP.md`, `MACHINE_CONTEXT.md`
2. `workspace_config/**` governance, manifests, and policy contracts
3. `scripts/**` workspace orchestration and validation entrypoints
4. `projects/**` source, manifests, docs, and active/supporting modules
5. `shared_systems/**` reusable system modules and system manifests
6. `docs/**` architecture, governance, and review artifacts (sanitized)

## Excluded from Public Repository

The following are intentionally local-only and must not be committed:

1. secrets (`.env*`, keys, tokens, credentials, cookies, sessions)
2. runtime/debug output (`runtime/**`, `setup_reports/**`, logs, traces, dumps)
3. transient local caches (`tmp`, `temp`, `cache`, `__pycache__`, `.pytest_cache`, `.mypy_cache`)
4. local environment trees (`.venv`, `venv`, `node_modules`)
5. publication/tunnel leftovers (`tools/public_mirror/**`, tunnel credentials, router diagnostics)
6. heavy local data not required for audit readability (`models`, `datasets`, media caches, setup assets)

## Sanitization Rules

1. No real secrets in tracked files.
2. No hardcoded machine-specific absolute paths; use placeholders (for example: `<REPO_ROOT>`, `<USER_HOME>`).
3. No private WAN/LAN diagnostics in tracked state.
4. If an artifact is required for audit context but contains sensitive values, commit only a sanitized form.

## External Auditor Reading Order

1. `README.md`
2. `workspace_config/workspace_manifest.json`
3. `workspace_config/codex_manifest.json`
4. `docs/INSTRUCTION_INDEX.md`
5. target `PROJECT_MANIFEST.json` and target project `README.md`

## Publication Gate

Before declaring any task complete:

1. `git status` must be clean.
2. `HEAD` must equal `safe_mirror/main`.
3. required outputs must be repo-visible on GitHub.
4. `workspace_config/SAFE_MIRROR_MANIFEST.json` must be refreshed for current state.
