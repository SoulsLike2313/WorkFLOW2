# Current Platform State

- snapshot_id: `platform-state-20260318-mission-baseline-accepted`
- snapshot_date_utc: `2026-03-18`
- source_of_truth:
  - `workspace_config/workspace_manifest.json`
  - `workspace_config/codex_manifest.json`
  - `projects/*/PROJECT_MANIFEST.json`

## Canonical Main Project

- slug: `platform_test_agent`
- path: `projects/platform_test_agent`
- status: `active`
- role: `primary audit-first tester agent`

## Platform Strategy

- strategy_id: `tester-agent-first`
- model: `all guarded projects require tester-agent evidence before manual testing`
- manual_testing_admission_requires:
  - repo-visible tester-agent report
  - required checks completed
  - final status `PASS` or `PASS_WITH_WARNINGS`

## Canonical Project Status Map

| slug | path | status | manual_testing_gate_state | registry_type |
| --- | --- | --- | --- | --- |
| `platform_test_agent` | `projects/platform_test_agent` | `active` | `gate_owner` | `registry_project` |
| `tiktok_agent_platform` | `projects/wild_hunt_command_citadel/tiktok_agent_platform` | `manual_testing_blocked` | `blocked_until_tester_agent_pass` | `registry_project` |
| `game_ru_ai` | `projects/GameRuAI` | `audit_required` | `manual_testing_blocked_until_tester_agent_pass` | `registry_project` |
| `voice_launcher` | `projects/voice_launcher` | `supporting` | `not_guarded` | `registry_project` |
| `adaptive_trading` | `projects/adaptive_trading` | `experimental` | `not_guarded` | `registry_project` |

## Federation Operational Framing (Current Stage)

Current department:

1. `Analytics Department`:
   - implementation: `platform_test_agent` (`projects/platform_test_agent`)
   - operational role: intake/audit/state-estimation/initial planning/recommendation layer

Not departments in current operational framing:

1. `tiktok_agent_platform` (`projects/wild_hunt_command_citadel/tiktok_agent_platform`)
2. `game_ru_ai` (`projects/GameRuAI`)
3. `voice_launcher` (`projects/voice_launcher`)
4. `adaptive_trading` (`projects/adaptive_trading`)

Current role for these lines:
- `test_product`
- `intake_subject`
- `analysis_candidate`

Canonical intake model anchors:
1. `docs/governance/ANALYTICS_DEPARTMENT_DOCTRINE.md`
2. `docs/governance/TEST_PRODUCT_INTAKE_MODEL.md`
3. `workspace_config/test_product_intake_contract.json`

Historical/non-operational traces (not current entities):

1. `shortform_core`
2. `tiktok_automation_app`
3. `wild_hunt_command_citadel` (container path, not a department)

## Audit-Blocked Scope

- `projects/wild_hunt_command_citadel/tiktok_agent_platform`: `manual_testing_blocked`
- `projects/GameRuAI`: `audit_required` with `manual_testing_blocked` admission state in project manifest

## Current Acceptance Model

Accepted for execution:

1. strict contract tasks matching governance files
2. tasks aligned to canonical next step
3. tasks bounded to declared paths and validation steps

Not accepted for execution:

1. non-canonical tasks
2. insufficient-contract tasks
3. out-of-scope tasks
4. broad creative asks without strict repo contract

## Governance / Federation State

- governance foundation: `accepted`
- repo control center: `accepted`
- targeted bundle export: `accepted`
- operator query layer: `accepted`
- operator command execution layer: `accepted`
- operator task / program layer: `accepted`
- work package / mission layer: `accepted / certified baseline`
- current canonical phase: `constitution-v1-finalized`
- current constitutional regime: `lightweight constitutional enforcement`
- federation operational model: `single real department (Analytics Department)`
- federation model anchor: `docs/governance/FEDERATION_OPERATIONAL_MODEL.md`
- constitutional core artifact: `docs/governance/WORKFLOW2_CONSTITUTION_V1.md`
- constitutional predecessor artifact: `docs/governance/WORKFLOW2_CONSTITUTION_V0.md`
- next canonical direction: `select post-constitution path from controlled options; no automatic new brain-layer launch`

## Canonical Root Context

- canonical operational workspace root: `E:\CVVCODEX`
- safe mirror orientation surface: `WorkFLOW2` (`safe_mirror/main`)
- safe mirror is not sovereign source-of-truth and cannot elevate node rank
- path drift from `E:\CVVCODEX` must reduce trust/admission/rank confidence until revalidated

## Shared Systems Baseline

Installed system baseline for guarded projects:

- `ui_qa_toolkit`
- `verification_toolkit`
- `reporting_toolkit`
- `localization_toolkit`
- `audit_observability_toolkit`

Optional/partial baseline modules:

- `update_patch_toolkit`
- `security_baseline`
