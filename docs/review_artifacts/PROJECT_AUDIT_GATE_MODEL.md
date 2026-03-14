# Project Audit Gate Model

## Canonical Owner

- project: `platform_test_agent`
- role: platform audit agent and manual testing admission controller

## Gate States

| State | Meaning | Manual Testing |
| --- | --- | --- |
| `audit_required` | Target project must pass tester-agent audit sequence | blocked |
| `manual_testing_blocked` | Target project has active manual testing block until admission evidence is produced | blocked |
| `PASS` | Tester-agent final audit verdict | allowed |
| `PASS_WITH_WARNINGS` | Tester-agent final audit verdict with warnings | allowed |
| `FAIL` | Tester-agent final audit verdict | blocked |

## Required Audit Axes

1. verification
2. readiness
3. UI-QA (if UI exists)
4. reporting checks
5. localization audit
6. audit/observability audit
7. evidence collection and final machine report

## Admission Evidence Contract

Mandatory evidence:

1. repo-visible summaries
2. repo-visible final machine audit report
3. status for admission (`PASS` or `PASS_WITH_WARNINGS`)

If evidence is missing or non-repo-visible:

- resulting state: `manual_testing_blocked`

## Current Guarded Projects

1. `projects/wild_hunt_command_citadel/tiktok_agent_platform` -> `manual_testing_blocked`
2. `projects/GameRuAI` -> `audit_required`
