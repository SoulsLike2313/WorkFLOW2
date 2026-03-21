# GENOME_BUNDLE_SPEC

Status:
- spec_version: `v1`
- scope: `owner-issued offline Primarch elevation bundle`

## 1) Definition

Genome bundle is a manual offline authority package that can elevate a valid repo-copy node from `ASTARTES` to `PRIMARCH`.

## 2) Core Properties

1. issued only by EMPEROR authority;
2. applies only to machine with valid repo-copy anchors;
3. grants PRIMARCH-grade non-sovereign authority only;
4. never grants EMPEROR.

## 3) Canonical Contract

`workspace_config/genome_bundle_contract.json` defines:
1. env hook;
2. marker filename;
3. required fields/literals/booleans;
4. root binding;
5. forbidden origin zones.

## 4) Validation Inputs

1. bundle directory path from env var;
2. marker parse and schema checks;
3. explicit `granted_rank=PRIMARCH`;
4. explicit `grants_emperor_authority=false`.

## 5) Output Semantics

1. VALID genome bundle + valid repo-copy anchors -> PRIMARCH path available;
2. invalid/absent genome bundle -> fallback to ASTARTES (or lower if repo invalid).
