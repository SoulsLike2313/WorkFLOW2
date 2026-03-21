# RANK_DERIVED_MACHINE_MODE_SPEC

Status:
- version: `v2.0.0`
- classification: `load-bearing`
- scope: `machine mode derivation from rank model v2`

## Canonical Mapping

1. `rank=EMPEROR` -> `base_machine_mode=creator`
2. `rank=PRIMARCH` -> `base_machine_mode=helper`, `helper_tier=high`
3. `rank=ASTARTES` -> `base_machine_mode=helper`, `helper_tier=low`
4. `rank=UNKNOWN` -> fail-closed helper posture (non-authoritative)

Integration rule:
1. `integration` is `work_posture` / `intent overlay` only;
2. integration is not rank and not authority source;
3. integration never upgrades base mode or helper tier.

## Rank Resolution Dependencies (authoritative)

1. repo only -> `ASTARTES`
2. repo + genome -> `PRIMARCH`
3. repo + substrate -> `EMPEROR`
4. repo + genome + substrate -> `EMPEROR` (substrate decisive)

Hard meaning:
1. genome never produces emperor;
2. substrate path is the only emperor path;
3. creator marker is not required for emperor and not sufficient for creator.

## WHY CREATOR MUST BE RANK-DERIVED

1. removes legacy split where mode and rank can contradict each other;
2. prevents hidden creator backdoor from external marker-only surfaces;
3. aligns authority gate with sovereign proof model and fail-closed semantics.

## WHY LEGACY CREATOR AUTHORITY MUST BE DEPRECATED

1. it is external marker evidence, not sovereign proof;
2. it can exist on non-emperor contexts and would otherwise create false creator claims;
3. it is retained only for compatibility telemetry/migration diagnostics.

## WHY PRIMARCH IS HIGH-HELPER, NOT CREATOR

1. PRIMARCH is non-sovereign delegated authority in v2;
2. PRIMARCH can direct bounded proposals and execution envelopes;
3. PRIMARCH cannot perform sovereign acceptance or constitutional mutation.

## WHY ASTARTES IS LOW-HELPER

1. ASTARTES is repo-governed execution layer;
2. ASTARTES can execute bounded tasks and produce reports;
3. ASTARTES cannot claim primarch/emperor authority classes.

## WHY GENOME + SUBSTRATE DOES NOT MEAN TWO EMPEROR PATHS

1. substrate presence is decisive for emperor determination;
2. genome stays PRIMARCH-only material by contract;
3. simultaneous presence does not add a second elevation mechanism.

## Hard Guards

1. if `rank!=EMPEROR`, mode must never resolve to creator;
2. if `rank=PRIMARCH`, helper tier must be `high`;
3. if `rank=ASTARTES`, helper tier must be `low`;
4. if mapping contract is inconsistent, detector must fail-closed.
