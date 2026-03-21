# ASSIGNMENT_BINDING_DOCTRINE_V1

Status:
- doctrine_version: `v1`
- doctrine_layer: `binding`
- scope: `appointment/delegation binding document`

## 1) Definition

`Assignment-binding` is a document of appointment and responsibility binding.
It records who appointed whom, to which level/scope/domain, under what validity conditions.

## 2) Binding Must Record

1. assigner identity and rank;
2. assignee identity and rank target;
3. responsibility zone;
4. department/execution domain;
5. validity window (start/end or explicit open-ended rule);
6. revocation authority;
7. mutation authority;
8. non-override boundaries.

## 3) What Assignment-binding Does

1. Binds responsibility and delegation scope.
2. Defines revocation/mutation route for assignment.
3. Constrains execution authority in declared domain.

## 4) What Assignment-binding Does Not Do

1. Does not grant Primarch status (not Genome).
2. Does not represent direct Emperor will/order tasking by itself (not Gramota).
3. Does not override constitutional or sovereign claim boundaries.
4. Does not convert non-sovereign actor into sovereign authority.

## 5) Issuer and Signature Discipline

1. Issuer:
   - `EMPEROR` for sovereign-level assignment binding;
   - `PRIMARCH` only when explicitly delegated by valid Emperor will/envelope.
2. Signature class: `assignment_binding_signature`.
3. Minimum assurance: `locally_verifiable` (higher assurance required for sovereign-sensitive scope).

## 6) Conflict / Priority Rules

When documents conflict:
1. direct Emperor Gramota has highest command priority;
2. sovereign-level assignment-binding is subordinate to direct Emperor Gramota;
3. delegated Primarch order/binding cannot override Emperor Gramota or constitutional boundary;
4. lower delegated order cannot override valid assignment-binding envelope;
5. constitutional boundary always outranks status/will/binding document conflicts.

## 7) Non-Overridable Boundaries

Assignment-binding cannot override:
1. constitutional immutability boundary;
2. Emperor-only sovereign claim classes;
3. canonical acceptance authority boundary;
4. fail-closed proof and claim-denial model.
