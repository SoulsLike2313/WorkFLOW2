# CANONICAL SOURCE PRECEDENCE

Policy class: contradiction resolution contract for source authority.

## 1) Authority layers

Precedence from highest to lowest:

1. Repo reality and command evidence (`git`, script outputs, existing files)
2. Level 0-1 governance law (`FIRST_PRINCIPLES`, `GOVERNANCE_HIERARCHY`, core execution policies)
3. Canonical manifests (`workspace_manifest.json`, `codex_manifest.json`, relevant `PROJECT_MANIFEST.json`)
4. Control policies and contracts (`GITHUB_SYNC_POLICY`, `MACHINE_REPO_READING_RULES`, admission/verification policies)
5. Narrative docs (`README.md`, `REPO_MAP.md`, `MACHINE_CONTEXT.md`, indexes)
6. Review artifacts and runtime reports (evidence only, non-authoritative for policy)

## 2) Conflict rule

When two sources conflict:

1. choose higher-precedence source
2. mark lower source as stale/non-canonical
3. record contradiction in audit/report
4. update stale source before completion claim

## 3) Special cases

### Active project source

Authoritative source:

- `workspace_config/workspace_manifest.json` -> `active_project`

Narrative docs cannot override this value.

### Sync source

Authoritative source:

- `git rev-parse HEAD`
- `git rev-parse safe_mirror/main`
- `git rev-list --left-right --count HEAD...safe_mirror/main`

Narrative sync claims are invalid without command evidence.

### Safe mirror evidence source

Authoritative contract:

- `workspace_config/SAFE_MIRROR_MANIFEST.json`
- `docs/review_artifacts/SAFE_MIRROR_BUILD_REPORT.md`
- evidence basis model (`basis_head_sha`)

## 4) Forbidden behavior

Forbidden:

1. treating lower-level narrative as override for manifest/policy
2. completion claim with unresolved critical contradiction
3. using legacy artifact as canonical source
4. reporting PASS when evidence and source precedence disagree

## 5) Minimum contradiction response

If critical contradiction is found:

1. status becomes `NOT_COMPLETED` or `FAIL`
2. fix conflicting source or explicitly retire stale source
3. rerun sync/trust/full-check gates before any PASS claim
