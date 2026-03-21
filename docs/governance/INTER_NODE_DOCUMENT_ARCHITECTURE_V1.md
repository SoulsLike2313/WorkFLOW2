# INTER_NODE_DOCUMENT_ARCHITECTURE_V1

Status:
- architecture_version: `v1`
- scope: `rank-bound inter-node authority documents`
- note: `lightweight enforceable stage; no heavy PKI rollout`

## 1) Authority Document Classes

### A) Emperor-issued

1. `warrant`
2. `charter`
3. `gramota` (order/mandate/tasking/signoff-bearing directive)
4. `genome` (Primarch status attestation)
5. `assignment_binding` (sovereign assignment/binding document)

### B) Primarch-issued

1. `reintegration_proposal`
2. `engineering_directive_proposal`
3. `strategic_return_memo`
4. `assignment_binding` (delegated only when Emperor envelope explicitly allows)

### C) Astartes-issued

1. `execution_report`
2. `task_return_dossier`
3. `bounded_completion_report`

## 2) Class Matrix

| class | issuer_rank | allowed_recipients | authority type | can trigger reintegration | portable travel | sovereign claim allowed |
|---|---|---|---|---|---|---|
| warrant | EMPEROR (or delegated PRIMARCH when charter allows) | PRIMARCH, ASTARTES | delegated execution authority | yes | yes | no |
| charter | EMPEROR | PRIMARCH, ASTARTES | operating envelope | yes | yes | no |
| gramota | EMPEROR | PRIMARCH, ASTARTES | order/mandate/tasking/signoff directive | yes | controlled | yes (Emperor only by claim class) |
| genome | EMPEROR | PRIMARCH | status attestation | no (status by itself) | controlled | no |
| assignment_binding | EMPEROR or delegated PRIMARCH | PRIMARCH, ASTARTES | appointment/delegation binding | yes | controlled | no (binding is non-sovereign by itself) |
| reintegration_proposal | PRIMARCH | EMPEROR | proposal | yes | yes | no |
| engineering_directive_proposal | PRIMARCH | EMPEROR | proposal | yes | yes | no |
| strategic_return_memo | PRIMARCH | EMPEROR | recommendation | yes | yes | no |
| execution_report | ASTARTES | PRIMARCH, EMPEROR | bounded reporting | yes | yes | no |
| task_return_dossier | ASTARTES | PRIMARCH, EMPEROR | bounded reporting | yes | yes | no |
| bounded_completion_report | ASTARTES | PRIMARCH, EMPEROR | bounded reporting | yes | yes | no |

## 3) Global Validity Preconditions

Document is authority-bearing only when all pass:
1. schema required fields are present;
2. issuer rank and claim class are compatible;
3. `lifecycle_status=valid`;
4. signature/identity fields satisfy claim sensitivity (`signature_status`, `signature_assurance`, `issuer_identity_status`);
5. canonical root context aligns with `E:\CVVCODEX` for sovereign-sensitive evaluation;
6. for Astartes execution claims, at least one of `warrant_status` or `charter_status` is `valid`.

## 4) What Each Rank Cannot Claim

1. Primarch cannot assert sovereign acceptance, Emperor rank, or unrestricted structural mutation rights.
2. Astartes cannot claim creator-grade sovereignty or initiate sovereign policy changes.
3. Portable/safe mirror copies cannot upgrade authority class.

## 4.1) Status/Will/Binding Distinction

1. `genome` = status layer (Primarch attestation), not order/tasking.
2. `gramota` = will/order layer, not status attestation.
3. `assignment_binding` = responsibility/delegation binding layer, not status and not direct Emperor order substitute.
4. Direct Emperor `gramota` has priority over delegated binding/order in conflicts.

## 5) Safe Mirror and Root Context

1. `WorkFLOW2` mirror is informational/orientation surface only.
2. Mirror presence never acts as sovereign proof or authority source.
3. canonical root mismatch narrows admissibility and blocks sovereign elevation.

## 6) Signature and Verification Scope

1. every authority-bearing class must carry signature status and assurance class;
2. sovereign-sensitive acceptance may require `emperor_local_only_verifiable` assurance;
3. metadata-only fields do not constitute sovereign-grade proof.

## 7) Canonical Triad Contract

Canonical machine-readable distinction contract:
- `workspace_config/genome_gramota_assignment_binding_contract.json`

Doctrinal anchors:
1. `docs/governance/GENOME_DOCTRINE_V1.md`
2. `docs/governance/GRAMOTA_DOCTRINE_V1.md`
3. `docs/governance/ASSIGNMENT_BINDING_DOCTRINE_V1.md`
