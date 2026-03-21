# CREATOR_AUTHORITY_POLICY

## Purpose

Define treatment of legacy creator-authority marker under rank-derived mode model v2.

## Scope Classification

1. `creator authority` marker is a `LEGACY` compatibility telemetry surface.
2. `creator authority` marker is `DEPRECATED` as a source of machine mode.
3. `creator authority` marker is **not** load-bearing for EMPEROR rank.
4. `creator authority` marker is **not** load-bearing for creator mode.
5. Creator mode must be derived only from rank model v2 (`EMPEROR -> creator`).

## Canonical Detection Contract

- env var name: `CVVCODEX_CREATOR_AUTHORITY_DIR`
- marker filename: `creator_authority.json`
- required marker fields:
  - `authority_mode = "creator"`
  - `profile_version = "v1"`
  - `machine_role = "canonical_creator_machine"`

## What Creator Authority Can Do (Compatibility Only)

1. provide backward-compatibility telemetry for legacy scripts;
2. support migration checks and historical diagnostics.

## What Creator Authority Cannot Do

1. cannot produce creator mode without EMPEROR rank;
2. cannot elevate ASTARTES to PRIMARCH;
3. cannot elevate PRIMARCH to EMPEROR;
4. cannot act as sovereign local substrate;
5. cannot replace rank proof contracts.

## Mandatory Mapping (Rank-Derived)

1. `EMPEROR -> creator`
2. `PRIMARCH -> helper(high)`
3. `ASTARTES -> helper(low)`
4. `integration` is posture/intent overlay only and never an authority source.

## Deprecation Note

Any surface treating creator marker as a required authority source is deprecated and must be rewritten to rank-derived mode v2.
