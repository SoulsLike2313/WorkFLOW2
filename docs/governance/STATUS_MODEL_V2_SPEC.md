# STATUS_MODEL_V2_SPEC

Status:
- spec_version: `v2`
- scope: `ASTARTES/PRIMARCH/EMPEROR determination and downgrade rules`
- enforcement_anchor: `scripts/validation/detect_node_rank.py`

## 1) Status Definitions

### ASTARTES
`ASTARTES` = machine has valid full repo-copy anchors and no valid elevation layer.

### PRIMARCH
`PRIMARCH` = machine has valid full repo-copy anchors + valid owner-issued genome bundle.

### EMPEROR
`EMPEROR` = machine has valid full repo-copy anchors + valid local sovereign substrate.

## 2) Required Proof Inputs

1. repo-copy anchors from `workspace_config/status_model_v2_contract.json`
2. genome bundle checks from `workspace_config/genome_bundle_contract.json`
3. local substrate checks from `workspace_config/emperor_local_proof_contract.json`

## 3) Forbidden Shortcuts

1. repo copy alone cannot elevate beyond ASTARTES;
2. creator marker cannot elevate to EMPEROR;
3. genome bundle cannot elevate to EMPEROR;
4. safe mirror/portable/import/metadata-only surfaces cannot elevate rank.

## 4) Downgrade Behavior

1. missing local substrate => no EMPEROR;
2. missing genome bundle => no PRIMARCH;
3. invalid repo-copy anchors => UNKNOWN fail-closed;
4. invalid partial materials always downgrade to lower valid rank.

## 5) Portable vs Local-Only

Portable:
1. repo copy;
2. genome bundle (offline manual transfer).

Local-only:
1. sovereign substrate raw files;
2. local authority root and possession/continuity markers.

Owner-manual only:
1. genome issuance and transfer;
2. sovereign substrate transfer.

Must never be exported:
1. local sovereign substrate raw contents;
2. local authority root internals;
3. any secret that could recreate EMPEROR status remotely.

## 6) WHY FULL REPO COPY IS NOT ENOUGH

Repo copy can be cloned, mirrored, archived, or imported.
Therefore repo copy alone has no sovereign uniqueness and cannot prove higher authority.

## 7) WHY EMPEROR DOES NOT NEED GENOME

Genome is a PRIMARCH attestation mechanism.
EMPEROR is proven by sovereign local substrate, which is a separate higher layer.

## 8) WHY GENOME EXISTS ONLY FOR PRIMARCH ELEVATION

Genome allows owner-issued offline grant of director-grade authority without exposing sovereign root.
Its contract explicitly forbids Emperor grant semantics.

## 9) WHY EMPEROR DEPENDS ONLY ON LOCAL SOVEREIGN SUBSTRATE

Sovereign authority must stay local, non-tracked, and non-networked.
Only local substrate can satisfy that boundary while remaining fail-closed.

## 10) WHY ALL OF THIS MUST FAIL CLOSED

Any ambiguous/missing/partial evidence must reduce authority, not expand it.
This prevents false elevation, replay, mirror leakage, and narrative-only sovereign claims.
