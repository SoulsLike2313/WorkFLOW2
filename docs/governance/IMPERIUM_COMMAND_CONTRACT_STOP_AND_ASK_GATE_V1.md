# IMPERIUM_COMMAND_CONTRACT_STOP_AND_ASK_GATE_V1

Status:
- class: `foundation_enforcement_gate`
- mutability: `immutable_by_default`
- change_authority: `EMPEROR_ONLY`
- implementation_state: `active_contract_gate`

Purpose:
- block silent drift from ambiguous commands.
- enforce stop-and-ask behavior before risky execution.

Required fields:
1. `intent`
2. `scope`
3. `must_preserve`
4. `unknowns`
5. `assumptions`
6. `stop_triggers`
7. `acceptance_criteria`
8. `risk_cost_estimate`
9. `escalation_rule`

Gate states:
1. `GREEN`: all required fields present, unknown pressure low.
2. `AMBER`: required fields present, but unknown/assumption pressure elevated.
3. `RED_BLOCK`: critical missing fields or explicit stop trigger reached.

Stop-and-ask law:
1. `RED_BLOCK` => execution must stop and request owner decision.
2. `AMBER` => execution allowed only in bounded low-risk scope.
3. `GREEN` => execution allowed for declared scope only.

Integration:
1. Administratum owns contract quality.
2. Mechanicus can raise readiness-based stop escalation.
3. Custodes can hard block foundation-touching tasks.
