# LOCAL / GIT / GITHUB SINGLE-TRUTH REPORT

- repo name: `WorkFLOW`
- checked branch: `main`
- local head: `a8ca0681a14a7da30d0b1d58e8faedf4862e2144`
- origin/main head: `a8ca0681a14a7da30d0b1d58e8faedf4862e2144`
- sync status: `IN_SYNC` (ahead=0, behind=0)
- working tree status: `CLEAN`

## Canonical Active Project
- slug: `tiktok_agent_platform`
- path: `projects/wild_hunt_command_citadel/tiktok_agent_platform`

## Canonical Project Inventory
- `tiktok_agent_platform` | status=`active` | priority=`1` | path=`projects/wild_hunt_command_citadel/tiktok_agent_platform`
- `voice_launcher` | status=`supporting` | priority=`2` | path=`projects/voice_launcher`
- `adaptive_trading` | status=`experimental` | priority=`3` | path=`projects/adaptive_trading`
- `game_ru_ai` | status=`experimental` | priority=`5` | path=`projects/GameRuAI`

## Priority Paths State
- `projects/wild_hunt_command_citadel/shortform_core`: local_exists=True, local_files=11166, tracked_files=0, origin_files=0, ignored_local_files=11166
- `projects/wild_hunt_command_citadel/tiktok_agent_platform`: local_exists=True, local_files=18009, tracked_files=387, origin_files=387, ignored_local_files=17622
- `projects/GameRuAI`: local_exists=True, local_files=4308, tracked_files=525, origin_files=525, ignored_local_files=3783

## Mismatches Found
- M1: shortform_core existed only as local ignored residue while previous canonical wording could be interpreted as repo-visible path.

## Mismatches Fixed
- M1: Aligned README and workspace_manifest to classify shortform_core as local-only ignored legacy residue (tracked_by_git=false, github_visible=false).

## Remaining Gaps
- none

- stage1 consolidation status: `PASS`
- final agreement status: `MATCH`
