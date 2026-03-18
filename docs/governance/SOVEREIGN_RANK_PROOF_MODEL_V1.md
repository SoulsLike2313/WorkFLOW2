# SOVEREIGN_RANK_PROOF_MODEL_V1

Status:
- policy_version: `v1`
- scope: `machine-enforced rank proof model`
- design_rule: `fail-closed rank narrowing`

## 1) Rank Classes

1. `EMPEROR`
2. `PRIMARCH`
3. `ASTARTES`
4. `UNKNOWN` (ambiguity/error fallback)

## 2) Emperor-Only Local Proof

Emperor requires all required proof classes:

1. valid Primarch authority path contract (creator authority contract);
2. valid canonical root context (`E:\CVVCODEX`);
3. Emperor local proof contract:
   - external proof directory;
   - valid Emperor proof marker;
   - required fields aligned with sovereign proof contract.

Supporting proof classes (recommended but not mandatory in v1 hardening):
1. local sovereign continuity evidence;
2. local issuer identity binding metadata.

## 3) Primarch-Grade Proof

Primarch requires:
1. valid creator authority contract path;
2. valid `creator_authority.json` fields;
3. canonical root context valid.

Primarch does not require Emperor-only proof and cannot inherit Emperor sovereignty by bundle copy.

## 4) Astartes / Default Fallback

Astartes is mandatory fallback when:
1. Primarch authority path is invalid;
2. canonical root context is invalid;
3. rank signals are unknown/partial/contradictory;
4. rank validator is unavailable or errored.

## 5) Required vs Supporting Proofs

Required for Emperor:
1. canonical root valid;
2. primarch authority path valid;
3. emperor proof marker valid.

Required for Primarch:
1. canonical root valid;
2. creator authority path valid.

Supporting:
1. signed inter-node document identity metadata;
2. reintegration proof chain completeness.

## 6) Proofs Excluded From Normal Portable Bundles

Must not be included in ordinary portable bundle payload:
1. Emperor local proof marker and proof directory contents;
2. local sovereign secret references;
3. any artifact that can be interpreted as sovereign transfer token.

## 7) Fail-Closed Logic

Hard rules:
1. missing Emperor proof never yields `EMPEROR`;
2. invalid Primarch authority path never yields `PRIMARCH`;
3. unknown/partial conditions narrow rank (`ASTARTES` or `UNKNOWN`);
4. leftover portable files never elevate rank;
5. safe mirror presence never elevates rank.

## 8) Relation To Creator/Helper Modes

Mode and rank are related but distinct:
1. creator/helper/integration mode controls operation surface;
2. sovereign rank controls claim authority boundaries.

Rule:
- creator-grade capability is not equal to Emperor sovereignty.

## 9) Canonical Root Confidence

`E:\CVVCODEX` validity is rank confidence anchor.

If canonical root is invalid:
1. Emperor is forbidden;
2. Primarch confidence is reduced/fallback applied;
3. claim scope must narrow.

## 10) Safe Mirror Constraint

`WorkFLOW2` safe mirror cannot be source of sovereign rank proof.

Safe mirror is orientation/export surface only and has zero sovereign proof elevation power.
