# Tasks Registry

## Purpose

Store machine-readable block task contracts resolved by `task_id`.

## Canonical Location

- registry root: `tasks/registry/`
- each task file: JSON with required contract fields defined in `workspace_config/block_task_schema.json`

## Helper Workflow

1. resolve task: `python scripts/resolve_task_id.py --task-id <TASK_ID>`
2. execute only allowed scope
3. generate handoff package: `python scripts/prepare_handoff_package.py ...`
4. deliver package to `integration/inbox/`

