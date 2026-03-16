# GOVERNANCE SCHEMA VERSIONING POLICY

Policy class: Governance v1.1 hardening schema/version control.

Authority inputs:

- `workspace_config/workspace_manifest.json`
- `workspace_config/codex_manifest.json`
- `docs/governance/GOVERNANCE_HIERARCHY.md`

## 1) Versioning scope

Versioning rules apply to:

1. policy document schemas
2. machine manifests
3. report schemas
4. maturity model definitions
5. evolution artifacts

## 2) Versioning model

Use semantic policy/schema versioning:

- `MAJOR`: breaking compatibility
- `MINOR`: backward-compatible extension
- `PATCH`: clarification/fix without schema break

## 3) Compatibility rules

Backward-compatible change examples:

1. adding optional fields
2. adding non-breaking statuses
3. adding new report sections with defaults

Breaking change examples:

1. removing required fields
2. changing required field semantics
3. renaming canonical fields without migration

## 4) Breaking change requirements

Breaking changes require:

1. explicit approval in task contract
2. migration plan
3. compatibility impact statement
4. full validation cycle

## 5) Migration requirements

Migration package must include:

1. before/after schema mapping
2. migration sequence
3. validation commands
4. rollback path

## 6) Drift detection expectations

Schema drift checks must verify:

1. manifest fields match current docs
2. read-order references are valid
3. required artifacts follow expected schema fields
4. no stale schema assumptions in active policies

## 7) Completion gate for versioning changes

Versioning-related completion is forbidden if:

1. migration requirements are incomplete
2. schema compatibility state is undefined
3. required validation evidence missing