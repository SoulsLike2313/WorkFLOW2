# External Block Handoff Policy

## Purpose

Standardize helper delivery package for canonical integration review.

## Required Handoff Package Content

- `block_id` / `task_id`
- `node_id`
- `mode` (must be `helper` for external block delivery)
- `changed_files` list
- `checks` summary
- `risks` list
- `blockers` list
- `verdict`
- `delivery_timestamp`

## Optional Content

- attachments bundle
- local logs sanitized for safe sharing

## Required Structure

- package root in `integration/inbox/<package_id>/`
- `handoff_package.json`
- `HANDOFF_REPORT.md`
- optional `attachments/`

## Hard Rules

- no direct canonical merge rights in handoff package
- no governance override in handoff package
- no creator authority assumptions in helper package

