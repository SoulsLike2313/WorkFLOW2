# ISSUER_IDENTITY_AND_SIGNATURE_DISCIPLINE_V1

Status:
- policy_version: `v1`
- scope: `minimum viable issuer identity and signature discipline`
- stage: `pre-sovereign hardening without heavy PKI`

## 1) Issuer Identity Definition

`issuer_identity` is a stable identifier bound to the issuing node/operator context for an authority-bearing document.

Minimum components:
1. issuer rank claim (`issuer_rank`);
2. issuer node identity (`originating_node`);
3. issuer identity token (`issuer_identity` string);
4. verification status (`issuer_identity_status`).

## 2) Why Metadata-Only Identity Is Insufficient

Metadata-only identity is insufficient because it is:
1. easy to self-assert without independent binding;
2. vulnerable to replay or copy-with-edit;
3. ambiguous under multi-machine handoff if not tied to document structure and verifier scope.

## 3) Minimum Viable Signature Discipline (Current Stage)

Without heavy PKI, require:
1. stable `document_id` and `document_hash` fields;
2. explicit `signature_status` and `signature_assurance` class;
3. issuer identity status (`verified|invalid|unknown`);
4. verifier scope declaration (`local_runtime|locally_verifiable|emperor_local_only`);
5. fail-closed denial for unknown/insufficient states on elevated claim classes.

## 4) Signature Assurance Classes

Signature assurance classes:
1. `unsigned`
2. `self_asserted`
3. `structurally_bound`
4. `locally_verifiable`
5. `emperor_local_only_verifiable`
6. `unknown`

Interpretation:
1. `unsigned`: no binding; authority expansion denied.
2. `self_asserted`: claim exists but no strong local verifier.
3. `structurally_bound`: document hash/id binding present and internally consistent.
4. `locally_verifiable`: local verifier confirms binding and issuer context.
5. `emperor_local_only_verifiable`: requires Emperor-local proof domain to verify.
6. `unknown`: treat as unresolved and narrow authority.

## 5) Required Identity/Signature Coverage

Documents that must carry identity/signature fields:
1. warrant;
2. charter;
3. sovereign directive/edict;
4. reintegration proposal;
5. engineering directive proposal;
6. strategic return memo;
7. execution report;
8. task return dossier;
9. bounded completion report.
10. genome;
11. gramota;
12. assignment_binding.

Triad signature class baseline:
1. genome -> `genome_status_signature`
2. gramota -> `gramota_directive_signature`
3. assignment_binding -> `assignment_binding_signature`

## 6) Required Behavior by Claim Sensitivity

1. sovereign claim classes require at least `locally_verifiable` assurance and `signature_status=valid`, `issuer_identity_status=verified`.
2. bounded engineering proposals require at least `structurally_bound` assurance.
3. execution reports require at least non-`unsigned` assurance; unknown assurance narrows to deny in authority-bearing contexts.
4. assignment-binding requires at least `locally_verifiable` assurance.
5. unknown signature/identity state never expands authority.

## 7) Emperor-Local-Only Checks

Must be validated on Emperor machine:
1. emperor-local-only verifiable signature assumptions;
2. binding between issuer identity and sovereign acceptance authority;
3. final acceptance of authority-bearing documents affecting canonical truth.
4. genome bundle issuance authority claims (`genome_bundle_issuance_claim`) where relevant.

## 8) What Is Achievable Now (Without Heavy PKI)

Can enforce now:
1. strict field presence and enums;
2. assurance class gating by claim class;
3. fail-closed denial for unknown/invalid identity/signature states;
4. explicit separation of proposal-grade vs sovereign-grade admissibility.

Not fully achievable now:
1. cross-node cryptographic trust chain;
2. non-replay guarantees with globally trusted key infrastructure;
3. autonomous sovereign verification without Emperor-local checks.

## 9) Fail-Closed Rule

If any of `issuer_rank`, `issuer_identity`, `signature_status`, `signature_assurance`, `issuer_identity_status` is missing/unknown in authority-bearing context, claim scope narrows (deny elevation).

Local sovereign substrate boundary:
1. signature metadata alone never substitutes `local_sovereign_substrate`;
2. Emperor elevation still requires local substrate proof contract pass.
