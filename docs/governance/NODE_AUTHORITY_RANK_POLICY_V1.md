# NODE_AUTHORITY_RANK_POLICY_V1

Status:
- policy_version: `v1.rewritten_for_status_model_v2`
- scope: `machine rank identity and claim boundaries`
- enforcement_anchor: `scripts/validation/detect_node_rank.py`

## 1) Rank Ladder (Canonical)

1. `ASTARTES` = valid full repo copy (1:1 working copy anchor) only.
2. `PRIMARCH` = valid full repo copy + valid owner-issued offline genome bundle.
3. `EMPEROR` = valid full repo copy + valid local sovereign substrate.

Hard boundaries:
1. `EMPEROR` does not depend on genome bundle.
2. `EMPEROR` does not depend on creator authority marker.
3. full repo copy alone never elevates to `PRIMARCH` or `EMPEROR`.

## 2) Rank Resolution Order

1. repo copy valid + local sovereign substrate valid -> `EMPEROR`
2. repo copy valid + genome bundle valid -> `PRIMARCH`
3. repo copy valid only -> `ASTARTES`
4. invalid/partial repo copy evidence -> `UNKNOWN` fail-closed

Disambiguation rule:
1. repo copy + genome + substrate -> `EMPEROR` because substrate is decisive;
2. this is not a second genome path to `EMPEROR`.

## 2.1) Rank-Derived Machine Mode Mapping

1. `EMPEROR -> creator`
2. `PRIMARCH -> helper(high)`
3. `ASTARTES -> helper(low)`
4. `integration` is intent/posture overlay only, never a rank and never an authority source.

## 3) Capability Boundaries

### EMPEROR
Can:
1. assert sovereign claim classes;
2. issue genome bundles;
3. execute sovereign constitutional mutation path.

Cannot:
1. transfer sovereign substrate by tracked repo/mirror/network bundle;
2. bypass constitutional fail-closed gates.

### PRIMARCH
Can:
1. assert `primarch_rank_claim`;
2. execute bounded non-sovereign proposal/report classes;
3. operate under delegated envelopes.

Cannot:
1. assert `emperor_rank_claim`;
2. issue sovereign policy changes;
3. issue sovereign constitutional mutation;
4. issue genome bundles.

### ASTARTES
Can:
1. execute bounded helper/integration tasks;
2. publish bounded execution/report claims.

Cannot:
1. assert `primarch_rank_claim`;
2. assert `emperor_rank_claim`;
3. issue sovereign classes.

## 4) Load-Bearing Inputs by Rank

1. repo copy anchors: `workspace_config/status_model_v2_contract.json`
2. genome bundle contract: `workspace_config/genome_bundle_contract.json`
3. local sovereign substrate contract: `workspace_config/emperor_local_proof_contract.json`

Compatibility-only surface:
1. `creator authority` marker is deprecated compatibility telemetry, not a load-bearing authority source.

## 5) Safe Mirror and Portable Constraint

1. `WorkFLOW2/safe_mirror` is non-sovereign and non-elevating.
2. portable/import/metadata-only manifests cannot elevate to `PRIMARCH` or `EMPEROR`.
3. absent local sovereign substrate always excludes `EMPEROR`.
