# README Rewrite Rationale

## Why full rewrite (not partial patch)
A complete rewrite was chosen to:
- eliminate hidden carryover from earlier repository eras,
- align section ordering with current governance,
- make root README a stable repository map instead of a mixed operational memo.

## Design decisions in the new root README
1. Keep only current repository reality:
   - active module fixed to `projects/wild_hunt_command_citadel/shortform_core`.

2. Separate responsibility levels:
   - root README = repository map + entrypoint map,
   - active module README/CODEX = detailed runtime and engineering contracts.

3. Clarify launch model:
   - user mode first, desktop-first script path,
   - developer mode explicit and separate.

4. Keep verification policy unambiguous:
   - canonical verify entrypoint is `python -m app.verify`,
   - manual testing allowed only on `PASS`.

5. Keep update/patch flow usable for non-developer users:
   - local `run_update.ps1` flow shown directly,
   - developer endpoint flow retained only as integration/debug note.

## Expected outcome
- lower documentation drift,
- cleaner onboarding,
- better alignment between repository root and active module lifecycle.
