# OPERATOR_INTENT_ROUTING

## Purpose
Define deterministic mapping from operator query patterns to query classes and response contract.

## Routing Rules

| request_class | Query pattern hints | Resolved scope | Response contract focus | Canonical evidence |
| --- | --- | --- | --- | --- |
| `mode_query` | mode, режим, creator/helper/integration | machine mode identity | mode state + mode verdict | one_screen + detect_machine_mode output |
| `authority_query` | authority, права, creator authority, creator-level acceptance | authority contract state | authority + escalation requirement | one_screen + creator authority env output |
| `workspace_health_query` | health, состояние системы, workspace health, sync health | workspace technical state | workspace health + sync/trust | one_screen + repo_control_status |
| `governance_query` | governance, compliant, governance acceptance | governance chain state | governance verdict + acceptance verdict | one_screen + repo_control_status |
| `admission_query` | admission, admissible, gate open/closed | admission gate state | admission verdict + admission status | one_screen + repo_control_status |
| `capability_query` | what can, умеешь, allowed/forbidden actions | capability surface | capability scope + authority constraints | capabilities summary + federation contract |
| `blocker_query` | blocker, blocked, why fail, why warning | active blockers | blocker category + blocker detail | one_screen + repo_control_status |
| `next_step_query` | next step, что дальше, canonical step | canonical routing | next step only | one_screen + NEXT_CANONICAL_STEP |
| `policy_reference_query` | based on policy, какой policy, источник правила | policy basis | policy basis mapping | policy digest + relevant policy file |

## Determinism Constraints
- One query resolves to one dominant class.
- Multi-intent query resolves by precedence:
  1. `blocker_query`
  2. `authority_query`
  3. `admission_query`
  4. `governance_query`
  5. `workspace_health_query`
  6. `mode_query`
  7. `next_step_query`
  8. `capability_query`
  9. `policy_reference_query`
- If no pattern match: fallback to `workspace_health_query`.

## Contract Binding
All routed classes must emit the response shape from `OPERATOR_RESPONSE_CONTRACT.md`.
