# OPERATOR_RESPONSE_CONTRACT

## Purpose
Define stable operator-facing response structure for query-layer outputs.

## Core Contract (Mandatory)
- `request_class`
- `resolved_scope`
- `current_state`
- `authority`
- `verdict`
- `blocking_factors`
- `next_step`
- `evidence_source`

## Optional Fields (Class-Dependent)
- `capability_scope`
- `policy_basis`
- `escalation_requirement`
- `confidence_or_stability`
- `notes`

## Field Semantics
- `request_class`: normalized class from intent routing.
- `resolved_scope`: bounded interpretation scope for the query.
- `current_state`: relevant state snapshot (mode/health/gate context).
- `authority`: authority contract status and creator-rights context.
- `verdict`: class-specific decisive verdict (`*_verdict` value where applicable).
- `blocking_factors`: category/detail pair and blocking list.
- `next_step`: canonical actionable step string.
- `evidence_source`: explicit file references used as truth basis.

## Naming Discipline
- Verdict values originate from runtime gate fields and keep engineering tokens.
- `*_verdict` only for verdict fields.
- `*_status` only for layered status fields.
- Health fields remain health fields (`workspace_health`).

## Output Formats
Allowed:
- compact JSON snapshot
- compact Markdown response

Both must preserve the same contract semantics.

## Determinism Requirements
- Same request class + same runtime state -> same contract shape.
- Query wording variance must not change response shape without scope change.
- Query layer cannot emit verdict contradicting runtime truth artifacts.
