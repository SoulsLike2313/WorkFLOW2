# Project Rules (Workspace Standard)

## Purpose
This document defines strict rules for creating and maintaining projects inside this multi-project workspace.

## Core principles
1. Every project must be machine-readable.
2. Every project must be registered in `workspace_config/workspace_manifest.json`.
3. Every registered project must contain:
   - `README.md`
   - `PROJECT_MANIFEST.json`
4. Active project status is unique and explicit.
5. Legacy/archived projects are changed only on explicit request.

## Allowed statuses
- `active`
- `supporting`
- `experimental`
- `archived`
- `legacy`

## Required fields for PROJECT_MANIFEST.json
- `name`
- `slug`
- `description`
- `status`
- `category`
- `type`
- `priority`
- `root_path`
- `readme_path`
- `main_entrypoints`
- `verification_entrypoints`
- `user_mode_entrypoint`
- `developer_mode_entrypoint`
- `update_entrypoint`
- `config_files`
- `runtime_dirs`
- `log_dirs`
- `data_dirs`
- `dependencies_file`
- `owner`
- `maturity_level`
- `tags`
- `notes`

## Project creation workflow
1. Run generator:
   - `python scripts/new_project.py`
2. Provide:
   - name
   - slug
   - status
   - type
3. Generator must create:
   - project folder
   - `README.md`
   - `PROJECT_MANIFEST.json`
   - preset structure
4. Generator must register project in `workspace_manifest.json`.
5. Run workspace validator:
   - `python scripts/validate_workspace.py`

## Validation policy
Workspace validation must fail if:
- a project is registered without a manifest,
- a project has missing required fields,
- status is invalid,
- README is missing,
- slug conflicts exist,
- unregistered project folders are detected.

## Status transition policy
- Only one `active` project is allowed.
- Promoting another project to `active` requires explicit status transition in workspace manifest.
- `legacy` and `archived` are excluded from default active analysis flow.

## Documentation policy
- Root README is workspace map.
- Project README is project-level source of truth.
- Manifests are authoritative machine-readable contracts.
