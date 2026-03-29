# IMPERIUM_LAW_EVENT_CARRY_FORWARD_CANON_V1

## Status

- status: `active`
- mode: `code_first`
- owner_trigger: `remember / fix in law / add to law / pin in law`

## Event Model

Each owner law instruction becomes a `law_event` with:

1. event id
2. source phrase
3. target law layer
4. target codification surface
5. next relevant prompt injection note
6. codification state
7. evidence path

## Workflow

1. register event
2. classify target layer (`front/core/logos/servitor/shared`)
3. generate injection note for next master prompt
4. execute codification delta
5. mark event as `codified`
6. keep event visible in registry history

## Hard Rules

1. no law event remains chat-only memory
2. pending law events must appear in injection note
3. codified events must carry evidence pointer
4. stale pending events are drift risks

## Runtime Anchors

1. `runtime/administratum/IMPERIUM_LAW_EVENT_REGISTRY_V1.json`
2. `runtime/administratum/IMPERIUM_LAW_CARRY_FORWARD_STATUS_V1.json`
3. `runtime/administratum/IMPERIUM_LAW_INJECTION_NOTE_V1.md`
4. `scripts/imperium_law_event_registry.py`
