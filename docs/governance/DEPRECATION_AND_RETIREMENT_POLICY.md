# DEPRECATION AND RETIREMENT POLICY

Policy class: Governance v1.1 hardening lifecycle control.

Authority inputs:

- `docs/governance/GOVERNANCE_HIERARCHY.md`
- `workspace_config/workspace_manifest.json`
- `workspace_config/codex_manifest.json`

## 1) Lifecycle statuses

- `deprecated`: still present, replacement path exists, not recommended for new tasks.
- `legacy`: historical/non-canonical, may remain for reference.
- `retired`: execution path disabled, not part of active workflow.
- `archived`: historical record only, excluded from active read paths.

## 2) Marking rules

Any deprecated/legacy/retired/archived artifact must include:

1. explicit status label
2. canonical replacement (if applicable)
3. reason and date
4. authority source for status decision

## 3) Bootstrap read-order removal rules

Must be removed from `bootstrap_read_order`:

1. retired files
2. archived files
3. deprecated files without active control relevance

## 4) Active reading path cleanup rules

Must be removed from active reading indexes:

1. non-canonical legacy evidence without operational role
2. stale artifacts replaced by newer canonical artifacts

## 5) Historical reference retention

Can stay as historical reference only if:

1. marked `legacy`/`archived`
2. excluded from active read order
3. explicitly non-authoritative

## 6) Retirement evidence requirements

Retirement requires:

1. replacement or closure rationale
2. contradiction check proving no active dependency
3. manifest/doc updates reflecting removal
4. sync parity after change