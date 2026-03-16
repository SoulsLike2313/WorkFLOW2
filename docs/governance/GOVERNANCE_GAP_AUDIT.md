# GOVERNANCE GAP AUDIT

Generated from current repository truth at `E:\CVVCODEX`.

## 1) What already exists

Current governance/context baseline is present and readable:

- root context: `README.md`, `REPO_MAP.md`, `MACHINE_CONTEXT.md`
- instruction index: `docs/INSTRUCTION_INDEX.md`
- publication and export contracts: `docs/repo_publication_policy.md`, `docs/CHATGPT_BUNDLE_EXPORT.md`
- sync and execution policies: `workspace_config/GITHUB_SYNC_POLICY.md`, `workspace_config/AGENT_EXECUTION_POLICY.md`, `workspace_config/MACHINE_REPO_READING_RULES.md`
- machine manifests: `workspace_config/workspace_manifest.json`, `workspace_config/codex_manifest.json`, `workspace_config/SAFE_MIRROR_MANIFEST.json`
- safe-state report artifacts: `docs/review_artifacts/SAFE_MIRROR_BUILD_REPORT.md`, `docs/review_artifacts/PUBLIC_REPO_SANITIZATION_REPORT.md`

Canonical model is repeatedly stated and aligned in most core files:

- local source of truth: `E:\CVVCODEX`
- public safe mirror target: `WorkFLOW2` via `safe_mirror/main`
- ChatGPT external reading channel: targeted bundle export

## 2) Contradictions found

### C1. Stale sanitization report conflicts with current canon

`docs/review_artifacts/PUBLIC_REPO_SANITIZATION_REPORT.md` still states:

- `repo_name: WorkFLOW`
- `tracking_branch: origin/main`
- outdated basis SHA

This conflicts with current canonical model (`WorkFLOW2`, `safe_mirror/main`).

### C2. Path policy contradiction

`docs/repo_publication_policy.md` says hardcoded machine-specific absolute paths should be avoided (`<REPO_ROOT>` style), but top-level canonical docs intentionally hardcode `E:\CVVCODEX`.

Result: policy text and operational canon conflict.

### C3. Safe-state identity drift risk

`workspace_config/SAFE_MIRROR_MANIFEST.json` and `docs/review_artifacts/SAFE_MIRROR_BUILD_REPORT.md` are generated from current HEAD, but committing regenerated files changes HEAD immediately after generation.

Result: a recurring one-commit drift can appear between runtime identity claim and final committed HEAD if not handled as a two-step process.

## 3) Duplicates and legacy noise

### D1. Repeated read-order contracts across multiple docs

Read gate/order is duplicated in:

- `README.md`
- `docs/INSTRUCTION_INDEX.md`
- `workspace_config/MACHINE_REPO_READING_RULES.md`

No explicit single-source field is declared for read-order authority.

### D2. Legacy origin references remain as noise

`origin (WorkFLOW)` is marked non-canonical (correct), but still repeatedly present in governance docs. This is useful historically, but creates parsing noise for a new machine if not grouped under one explicit legacy section.

## 4) Weak governance points

### W1. Missing bootstrap read order in codex manifest

`workspace_config/codex_manifest.json` has `bootstrap_read_order` as empty list.

This weakens machine onboarding determinism despite strict read-gate requirements elsewhere.

### W2. No explicit governance hierarchy document

There is no dedicated doc defining authoritative hierarchy of governance layers (constitution -> execution law -> operational contracts -> evidence).

### W3. No explicit anti-false-completion control matrix

Completion controls exist, but they are distributed. There is no single matrix mapping each required completion check to exact proof artifact and failure status.

### W4. No explicit governance self-audit policy

No dedicated policy defines periodic governance integrity checks (consistency scan, stale artifact scan, contradiction scan, drift scan).

## 5) Policy gaps

Missing top-level controlling laws (documented as a single governance stack) for:

- hierarchy resolution when multiple policy docs overlap
- stale report invalidation rules
- generation/commit sequencing for machine state artifacts
- required self-audit cadence and required outputs
- strict handling of legacy references (where allowed vs forbidden)

## 6) Machine-understanding gaps

### M1. New machine can misread stale artifacts as authoritative

`PUBLIC_REPO_SANITIZATION_REPORT.md` currently looks authoritative but is stale and contradicts current mirror model.

### M2. Governance entrypoint ambiguity

There is no one “governance entrypoint” file that says: read this first for governance stack authority, then this order.

### M3. Contract source fragmentation

Task acceptance, execution, reading, sync, and publication constraints are each present, but distributed. Machine confidence depends on resolving multiple docs correctly.

## 7) Missing controls before governance brain stack

Required before stack hardening:

1. Refresh stale sanitization report to current `WorkFLOW2/safe_mirror` canon.
2. Resolve absolute-path policy conflict (either allow canonical absolute root or replace with placeholder model).
3. Define one governance hierarchy source file and point all docs to it.
4. Add codex bootstrap read order to manifest.
5. Add stale-artifact invalidation rule and state-artifact generation/commit sequence rule.
