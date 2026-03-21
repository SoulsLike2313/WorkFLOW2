# WARRANT_CHARTER_LIFECYCLE_V1

Status:
- policy_version: `v1`
- scope: `warrant/charter lifecycle for rank-bound execution`
- security_posture: `fail-closed`

## 1) Definitions

### Warrant

`warrant` is a bounded execution authorization for concrete work scope, usually task/mission-level.

Minimum intent:
1. authorize specific execution action;
2. constrain path/scope/claim classes;
3. bind issuer identity, recipient rank, and validity window.

### Charter

`charter` is a broader operating envelope that defines permissible behavior class for a node/session.

Minimum intent:
1. define operating mandate and boundaries;
2. define allowed claim classes and review obligations;
3. constrain execution outside ad-hoc warrants.

## 2) Issuance and Acceptance Authority

1. `EMPEROR` may issue `warrant` and `charter`.
2. `PRIMARCH` may issue delegated bounded execution warrants only if explicit Emperor charter permits sub-delegation.
3. `ASTARTES` cannot issue sovereign authority documents.

Acceptance:
1. `PRIMARCH` accepts Emperor-issued warrants/charters for creator-grade non-sovereign operation.
2. `ASTARTES` accepts Emperor/authorized-Primarch warrants within charter limits.
3. `EMPEROR` validates all authority-bearing documents before sovereign acceptance.

## 3) Lifecycle States

Document lifecycle states:
1. `valid`
2. `invalid`
3. `expired`
4. `superseded`
5. `unknown`

State rules:
1. `valid`: required fields present, issuer/recipient/scope consistent, time window active, signature/identity status not disqualifying.
2. `invalid`: structural mismatch, issuer mismatch, forbidden scope, or denied signature/identity condition.
3. `expired`: outside validity window.
4. `superseded`: replaced by newer document with explicit supersession link.
5. `unknown`: missing evidence to establish state.

## 4) Scope Binding Rules

1. warrant/charter must include explicit `authority_scope` and `claim_class` boundaries.
2. requested execution outside scope is denied.
3. sovereign claims are never granted by warrant/charter to non-Emperor nodes.
4. canonical root mismatch (`E:\CVVCODEX` expectation violated) narrows effective scope.

## 5) Mandatory Execution Paths

Warrant/charter are mandatory for:
1. Astartes execution reports claiming authorized execution scope;
2. Astartes task-return dossiers requesting reintegration action;
3. Primarch delegated execution on behalf of Emperor policy envelope when such delegation is used;
4. any authority-bearing reintegration request that implies more than informational reporting.

## 6) Claims Forbidden Without Valid Warrant/Charter

Forbidden without valid warrant/charter:
1. Astartes execution authority claim;
2. Astartes bounded completion claim as authoritative reintegration basis;
3. delegated Primarch execution authority claim where charter requires explicit warrant;
4. any attempt to treat unsigned/unknown warrant metadata as authoritative.

## 7) Companion Requirement for Execution

1. Primarch/Astartes execution artifacts must reference active warrant/charter context via `warrant_ref`/`charter_ref` or explicit `not_required` rationale.
2. absence of required reference narrows claim class to informational-only.
3. reintegration reviewers must verify lifecycle state before accepting authority-bearing claims.

## 8) Fail-Closed Behavior

Fail-closed outcomes:
1. missing required warrant/charter -> deny authority-bearing claim;
2. invalid/expired/superseded status without replacement -> deny authority-bearing claim;
3. unknown state -> deny elevation and narrow to report-only claim scope;
4. signature/identity ambiguity on authority-bearing document -> deny sovereign-sensitive acceptance;
5. safe mirror context cannot satisfy warrant/charter authority requirements.

## 9) Lightweight Validation Contract (Current Stage)

Current lightweight validation contract:
1. runtime claim gate evaluates `warrant_status` and `charter_status` for Astartes execution claims;
2. accepted statuses for authority-bearing Astartes execution: at least one of `warrant_status` or `charter_status` is `valid`;
3. all other states are deny-by-default for that claim context.

This contract is intentionally lightweight and does not replace future stronger signature verification.

## 10) Relation To Genome / Gramota / Assignment-binding

1. warrant/charter are execution-envelope documents, not status-attestation documents.
2. `genome` is status layer and does not replace warrant/charter.
3. `gramota` is direct Emperor will/order layer and may issue tasking/signoff intent.
4. `assignment_binding` is responsibility/delegation binding layer and does not replace direct Emperor gramota.
