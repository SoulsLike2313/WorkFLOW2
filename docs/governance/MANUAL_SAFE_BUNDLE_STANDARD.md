# MANUAL_SAFE_BUNDLE_STANDARD

Status:
- standard_version: `v1`
- class: `canonical fallback pipeline`
- scope: `safe-mode bundle assembly when default exporter is insufficient`

## 1) Purpose

Make staged manual-safe bundle assembly a canonical standard, not an emergency workaround.

Core goal:
1. preserve safe-mode;
2. preserve evidence density;
3. preserve reading clarity;
4. preserve exclusions transparency.

## 2) Default Export Path vs Fallback Path

Default path:
1. use `scripts/export_chatgpt_bundle.py`.

Fallback path:
1. use `scripts/export_manual_safe_bundle.py` when default exporter is insufficient.

## 3) Canonical Fallback Triggers

Fallback is valid when at least one is true:
1. default exporter skips required files as `exists_but_not_tracked`;
2. requested scoped payload is safe but default exporter cannot assemble complete bundle;
3. large step requires fresh untracked artifacts in bundle;
4. operator explicitly requests manual-safe fallback.

Fallback is not a security bypass:
1. same safe-mode disallow patterns still apply;
2. protected local sovereign artifacts remain excluded.

## 4) Required Fallback Bundle Structure

Mandatory companion files inside bundle root:
1. `bundle_include_manifest.json`
2. `bundle_summary.md`
3. `bundle_reading_order.md`
4. `bundle_exclusions.md`
5. `manual_safe_export_report.md`

Payload folder:
1. `exported/<repo-relative paths...>`

## 5) Minimal Required Payload Quality

Every fallback bundle must preserve:
1. evidence density (no silent truncation of core proof surfaces),
2. reading order,
3. exclusions visibility,
4. contextual readability (index/report notes),
5. claim markings (`OBSERVED/INFERRED/NOT-PROVEN`) where applicable.

## 6) Canonical Naming and Staging Convention

Staging root:
1. `runtime/manual_safe_bundle_staging/<bundle_name>/`

Output root:
1. `runtime/chatgpt_bundle_exports/<bundle_name>.zip`

Naming pattern:
1. `<topic>_manual_safe_bundle_<timestamp_utc>`

Staging status:
1. staging is assembly workspace only (not runtime truth surface).

## 7) Safe-Mode Rules for Fallback

Must block:
1. secret-bearing files/patterns,
2. protected local sovereign substrate payloads,
3. disallowed path classes (`.env`, private keys, credentials/secrets dirs, etc.),
4. runtime paths outside explicit audit allowlist (if runtime files requested).

Must report:
1. blocked file list,
2. skipped file list,
3. exclusions note.

## 8) Operator Interpretation Rules

Fallback success means:
1. complete scoped payload assembled,
2. companion files generated,
3. safe-mode checks passed for included payload.

Fallback success does not mean:
1. global trust/sync/admission is automatically green.

## 9) Chat Completion Rule

For large tasks requiring bundle:
1. if fallback bundle not produced, status cannot be `DONE`;
2. chat response remains ultra-short and references bundle path.

## 10) Machine-Readable Anchor

Contract:
1. `workspace_config/bundle_fallback_contract.json`

Helper:
1. `scripts/export_manual_safe_bundle.py`

## 11) Canonical Invocation

```powershell
python scripts/export_manual_safe_bundle.py `
  --topic p1_bundle_acceleration `
  --include docs/governance/MANUAL_SAFE_BUNDLE_STANDARD.md workspace_config/bundle_fallback_contract.json `
  --fallback-trigger exists_but_not_tracked
```

Optional include-file mode:

```powershell
python scripts/export_manual_safe_bundle.py `
  --topic p1_bundle_acceleration `
  --include-file runtime/chatgpt_bundle_requests/request_paths.txt `
  --fallback-trigger scoped_payload_incomplete_in_default_exporter
```

## 12) Operator Success Signal

Fallback is considered normal/canonical (not аварийный), when:
1. `bundle_include_manifest.json` exists;
2. `manual_safe_export_report.md` exists;
3. required companion files are present;
4. exclusions are explicitly listed;
5. bundle zip is produced under `runtime/chatgpt_bundle_exports/`.
