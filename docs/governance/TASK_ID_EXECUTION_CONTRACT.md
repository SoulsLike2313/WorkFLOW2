# Task ID Execution Contract

## Purpose

Define deterministic block-task execution model for helper nodes.

## Task ID Format

- canonical regex: `^TASK-[A-Z0-9_]+-[0-9]{3}$`
- task source: `tasks/registry/*.json`

## Required Task Fields

- `task_id`
- `title`
- `target_scope`
- `allowed_paths`
- `forbidden_paths`
- `required_outputs`
- `required_checks`
- `handoff_target`
- `non_goals`

## Execution Boundaries

- helper must execute only within `allowed_paths`
- any touched `forbidden_paths` is contract violation
- missing required outputs/checks is incomplete block

## Delivery Rules

- helper does not merge directly
- helper prepares handoff package per `EXTERNAL_BLOCK_HANDOFF_POLICY.md`
- canonical machine reviews via integration inbox flow

