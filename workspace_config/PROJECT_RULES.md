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
6. Every project must have isolated runtime namespace and isolated port range.

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
- `runtime_namespace`
- `port_range`
- `port_mode_default`
- `service_ports`
- `runtime_paths`
- `state_paths`
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

## Port isolation policy
1. Every project must have its own default port range.
2. Default port ranges must not overlap.
3. Every service port must stay inside project range.
4. Startup must run preflight checks before launch.
5. Port fallback is allowed only in `auto` mode and only inside project range.
6. Silent fallback is forbidden.
7. `fixed` mode must fail with explicit error if required port is occupied.

## Runtime namespace policy
1. Every project must define unique `runtime_namespace`.
2. Runtime resources must be project-scoped.
3. Runtime resources include:
   - logs
   - diagnostics
   - database
   - temp
   - cache
   - update artifacts
   - verification outputs
   - workspace state
4. Cross-project runtime path sharing is forbidden.

## Startup diagnostics policy
Startup preflight must produce machine-readable diagnostics that include:
- selected ports
- occupied ports
- fallback ports
- backend base URL
- runtime namespace
- runtime paths

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
   - runtime isolation contract (namespace, range, service ports, paths)
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
- runtime namespace conflicts exist,
- port ranges overlap,
- service ports conflict or leave their range,
- runtime/state paths are invalid or non-isolated,
- unregistered project folders are detected.

## Status transition policy
- Only one `active` project is allowed.
- Promoting another project to `active` requires explicit status transition in workspace manifest.
- `legacy` and `archived` are excluded from default active analysis flow.

## Documentation policy
- Root README is workspace map.
- Project README is project-level source of truth.
- Manifests are authoritative machine-readable contracts.

## Task governance policy
1. Task intake is governed by:
   - `workspace_config/TASK_RULES.md`
   - `workspace_config/task_manifest.schema.json`
   - `workspace_config/AGENT_EXECUTION_POLICY.md`
   - `workspace_config/MACHINE_REPO_READING_RULES.md`
2. Tasks without strict parameters are not accepted.
3. Cross-project or cross-module edits are forbidden unless explicitly declared in task scope.
4. Output must match declared task artifacts only.
