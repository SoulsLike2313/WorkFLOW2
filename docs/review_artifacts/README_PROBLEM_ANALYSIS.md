# README Problem Analysis

## Scope and reading strategy
To avoid noisy full-file dumps, the root `README.md` was reviewed in two steps:
1. targeted marker search (`Select-String`) for stale patterns,
2. focused section review by line ranges for launch/structure/verification blocks.

## Targeted markers reviewed
Markers checked first:
- `E:\CVVCODEX`
- `.exe`
- `active_projects`
- `tiktok_automation_app`
- `legacy`
- launch/update wording (`launch`, `localhost`, `uvicorn`, `run_setup`)

## Problematic fragments identified in the previous root README
1. Fragment:
   - `README.md:32` - `Secondary / legacy / experimental components:`
   - `README.md:36` - `...not the primary reference...`
   Why problematic:
   - status taxonomy was vague and not tied to an explicit repository-map rule;
   - wording was broad, but did not state where canonical runtime contracts live.

2. Fragment:
   - `README.md:44` - `python -m app.launcher user`
   - `README.md:48-49` - direct developer commands
   Why problematic:
   - commands were valid, but the README did not first enforce environment setup in the same section;
   - this can cause drift between root instructions and active module practice.

3. Fragment:
   - `README.md:86-88` - developer update API endpoints in root flow
   Why problematic:
   - root README should primarily act as repository map and user-safe entrypoint guide;
   - endpoint-level details belong to active module docs and should be referenced, not over-specified.

4. Gap:
   - no explicit statement that root README is a map while runtime contracts are maintained in `tiktok_agent_platform/core` docs.
   Why problematic:
   - increases chance of root/module documentation divergence over time.

## Critical stale markers status in previous README
- `E:\CVVCODEX`: not found
- `.exe` references: not found
- `active_projects`: not found
- `tiktok_automation_app`: not found

Conclusion:
- the previous README was already cleaner than old legacy versions, but still needed normalization to make root/module responsibility boundaries explicit and launch guidance more deterministic.
