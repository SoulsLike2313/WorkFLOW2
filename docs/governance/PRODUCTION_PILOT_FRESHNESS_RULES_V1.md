# PRODUCTION_PILOT_FRESHNESS_RULES_V1

## Purpose
Define minimal freshness discipline for constitutional production pilot execution and closure claims.

## Refresh Before Pilot Execution
Required pre-execution freshness refresh:
1. `python scripts/repo_control_center.py bundle`
2. `python scripts/repo_control_center.py full-check`
3. `python scripts/validation/run_constitution_checks.py`

Required fresh surfaces:
- `runtime/repo_control_center/repo_control_status.json`
- `runtime/repo_control_center/repo_control_report.md`
- `runtime/repo_control_center/constitution_status.json`
- `runtime/repo_control_center/constitution_status.md`
- mission runtime surfaces for active mission run

## Refresh Before Pilot Completion Claim
Before claiming pilot mission completion or pilot PASS:
1. refresh mission runtime outputs for the final run;
2. rerun `repo_control_center full-check`;
3. rerun constitutional checks aggregation;
4. for closure missions, refresh safe mirror evidence and run post-refresh full-check.

## Stale Downgrade Rule
Pilot verdict is downgraded to `PILOT_PARTIAL` when any of the following is stale/unknown at claim time:
- `repo_control_status` freshness against current `HEAD`
- `constitution_status` freshness against latest check outputs
- mission runtime evidence missing for final run_id

## Minimum Freshness Chain
Mandatory reporting chain for pilot closure packet:
1. mission execution run_id
2. mission runtime artifacts
3. constitutional checks status
4. repo_control full-check status
5. (if applicable) mirror refresh evidence
6. post-refresh full-check status

If chain item is missing, completion claim is not certifiable as pilot `PASS`.
