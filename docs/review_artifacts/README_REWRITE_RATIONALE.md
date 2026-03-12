# README Rewrite Rationale

## Why full rewrite (not partial patch)
A complete rewrite was chosen to:
- eliminate hidden carryover from earlier repository eras,
- align section ordering with current governance,
- make root README a stable repository map instead of a mixed operational memo.

## Design decisions in the new root README
1. Keep only current repository reality:
   - active project fixed to `projects/wild_hunt_command_citadel/tiktok_agent_platform`.

2. Separate responsibility levels:
   - root README = repository map + entrypoint map,
   - active module README/CODEX = detailed runtime and engineering contracts.

3. Clarify launch model:
   - user mode first, desktop-first script path,
   - developer mode explicit and separate.

4. Keep verification policy unambiguous:
   - canonical verify entrypoint is `python scripts/project_startup.py run --project-slug tiktok_agent_platform --entrypoint verify --startup-kind verify --port-mode fixed`,
   - manual testing allowed only on `PASS`.

5. Keep update/patch flow usable for non-developer users:
   - canonical root update flow shown via `project_startup.py` and active project slug,
   - update command aligned with workspace registry entrypoints.

## Expected outcome
- lower documentation drift,
- cleaner onboarding,
- better alignment between repository root and active module lifecycle.
