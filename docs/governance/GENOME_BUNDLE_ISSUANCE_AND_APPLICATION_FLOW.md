# GENOME_BUNDLE_ISSUANCE_AND_APPLICATION_FLOW

Status:
- flow_version: `v1`
- scope: `manual offline genome bundle lifecycle`

## A) Issuance (EMPEROR machine only)

1. verify node rank resolves to `EMPEROR`;
2. prepare genome bundle marker per `workspace_config/genome_bundle_contract.json`;
3. set grant scope strictly to `PRIMARCH`;
4. sign/store bundle in owner-controlled offline media.

## B) Transfer

1. transfer bundle manually (offline medium);
2. do not use safe mirror, import pipeline, or network transport as sovereign path.

## C) Application (target machine)

1. ensure full repo-copy anchors are valid;
2. place bundle in local directory outside repo root;
3. set `CVVCODEX_PRIMARCH_GENOME_BUNDLE_DIR` to that directory;
4. run rank detection validator;
5. confirm `detected_rank=PRIMARCH` and no sovereign elevation.

## D) Rejection Cases

1. marker parse/field/binding mismatch;
2. forbidden origin path;
3. explicit Emperor-grant booleans not false;
4. missing repo-copy anchors.
