# CONTRADICTION CONTROL POLICY

Policy class: Level 2 control policy.

Authority inputs:

- `docs/governance/FIRST_PRINCIPLES.md`
- `docs/governance/GOVERNANCE_HIERARCHY.md`
- `workspace_config/MACHINE_REPO_READING_RULES.md`

## 1) Objective

Detect, classify, and resolve contradictions between:

1. root docs (`README.md`, `REPO_MAP.md`, `MACHINE_CONTEXT.md`)
2. machine manifests (`workspace_config/*.json`, project manifests)
3. governance policies
4. repository reality (tracked files, current git state)

Completion is blocked while critical contradictions remain unresolved.

## 2) Canonical source precedence

Precedence order for contradiction resolution:

1. Level 0 laws: `docs/governance/FIRST_PRINCIPLES.md`
2. Hierarchy authority: `docs/governance/GOVERNANCE_HIERARCHY.md`
3. Workspace registry truth: `workspace_config/workspace_manifest.json`
4. Machine onboarding truth: `workspace_config/codex_manifest.json`
5. Root navigation truth: `README.md`
6. Evidence artifacts (`docs/review_artifacts/*`) as non-authoritative logs

If two sources conflict, higher precedence wins.

## 3) Contradiction classes

`CRITICAL`:

1. active project mismatch between root docs and manifest
2. sync-gate contradiction (completion allowed despite unsynced state)
3. source-of-truth contradiction (`E:\\CVVCODEX` vs other canonical root)
4. safe mirror target contradiction (`safe_mirror/main` vs other canonical target)
5. stale artifact presented as current authoritative state

`MAJOR`:

1. policy clauses with opposing operational behavior
2. entrypoint mismatch between docs and manifest
3. inconsistent completion gate wording across policy docs

`MINOR`:

1. redundant wording without semantic conflict
2. legacy note noise that is correctly marked non-canonical

## 4) Detection protocol

Mandatory contradiction scan before completion:

1. compare canonical identity fields:
   - local root
   - public safe mirror target
   - active project
2. compare completion gate rules across policy docs
3. compare required read order and authority declarations
4. compare generated state artifacts against current git reality

## 5) Resolution protocol

For each contradiction:

1. log source files and exact conflicting statements
2. classify severity (`CRITICAL`/`MAJOR`/`MINOR`)
3. resolve by precedence order
4. update lower-precedence source(s) to match canonical source
5. rerun contradiction scan

## 6) Escalation rules

`CRITICAL`:

1. immediate escalation
2. completion status forced to `FAIL` or `NOT_COMPLETED`
3. release/publish actions paused until resolved

`MAJOR`:

1. must be resolved in current task or explicitly deferred with blocker record
2. completion allowed only as `PASS_WITH_WARNINGS` if not completion-critical

`MINOR`:

1. may be deferred if non-blocking
2. must be tracked in governance backlog

## 7) Hard completion block

Completion is forbidden when unresolved `CRITICAL` contradiction exists.

Minimum required evidence for completion:

1. contradiction scan result: no unresolved critical items
2. sync proof against `safe_mirror/main`
3. updated files reflect canonical precedence

