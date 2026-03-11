# WorkFLOW Multi-Project Workspace

## Overview
This repository is a strict multi-project workspace with machine-readable governance.

Primary goals:
- explicit active project selection
- isolated project scopes
- machine-verifiable manifests
- repeatable onboarding for Codex and human operators

## Workspace control plane
Canonical workspace files:
- `workspace_config/workspace_manifest.json`
- `workspace_config/codex_manifest.json`
- `workspace_config/PROJECT_RULES.md`
- `workspace_config/codex_bootstrap.md`

Operational scripts:
- `scripts/bootstrap_workspace.ps1`
- `scripts/validate_workspace.py`
- `scripts/new_project.py`

## Active project
Current active project:
- `projects/wild_hunt_command_citadel/shortform_core`

Active project docs:
- `projects/wild_hunt_command_citadel/shortform_core/README.md`
- `projects/wild_hunt_command_citadel/shortform_core/CODEX.md`
- `projects/wild_hunt_command_citadel/shortform_core/PROJECT_MANIFEST.json`

Manual testing policy:
- manual test is allowed only after verification gate `PASS`.

## Project registry model
Statuses:
- `active`
- `supporting`
- `experimental`
- `archived`
- `legacy`

Registry is authoritative in:
- `workspace_config/workspace_manifest.json` (`project_registry`)

Each registered project must contain:
- `README.md`
- `PROJECT_MANIFEST.json`

## Verification proof model
Active verification entrypoint:
```powershell
cd projects/wild_hunt_command_citadel/shortform_core
python -m app.verify
```

Expected verification artifacts:
- `runtime/verification/<run_id>/verification_summary.json`
- `runtime/verification/<run_id>/verification_summary.md`
- `runtime/verification/<run_id>/readiness_summary.json`
- `runtime/verification/<run_id>/consolidated_status.json`
- `runtime/verification/<run_id>/diagnostics_manifest.json`
- `runtime/verification/<run_id>/test_results.json`
- `runtime/verification/<run_id>/patch_application_summary.json`
- `runtime/verification/<run_id>/update_audit_summary.json`

Gate values:
- `PASS`
- `PASS_WITH_WARNINGS`
- `FAIL`

## Workspace bootstrap and validation
Bootstrap (new device / onboarding):
```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\bootstrap_workspace.ps1
```

Workspace validation:
```powershell
python scripts/validate_workspace.py
```

Validation artifacts:
- `runtime/workspace_validation/<run_id>/validation_summary.json`
- `runtime/workspace_validation/<run_id>/validation_summary.md`

## Future project standard
Create new projects only via generator:
```powershell
python scripts/new_project.py
```

Template source:
- `workspace_config/templates/project_template/`

Rules:
- `workspace_config/PROJECT_RULES.md`

## Notes
Root README is a workspace map.
Project-level implementation details remain in each project README and PROJECT_MANIFEST.
