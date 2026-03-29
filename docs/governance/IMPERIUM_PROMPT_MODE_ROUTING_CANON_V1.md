# IMPERIUM_PROMPT_MODE_ROUTING_CANON_V1

## Status

- status: `active`
- default_mode_flow: `conditioning -> execution`

## Required Modes

1. `CONDITIONING`
- load front law
- load step anchor
- set in-scope/out-of-scope
- set output discipline and packaging discipline

2. `EXECUTION`
- execute bounded delta
- keep blocker honesty
- produce evidence-backed artifact

3. `REVIEW_ONLY`
- collect evidence without remediation

4. `FIX_ONLY`
- targeted remediation without broad redesign

5. `PACKAGING_ONLY`
- archive/transfer repair only

6. `VERIFICATION_ONLY`
- acceptance and integrity checks only

## Routing Rules

1. mode must be explicit in step anchor
2. mode shift must be recorded
3. step starts in conditioning unless owner says otherwise
4. block3 visual fronts cannot be entered from block2 step anchors

## Runtime Anchors

1. `runtime/administratum/IMPERIUM_ACTIVE_STEP_ANCHOR_V1.json`
2. `runtime/administratum/IMPERIUM_PROMPT_MODE_ROUTER_V1.json`
3. `runtime/administratum/IMPERIUM_FRONT_LAW_ACTIVE_V1.json`
