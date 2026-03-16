# REPO_MAP

## Workspace Purpose

`CVVCODEX` is the local source-of-truth workspace with `WorkFLOW2` as public safe mirror.

## Read First

1. `README.md`
2. `workspace_config/workspace_manifest.json`
3. `workspace_config/codex_manifest.json`
4. `docs/CURRENT_PLATFORM_STATE.md`
5. `docs/NEXT_CANONICAL_STEP.md`
6. `workspace_config/SAFE_MIRROR_MANIFEST.json`
7. `docs/review_artifacts/SAFE_MIRROR_BUILD_REPORT.md`

## Local Root and Sync Target

- Local working root for preparation: `E:\CVVCODEX`
- Remote publication-safe target: `safe_mirror/main` (`WorkFLOW2`)
- Rule: local sanitation/validation first, then sync approved state only.
- ChatGPT reading model: targeted CLI bundle export (`scripts/export_chatgpt_bundle.py`), not full-repository exposure.
- Legacy remote `origin` (`WorkFLOW`) is non-canonical in current architecture.

## Canonical Top-Level Directories

- `projects/`: product and platform project roots.
- `shared_systems/`: reusable system modules (`SYSTEM_MANIFEST.json` per module).
- `workspace_config/`: governance, manifests, execution contracts.
- `scripts/`: workspace utilities (`validate_workspace`, `install_system`, `remove_system`, sync checks).
- `docs/`: policy docs and review artifacts.
- `runtime/`: generated runtime diagnostics (non-source).

## Project Registry (Canonical)

- `platform_test_agent` -> `projects/platform_test_agent` (`active`)
- `tiktok_agent_platform` -> `projects/wild_hunt_command_citadel/tiktok_agent_platform` (`manual_testing_blocked`)
- `voice_launcher` -> `projects/voice_launcher` (`supporting`)
- `adaptive_trading` -> `projects/adaptive_trading` (`experimental`)
- `game_ru_ai` -> `projects/GameRuAI` (`audit_required`)

Authority: `workspace_config/workspace_manifest.json`.

## Non-Registry Paths

- `projects/wild_hunt_command_citadel` (container path, not standalone project).
- Layer manifests under TikTok project:
  - `projects/wild_hunt_command_citadel/tiktok_agent_platform/core/PROJECT_MANIFEST.json`
  - `projects/wild_hunt_command_citadel/tiktok_agent_platform/agent/PROJECT_MANIFEST.json`

## Source of Truth Order

1. `workspace_config/workspace_manifest.json`
2. `PROJECT_MANIFEST.json` of the target project
3. `README.md`
4. `docs/review_artifacts/*` (evidence only, not authority)

## Intentional Exclusions

- Public mirror/tunnel/server-publication tooling is excluded from canonical repo workflow.
- Local network diagnostics and temporary setup reports are excluded from tracked state.

## Targeted Bundle Entrypoint

- Exporter: `python scripts/export_chatgpt_bundle.py`
- Protocol doc: `docs/CHATGPT_BUNDLE_EXPORT.md`
