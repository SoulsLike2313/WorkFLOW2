# INTER_NODE_DOCUMENT_SCHEMA_V1

Status:
- schema_version: `v1`
- scope: `shared machine-readable fields for inter-node documents`
- implementation_stage: `lightweight enforceable semantics, no heavy PKI`

## 1) Required Fields

1. `document_id`
2. `document_type`
3. `document_version`
4. `issuer_rank`
5. `issuer_identity`
6. `issuer_identity_status`
7. `recipient_rank`
8. `authority_scope`
9. `originating_node`
10. `intended_node`
11. `canonical_root_context`
12. `constitutional_context`
13. `base_head`
14. `created_at`
15. `scope_of_work`
16. `claim_class`
17. `attached_bundle_refs`
18. `required_checks`
19. `signature_status`
20. `signature_assurance`
21. `signature_ref`
22. `verification_scope`
23. `warrant_ref`
24. `charter_ref`
25. `warrant_status`
26. `charter_status`
27. `lifecycle_status`
28. `notes`
29. `document_role_layer`
30. `signature_class`

## 2) Field Semantics

### `document_id`
- stable unique identifier (UUID or deterministic hash id).

### `document_type`
- enum class from `INTER_NODE_DOCUMENT_ARCHITECTURE_V1.md`.

### `document_version`
- schema/document payload version for compatibility checks.

### `issuer_rank`
- enum: `EMPEROR | PRIMARCH | ASTARTES | UNKNOWN`.

### `issuer_identity`
- stable issuer token used for traceability and binding checks.

### `issuer_identity_status`
- enum: `verified | invalid | unknown`.

### `recipient_rank`
- intended recipient authority class.

### `authority_scope`
- bounded scope declaration for allowed action/claim context.

### `originating_node` / `intended_node`
- source/target node identifiers.

### `canonical_root_context`
- expected canonical root assertion; baseline `E:\CVVCODEX`.

### `constitutional_context`
- constitution version and phase context.

### `base_head`
- git anchor for provenance/replay checks.

### `created_at`
- UTC timestamp.

### `scope_of_work`
- bounded work scope summary.

### `claim_class`
- claim taxonomy key used by denial gates.

### `attached_bundle_refs`
- references to bundled artifacts (not authority proof by itself).

### `required_checks`
- checks that must pass before acting on document.

### `signature_status`
- enum: `valid | missing | invalid | unknown`.

### `signature_assurance`
- enum:
  - `unsigned`
  - `self_asserted`
  - `structurally_bound`
  - `locally_verifiable`
  - `emperor_local_only_verifiable`
  - `unknown`

### `signature_ref`
- hash/signature pointer or local verification reference.

### `verification_scope`
- enum: `local_runtime | reintegration | emperor_local_only`.

### `warrant_ref` / `charter_ref`
- linked authority document identifiers or explicit `none`/`not_required` markers.

### `warrant_status` / `charter_status`
- enum:
  - `valid`
  - `missing`
  - `invalid`
  - `expired`
  - `superseded`
  - `unknown`
  - `not_required`

### `lifecycle_status`
- document lifecycle state: `valid | invalid | expired | superseded | unknown`.

### `notes`
- contextual clarifications; never authoritative by itself.

### `document_role_layer`
- enum: `status | will | binding | proposal | report`.

### `signature_class`
- class token identifying signature semantics by document family.
- examples: `genome_status_signature`, `gramota_directive_signature`, `assignment_binding_signature`.

## 3) Validation Rules (v1)

1. missing required field -> document invalid.
2. `issuer_rank=UNKNOWN` -> fail closed for elevated claims.
3. invalid/mismatched `canonical_root_context` -> fail closed for sovereign claims.
4. sovereign claim classes require:
   - `signature_status=valid`
   - `issuer_identity_status=verified`
   - `signature_assurance in {locally_verifiable, emperor_local_only_verifiable}`.
5. bounded engineering proposals require `signature_assurance` not lower than `structurally_bound`.
6. Astartes execution claims require at least one of `warrant_status` or `charter_status` to be `valid`.
7. safe mirror presence never upgrades schema validation outcomes.

## 4) Future Compatibility

Schema is prepared for future stronger verification fields (key-id, detached signature payload, replay nonce) without changing rank/authority semantics.

## 5) Triad Conditional Fields (Genome / Gramota / Assignment-binding)

### A) `document_type=genome`
Required additional fields:
1. `status_granted_level=PRIMARCH`
2. `status_subject_identity`
3. `grant_basis`
4. `tasking_marker=false`
5. `binding_marker=false`

### B) `document_type=gramota`
Required additional fields:
1. `directive_kind in {order, mandate, tasking, signoff}`
2. `directive_priority`
3. `tasking_marker` (must be `true` for tasking directives)

### C) `document_type=assignment_binding`
Required additional fields:
1. `assigner_identity`
2. `assignee_identity`
3. `target_level`
4. `responsibility_zone`
5. `execution_domain`
6. `validity_window`
7. `revocation_authority`
8. `mutation_authority`
9. `non_override_boundaries`
