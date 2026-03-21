# PRIMARCH_ISSUANCE_AND_TRANSFER_MANUAL

Status:
- manual_version: `v1`
- scope: `owner-issued offline Primarch elevation via genome bundle`

## Issuance (source EMPEROR machine)

1. confirm source rank is `EMPEROR`;
2. issue genome marker per `workspace_config/genome_bundle_contract.json`;
3. verify marker explicitly sets:
   - `granted_rank=PRIMARCH`
   - `grants_emperor_authority=false`.

## Transfer

1. transfer genome bundle offline by owner;
2. transfer full repo copy 1:1 to target machine.

## Application (target machine)

1. place genome bundle directory outside repo;
2. set `CVVCODEX_PRIMARCH_GENOME_BUNDLE_DIR`;
3. run rank detection;
4. expected result: `PRIMARCH`.

## Required Guard Check

Run sovereign-claim denial check for `emperor_rank_claim`:
1. expected result: deny for PRIMARCH.
