# EPHEMERAL_BUNDLE_TTL_POLICY_V1

Status:
- status: `active`
- scope: `E:\CVVCODEX`
- ttl_hours: `24`

## Purpose

Define safe, cheap, deterministic cleanup of temporary bundle/revision outputs without touching canonical tracked artifacts.

## Scope

Policy applies only to explicitly designated ephemeral roots:

1. `runtime/manual_safe_bundle_staging`
2. `runtime/chatgpt_bundle_exports`
3. `runtime/chatgpt_bundle_requests`

Everything outside these roots is out of cleanup scope.

## Hard Safety Rules

1. dry-run is default behavior.
2. deletion requires explicit apply flag.
3. tracked git paths are protected and cannot be deleted by janitor.
4. canonical tracked artifacts are never targetable.
5. latest/current bundle set is protected (`keep_latest_per_root`).
6. pinned bundles are protected when pin marker/registry says so.
7. cleanup report is mandatory for every run.

## Age and Eligibility

1. age is computed from filesystem last-modified time.
2. item becomes eligible only when age >= 24h.
3. eligible does not mean guaranteed delete; protection checks still apply.

## Active/Protected Set

Protected classes:

1. latest N entries per root (`keep_latest_per_root`);
2. explicit pin by marker file;
3. explicit pin by pin registry (if configured);
4. tracked-path protection.

## Archived Owner-Kept Bundles

Owner-kept archives must be moved outside ephemeral roots or pinned explicitly.
Otherwise they become TTL-eligible after threshold.

## Machine-Readable Anchor

- `workspace_config/EPHEMERAL_BUNDLE_TTL_CONTRACT.json`

## Tooling Anchor

- `scripts/ttl_bundle_janitor.py`

