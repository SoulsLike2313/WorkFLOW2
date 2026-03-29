# DIRECTED_EVOLUTION_CANDIDATE_LEDGER_V1

Status:
- ledger_state: `ACTIVE`
- update_mode: `repo_visible_only`
- hidden_evolution: `FORBIDDEN`

## Purpose

Track all evolution candidates and decisions with explicit owner-control evidence.

## Lifecycle States

1. `CANDIDATE`
2. `ACCEPTED`
3. `REJECTED`
4. `DEFERRED`

## Record Template

- candidate_id:
- created_at_utc:
- primary_cluster_id:
- secondary_cluster_links:
- branch_scope_summary:
- intended_gain:
- non_noise_rationale:
- measurement_method:
- required_owner_gate:
- decision_status:
- decision_reason:
- owner_decision_status:
- evidence_paths:
- promotion_status:
- rollback_trigger:

## Current Registry

None yet.

## Decision Log

None yet.

## Rules

1. No candidate may be promoted if it is not present here.
2. Rejected entries cannot be silently revived.
3. Deferred entries require fresh owner decision to re-open.
4. Every accepted entry must reference exact proof/evidence path.

