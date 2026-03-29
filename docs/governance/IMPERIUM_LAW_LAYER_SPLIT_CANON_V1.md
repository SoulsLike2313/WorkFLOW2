# IMPERIUM_LAW_LAYER_SPLIT_CANON_V1

## Status

- status: `active`
- scope: `block2_and_future`
- owner_model: `emperor_final_will`

## Law Layers

1. `Front Law`
- mutable
- step-local
- stored in runtime mutable control surfaces
- may change per bounded step

2. `Core Law`
- permanent
- shared imperium constraints
- must remain stable unless owner-approved canon change

3. `Logos Canon`
- permanent
- direction/synthesis/truth-check and law carry-forward layer
- not readable by Codex

4. `Servitor Canon`
- permanent
- Codex execution boundary and output discipline layer
- readable by Logos

## Hard Separation

1. front-law mutation must not rewrite Core Law by default
2. front-law mutation must not rewrite Logos Canon by default
3. front-law mutation must not rewrite Servitor Canon by default
4. shared constraints must be explicitly duplicated into Core Law only
5. temporary step tactics belong to Front Law only

## Access Law

1. Codex cannot read Logos Canon
2. Logos can read Servitor Canon
3. shared core law remains readable across execution lanes
4. violation is a drift event and must be recorded

## Runtime Anchors

1. `runtime/administratum/IMPERIUM_LAW_LAYER_REGISTRY_V1.json`
2. `runtime/administratum/IMPERIUM_FRONT_LAW_ACTIVE_V1.json`
3. `runtime/administratum/IMPERIUM_PROMPT_MODE_ROUTER_V1.json`

## Related Surfaces

1. `docs/governance/IMPERIUM_COMMAND_CONTRACT_STOP_AND_ASK_GATE_V1.md`
2. `docs/governance/CODEX_RESULT_BLOCK_OUTPUT_LAW_V1.md`
3. `workspace_config/codex_law_access_contract.json`
