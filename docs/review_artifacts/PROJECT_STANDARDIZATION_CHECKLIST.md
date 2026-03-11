# PROJECT_STANDARDIZATION_CHECKLIST

## Workspace-level
- [x] Workspace manifest exists and is machine-readable
- [x] Codex manifest exists and encodes analysis policy
- [x] Project rules document exists
- [x] Active project explicitly defined
- [x] Project statuses indexed

## Project-level
- [x] Every major project has PROJECT_MANIFEST.json
- [x] Manifest contract fields normalized across projects
- [x] README path declared in manifests
- [x] Entrypoints declared in manifests

## Tooling
- [x] New project generator implemented (`scripts/new_project.py`)
- [x] Workspace validator implemented (`scripts/validate_workspace.py`)
- [x] Bootstrap onboarding script implemented (`scripts/bootstrap_workspace.ps1`)
- [x] Template presets added for project types

## Verification evidence model
- [x] Verification summary includes run timing + gate + checks
- [x] test_results artifact is generated
- [x] Artifact list is explicit in verification summary
