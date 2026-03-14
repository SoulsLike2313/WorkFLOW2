# Test Agent Platform Reframe Report

## Reframe Scope

Platform model changed from app-first to tester-agent-first.

Canonical active project:

- `platform_test_agent`
- path: `projects/platform_test_agent`

## Canonical Tester-Agent Identity

- name: `Platform Test Agent`
- slug: `platform_test_agent`
- manifest: `projects/platform_test_agent/PROJECT_MANIFEST.json`

## Files Updated for Reframe

1. `README.md`
2. `workspace_config/workspace_manifest.json`
3. `workspace_config/codex_manifest.json`
4. `workspace_config/PROJECT_RULES.md`
5. `workspace_config/TASK_RULES.md`
6. `workspace_config/AGENT_EXECUTION_POLICY.md`
7. `workspace_config/MACHINE_REPO_READING_RULES.md`
8. `workspace_config/codex_bootstrap.md`
9. `docs/INSTRUCTION_INDEX.md`
10. `projects/wild_hunt_command_citadel/tiktok_agent_platform/PROJECT_MANIFEST.json`
11. `projects/GameRuAI/PROJECT_MANIFEST.json`

## Files Present in Reframed Model

1. `projects/platform_test_agent/PROJECT_MANIFEST.json`
2. `projects/platform_test_agent/README.md`
3. `projects/platform_test_agent/CODEX.md`
4. `projects/platform_test_agent/run_project.ps1`
5. `workspace_config/PROJECT_AUDIT_POLICY.md`
6. `docs/review_artifacts/TEST_AGENT_PLATFORM_REFRAME_REPORT.md`
7. `docs/review_artifacts/PROJECT_AUDIT_GATE_MODEL.md`

## Status Transitions Applied

1. `tiktok_agent_platform` -> `manual_testing_blocked`
2. `game_ru_ai` -> `audit_required`

## Manual Testing Gate (Reframed)

Manual testing admission now requires:

1. tester-agent final status `PASS` or `PASS_WITH_WARNINGS`;
2. repo-visible audit summaries;
3. final machine audit report as admission evidence.

Without all conditions, admission remains blocked.
