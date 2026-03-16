# DEVIATION INTELLIGENCE POLICY

Policy class: Level 3 adaptive/evolution policy (bounded by Level 0-2).

Authority inputs:

- `E:\CVVCODEX\docs\governance\FIRST_PRINCIPLES.md`
- `E:\CVVCODEX\docs\governance\GOVERNANCE_HIERARCHY.md`
- `E:\CVVCODEX\docs\governance\SELF_VERIFICATION_POLICY.md`
- `E:\CVVCODEX\docs\governance\CONTRADICTION_CONTROL_POLICY.md`
- `E:\CVVCODEX\docs\governance\ADMISSION_GATE_POLICY.md`
- `E:\CVVCODEX\docs\governance\ANTI_DRIFT_POLICY.md`
- `E:\CVVCODEX\docs\governance\GOVERNANCE_GAP_AUDIT.md`

## 1) Objective

Detect, classify, and respond to deviations with evidence, root-cause linkage, and governance updates.

## 2) Deviation taxonomy

Primary classes:

1. `DRIFT`: goal/scope/architecture/doc/manifest drift.
2. `FAILURE`: gate, validation, sync, or safety failure.
3. `REPEAT_PATTERN`: same failure/drift recurring across runs/tasks.

Subtypes:

1. `TRUTH_BREACH` (fact/claim mismatch)
2. `SYNC_BREACH` (`HEAD != safe_mirror/main`, divergence not `0/0`)
3. `ADMISSION_BREACH` (completion claim with unmet gates)
4. `CONTRADICTION_BREACH` (critical unresolved contradiction)
5. `COSMETIC_BREACH` (no operational value)
6. `SCOPE_BREACH` (unrequested paths/changes)
7. `STATE_ARTIFACT_BREACH` (stale manifest/report used as current truth)

## 3) Severity model

1. `S0-CRITICAL`: truth/sync/admission contradiction that invalidates completion.
2. `S1-HIGH`: repeated major breach or unresolved major control conflict.
3. `S2-MEDIUM`: single major deviation with bounded impact.
4. `S3-LOW`: minor non-authoritative drift/noise.

Mapping rule:

- any `TRUTH_BREACH`, `SYNC_BREACH`, `ADMISSION_BREACH`, or unresolved `CONTRADICTION_BREACH` => at least `S0-CRITICAL`.

## 4) Root-cause recording contract

Each serious deviation record must include:

1. deviation id/time
2. deviation class/subtype
3. severity
4. exact evidence paths/commands
5. observed symptom
6. root cause (single primary + optional secondary)
7. affected policies/manifests/docs
8. corrective action
9. verification of fix

## 5) Evidence requirements

Minimum evidence:

1. command output proving deviation
2. exact conflicting file/path references
3. before/after state identifiers (SHA, status, divergence)
4. validation output after fix

No evidence => no deviation closure.

## 6) Policy-gap linkage

Deviation handling must classify whether issue indicates:

1. execution failure under existing policy, or
2. missing/weak policy (governance gap).

If gap is detected:

1. link to exact gap statement in `GOVERNANCE_GAP_AUDIT.md` or add new gap line in next audit cycle
2. mark required policy evolution target

## 7) Required response after serious deviation

For `S0` and `S1`:

1. immediate completion block
2. perform fix
3. rerun mandatory checks (`SELF_VERIFICATION_POLICY` + sync/admission gates)
4. register governance update need (`GOVERNANCE_EVOLUTION_POLICY`)
5. issue final verdict only after clean recheck

Serious deviation unresolved => verdict cannot be `PASS`.

