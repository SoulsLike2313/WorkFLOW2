# ChatGPT Targeted Bundle Export

## Canonical Role

`scripts/export_chatgpt_bundle.py` is the official external reading channel.
When tracked-only behavior is insufficient for bounded safe scope, use canonical fallback:
`scripts/export_manual_safe_bundle.py` under
`docs/governance/MANUAL_SAFE_BUNDLE_STANDARD.md`.

Architecture anchor:

- local working source: `E:\CVVCODEX`
- public safe mirror only: `WorkFLOW2` (`safe_mirror/main`)
- ChatGPT reads request-scoped safe bundles, not full repository state
- federation model: helper nodes may provide block evidence, but canonical acceptance remains creator-only

## Governance Coupling

Exporter execution must respect governance brain stack:

- `docs/governance/FIRST_PRINCIPLES.md`
- `docs/governance/GOVERNANCE_HIERARCHY.md`
- `docs/governance/SELF_VERIFICATION_POLICY.md`
- `docs/governance/ADMISSION_GATE_POLICY.md`
- `workspace_config/GITHUB_SYNC_POLICY.md`
- `workspace_config/AGENT_EXECUTION_POLICY.md`
- `docs/governance/OPERATOR_COMMAND_EXECUTION_CONTRACT.md`
- `workspace_config/operator_command_registry.json`
- `docs/governance/OPERATOR_PROGRAM_EXECUTION_CONTRACT.md`
- `workspace_config/operator_program_registry.json`

## Modes

```powershell
python scripts/export_chatgpt_bundle.py context
python scripts/export_chatgpt_bundle.py files --include README.md REPO_MAP.md MACHINE_CONTEXT.md workspace_config/workspace_manifest.json
python scripts/export_chatgpt_bundle.py paths --include projects/platform_test_agent workspace_config docs/INSTRUCTION_INDEX.md
python scripts/export_chatgpt_bundle.py project --slug platform_test_agent
python scripts/export_chatgpt_bundle.py request --request-file chatgpt_request.txt
python scripts/export_chatgpt_bundle.py audit-runtime --include-rcc-runtime
```

Manual-safe fallback mode:

```powershell
python scripts/export_manual_safe_bundle.py --topic <topic> --include <paths...> --fallback-trigger exists_but_not_tracked
```

## Canonical Workflow (ChatGPT requested files)

1. ChatGPT sends exact files/paths.
2. User provides request file or `--include` arguments.
3. Exporter validates request against safety policy.
4. Exporter generates zip + manifest + report.
5. User uploads bundle only.

Fallback workflow (when default exporter cannot include required safe files):

1. Build explicit include scope.
2. Run `scripts/export_manual_safe_bundle.py`.
3. Verify companion files:
   - `bundle_include_manifest.json`
   - `bundle_summary.md`
   - `bundle_reading_order.md`
   - `bundle_exclusions.md`
   - `manual_safe_export_report.md`
4. Upload only produced safe bundle zip.

Federated note:

- helper deliveries for integration review use `integration/inbox/` handoff packages.
- canonical creator machine decides acceptance; bundle export is reading channel, not merge authority.

## Safety Scan Requirements

Before packing, exporter must:

1. resolve git state (`branch`, `head`, `tracking`, `ahead/behind`, `worktree_clean`)
2. enforce blocked path categories
3. scan included content for sensitive patterns
4. emit explicit safe-share verdict

Blocked categories include:

- `.env*`, keys/certs, credentials, secrets
- `setup_reports/*`, `tools/public_mirror/*`
- runtime/log/cache/tmp artifacts
- WAN/LAN/tunnel/router diagnostics and configs

Audit-safe exception:

- runtime remains blocked in standard modes.
- only `audit-runtime` mode may include runtime files from explicit allowlist:
  - `workspace_config/chatgpt_audit_runtime_allowlist.json`
  - currently restricted to `runtime/repo_control_center/*` reports.
- allowlisted runtime files still pass content safety scan; unsafe content is blocked.

## Bundle Output

Archive name:

- `chatgpt_bundle_<mode>_<timestamp>.zip`
- `<topic>_manual_safe_bundle_<timestamp>.zip` (fallback standard)

Contains:

- `CHATGPT_BUNDLE_MANIFEST.json`
- `EXPORT_REPORT.md`
- exported file tree
- or fallback companion set defined in `docs/governance/MANUAL_SAFE_BUNDLE_STANDARD.md`

`CHATGPT_BUNDLE_MANIFEST.json` includes sync verdict, requested/included/skipped/blocked lists, hashes, and safe-share verdict.

`EXPORT_REPORT.md` includes requested scope, inclusion decisions, block reasons, and final line:

- `SAFE TO SHARE WITH CHATGPT: YES/NO`

## Completion Rule

Bundle task cannot be marked complete without:

- repo-visible truth for required artifacts,
- sync integrity,
- self-verification pass.

## Repo Control Center Integration

Use Repo Control Center before external sharing:

```powershell
python scripts/repo_control_center.py bundle
python scripts/repo_control_center.py full-check
```

Required condition for bundle release:

- bundle check must be `READY`
- trust/sync/governance/admission checks must not be blocked
- evolution report must not contain blocking signals for current release gate
