# SOVEREIGN_RANK_PROOF_MODEL_V1

Status:
- policy_version: `v1.rewritten_for_status_model_v2`
- scope: `machine-enforced rank proof chain`
- design_rule: `fail-closed rank narrowing`

## 1) Rank Classes

1. `EMPEROR`
2. `PRIMARCH`
3. `ASTARTES`
4. `UNKNOWN`

## 2) Proof Inputs

### Repo-copy input (required for all ranks)
1. anchor files and workspace slug checks from `workspace_config/status_model_v2_contract.json`.

### Primarch input
1. valid genome bundle per `workspace_config/genome_bundle_contract.json`.

### Emperor input
1. valid local sovereign substrate per `workspace_config/emperor_local_proof_contract.json`.

## 3) Non-Inputs (Forbidden Shortcuts)

1. creator marker is not load-bearing for Emperor proof;
2. genome bundle is not Emperor proof;
3. safe mirror parity is not sovereign proof;
4. metadata-only manifests are not sovereign proof;
5. portable/import bundles are not sovereign proof.

## 4) Resolution Semantics

1. Emperor path has highest priority when both Primarch and Emperor materials exist.
2. Primarch path does not block Emperor path.
3. partial/invalid artifacts always downgrade.

## 5) Downgrade Behavior

1. missing local sovereign substrate -> never `EMPEROR`.
2. missing genome bundle -> never `PRIMARCH`.
3. invalid repo-copy anchors -> `UNKNOWN` fail-closed.

## 6) Export/Leakage Boundary

1. local sovereign substrate raw contents are local-only and non-exportable by default.
2. exported bundles may include only safe-equivalent contracts/reports.
3. proof of Emperor is surfaced as validator result, not raw substrate payload.

## 7) Compatibility Layer

`creator authority` remains:
1. compatibility metadata/telemetry surface only;
2. optional migration signal in diagnostics.

It is no longer a required proof input for `EMPEROR` and no longer a load-bearing machine-mode source.
