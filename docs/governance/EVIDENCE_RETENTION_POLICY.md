# EVIDENCE RETENTION POLICY

Policy class: Governance v1.1 hardening evidence control.

Authority inputs:

- `docs/governance/ADMISSION_GATE_POLICY.md`
- `docs/governance/SELF_VERIFICATION_POLICY.md`
- `docs/repo_publication_policy.md`

## 1) Evidence artifact classes

### Canonical evidence (must remain repo-visible)

1. policy and manifest source files
2. admitted review artifacts referenced by current workflow
3. safe mirror manifest/report artifacts
4. repo control runtime summaries required by admission flow

### Mandatory operational evidence (must exist for completion)

1. git parity checks
2. validation command outputs/run IDs
3. changed files list and head SHA
4. blocker register

### Temporary evidence

1. transient diagnostics not required for active truth
2. local runtime debug outputs
3. exploratory logs

Temporary evidence must not replace canonical evidence.

## 2) Retention classes

1. `HOT`: active reading path and bootstrap-critical artifacts.
2. `WARM`: evidence needed for recent audit continuity.
3. `COLD`: historical reference, non-authoritative.

## 3) Archive rules

1. move stale non-canonical artifacts out of active read order
2. mark legacy artifacts explicitly
3. keep trace link to commit/task/report id
4. never archive mandatory canonical files

## 4) Traceability requirements

Each retained evidence artifact must map to:

1. commit SHA
2. task/run ID
3. generating command/check
4. status/verdict context

## 5) Repo-visible requirements

Must stay repo-visible:

1. governance stack docs
2. canonical manifests
3. completion and sync policies
4. active safe-state references

Can be archived out of hot path:

1. stale historical review artifacts
2. superseded reports marked legacy

## 6) Forbidden evidence handling

1. deleting canonical evidence without replacement
2. reporting PASS with temporary-only evidence
3. using hidden/local-only files as completion proof