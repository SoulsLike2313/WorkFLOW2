# Next Canonical Step

- step_id: `next-step-governance-acceptance-closure`
- effective_date_utc: `2026-03-17`
- previous_accepted_stage: `governance-v11-hardening-and-repo-control-baseline`

## What Do We Do Next

Canonical next execution step is:

`governance acceptance closure` under formal gate control.

No optimization/filesystem/product branch execution is allowed before this gate is PASS.

## Canonical Goal

Close governance acceptance foundation with repo-visible proof:

1. governance acceptance gate exists and passes
2. bootstrap enforcement is executable and influences verdict chain
3. repo control evidence/runtime reports are exportable via audit-safe channel
4. sync/self-verification parity remains clean (`safe_mirror/main` 0/0)

## Canonical Scope

- target layer:
  - `docs/governance/**`
  - `scripts/repo_control_center.py`
  - `scripts/export_chatgpt_bundle.py`
  - `workspace_config/**` (only required integration keys/configs)
  - `docs/CHATGPT_BUNDLE_EXPORT.md`
- forbidden scope:
  - product feature work
  - filesystem optimization work
  - UI work
  - cross-project rebuilds

## Canonical Outputs

1. `docs/governance/GOVERNANCE_ACCEPTANCE_GATE.md`
2. refreshed `docs/NEXT_CANONICAL_STEP.md` (this file)
3. bootstrap enforcement evidence in Repo Control Center full-check output
4. audit-safe runtime export mode for RCC reports with explicit allowlist
5. runtime evidence files generated and export-verified

## Canonical Acceptance Criteria

1. governance acceptance gate verdict is `PASS`
2. `python scripts/repo_control_center.py full-check` shows bootstrap enforcement and governance acceptance sections
3. audit-safe export mode includes only allowlisted RCC runtime files and blocks non-allowlisted runtime
4. standard exporter policy still blocks generic runtime paths
5. `git status` clean and divergence with `safe_mirror/main` is `0/0`

## Canonical Prohibitions For This Step

1. no stage transition without governance acceptance gate PASS
2. no global exporter policy weakening
3. no completion claim without repo-visible truth + sync + self-verification + governance acceptance

## Rejection Condition

Any task request that skips governance acceptance closure must be rejected as:

```text
STATUS: REJECTED
REASON: non-canonical
NO EXECUTION
```
