# GRAMOTA_DOCTRINE_V1

Status:
- doctrine_version: `v1`
- doctrine_layer: `will`
- scope: `Emperor will/order mandate document`

## 1) Definition

`Gramota` is a document of Emperor will.
It carries order/mandate/tasking/signoff-bearing directive intent.

## 2) What Gramota Does

1. Issues explicit directive intent from Emperor authority.
2. Marks command/tasking/signoff path for execution lanes.
3. Can define delegated bounds for downstream execution.

## 3) What Gramota Does Not Do

1. Does not grant status by itself (not a Genome).
2. Does not equal appointment/assignment binding by itself.
3. Does not bypass constitutional/rank fail-closed gates.

## 4) Issuer and Signature Discipline

1. Issuer rank: `EMPEROR` (direct will document).
2. Signature class: `gramota_directive_signature`.
3. Minimum assurance:
   - `locally_verifiable` for operational directive;
   - `emperor_local_only_verifiable` for sovereign-sensitive directives.

## 5) Required Distinguishers

A valid Gramota must be explicitly markable:
1. `document_type=gramota`
2. `document_role_layer=will`
3. `issuer_rank=EMPEROR`
4. `directive_kind in {order, mandate, tasking, signoff}`
5. `tasking_marker=true` when it carries execution tasking.

Hard rule:
- Emperor tasking must be explicitly marked as Gramota (`document_type=gramota` + `tasking_marker=true`).

## 6) Legacy Mapping

`edict` is treated as a tolerated legacy class alias for Emperor sovereign directive intent.
Canonical class for this doctrine is `gramota`.
