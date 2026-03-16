# ChatGPT Targeted Bundle Export

## Purpose

`scripts/export_chatgpt_bundle.py` builds a sanitized, machine-readable zip bundle for ChatGPT from local root `E:\CVVCODEX`.

This avoids exposing full repository state and keeps sharing request-scoped.

## Why This Model

1. local root is canonical for heavy prep and validation
2. GitHub `WorkFLOW` keeps approved publication-safe state
3. ChatGPT gets only targeted context/code requested for the current task
4. exporter enforces safety scan before packaging

## Modes

```powershell
python scripts/export_chatgpt_bundle.py context
python scripts/export_chatgpt_bundle.py files --include README.md REPO_MAP.md MACHINE_CONTEXT.md workspace_config/workspace_manifest.json
python scripts/export_chatgpt_bundle.py paths --include projects/platform_test_agent workspace_config docs/INSTRUCTION_INDEX.md
python scripts/export_chatgpt_bundle.py project --slug platform_test_agent
python scripts/export_chatgpt_bundle.py request --request-file chatgpt_request.txt
```

## Request Mode Workflow

1. ChatGPT sends exact file/path list.
2. User writes list to request file (`chatgpt_request.txt`).
3. Run:

```powershell
python scripts/export_chatgpt_bundle.py request --request-file chatgpt_request.txt
```

4. Exporter writes zip + manifest + report.
5. User uploads zip to ChatGPT.

Request file format:

- one repo-relative path per line
- empty lines allowed
- `#` comments allowed
- `- path` and `* path` bullet style is supported

## Safety Scan Rules

Before packaging exporter checks:

1. repo root and git state (`branch`, `tracking`, `HEAD`, `ahead/behind`, `worktree_clean`)
2. path policy (blocked categories)
3. secret-like content patterns in included files
4. mandatory context inclusion

Blocked categories include:

- `.env*`
- key/cert files (`*.pem`, `*.key`, `*.p12`, `*.pfx`)
- credentials/secrets/token-like paths
- `setup_reports/*`
- `tools/public_mirror/*`
- `runtime/*`
- logs/cache/tmp artifacts
- tunnel/router/WAN/LAN/network-trace artifacts

## Bundle Structure

Bundle filename:

- `chatgpt_bundle_<mode>_<timestamp>.zip`

Bundle contents:

- `exported/**`
- `CHATGPT_BUNDLE_MANIFEST.json`
- `EXPORT_REPORT.md`

`CHATGPT_BUNDLE_MANIFEST.json` includes:

- git/sync summary
- requested paths
- included/skipped/blocked lists
- file hashes
- active project
- safe-share verdict

`EXPORT_REPORT.md` includes:

- request summary
- included/skipped/blocked details
- reasons
- sync summary
- final verdict:
  - `SAFE TO SHARE WITH CHATGPT: YES/NO`

## Verdict Interpretation

- `SAFE TO SHARE` -> allowed for ChatGPT upload
- `RESTRICTED/BLOCKED` -> some requested items blocked by policy
- `NOT SAFE TO SHARE` -> sync/repo state failed safety requirements

## Operational Notes

- CLI-first is canonical.
- No heavy UI layer is required for this workflow.
- Export artifacts are local-only runtime outputs.
