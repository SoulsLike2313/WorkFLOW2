# OPERATOR_COMMAND_EXECUTION_CONTRACT

## Purpose
Define the mandatory execution response contract for all operator commands.

## Mandatory Fields
- `command_class`
- `resolved_action`
- `execution_scope`
- `authority_check`
- `policy_check`
- `preconditions`
- `execution_result`
- `artifacts_produced`
- `state_change`
- `blocking_factors`
- `next_step`
- `evidence_source`

## Optional Fields
- `command_id`
- `execution_mode`
- `dry_run_supported`
- `mutability_level`
- `review_requirement`
- `escalation_requirement`
- `notes`

## Required Semantics
- `authority_check`: creator/helper/integration gate + authority presence result.
- `policy_check`: policy basis list + missing policy blockers.
- `preconditions`: machine-checkable prerequisites and failures.
- `execution_result`: `SUCCESS | BLOCKED | FAILED` with summary and exit code.
- `state_change`: explicit mutation class and git-status delta tracking.
- `blocking_factors`: exact reasons preventing successful execution.
- `next_step`: deterministic remediation step.
- `evidence_source`: canonical files used for decision and report.

## Mutability Discipline
- `read_only`: no intentional state mutation.
- `guarded_state_change`: mutation allowed only with explicit guard.
- creator-only guarded operations require creator authority.

## Refusal Rules
Command execution must return `BLOCKED` (not silent skip) when:
- authority checks fail,
- policy basis is missing,
- required preconditions are not satisfied,
- required command inputs are absent.

## Consistency Rule
- Same command class + same state + same flags => same contract shape.
- Execution contract must remain compatible with query-layer and repo-control verdict chain.
