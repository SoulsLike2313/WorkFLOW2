# GENOME_BUNDLE_SECURITY_BOUNDARIES

Status:
- policy_version: `v1`
- scope: `genome bundle security limits`

## Hard Boundaries

1. genome bundle is not sovereign substrate;
2. genome bundle cannot mint Emperor status;
3. genome bundle cannot authorize constitutional sovereign mutation;
4. genome bundle cannot replace local sovereign substrate checks.

## Allowed Transfer Mode

1. owner-manual offline transfer only;
2. no required network path;
3. no tracked repo storage of bundle secrets.

## Forbidden Uses

1. do not treat genome marker as Emperor proof surface;
2. do not load genome bundles from safe mirror/import staging paths;
3. do not publish raw genome issuance internals into public bundles unless sanitized.

## Required Denials

1. PRIMARCH node cannot claim `emperor_rank_claim`;
2. PRIMARCH node cannot claim `genome_bundle_issuance_claim`;
3. ASTARTES node cannot claim `primarch_rank_claim` without valid genome.
