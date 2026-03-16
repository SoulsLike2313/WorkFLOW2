# CREATIVE REASONING POLICY

Policy class: Level 3 adaptive reasoning policy, constrained by Level 0-2.

Authority inputs:

- `E:\CVVCODEX\docs\governance\FIRST_PRINCIPLES.md`
- `E:\CVVCODEX\docs\governance\GOVERNANCE_HIERARCHY.md`
- `E:\CVVCODEX\docs\governance\ADMISSION_GATE_POLICY.md`
- `E:\CVVCODEX\docs\governance\ANTI_DRIFT_POLICY.md`
- `E:\CVVCODEX\docs\governance\SELF_VERIFICATION_POLICY.md`

## 1) Core rule

Creative reasoning is permitted only after engineering discipline gates are satisfied.

Precondition gates:

1. truth gate: verified facts only
2. sync gate: no broken sync/completion integrity
3. scope gate: bounded execution contract active
4. contradiction gate: no unresolved critical contradiction

If any precondition fails, creative expansion is forbidden.

## 2) Mandatory idea labels

Every non-trivial idea/proposal must be explicitly labeled as one of:

1. `CANONICAL`
2. `EXPERIMENTAL`
3. `HYPOTHESIS`
4. `RISKY IMPROVEMENT`
5. `OPTIONAL INVENTION`

Labeling rule:

- unlabeled idea is non-executable.

## 3) Fact-hypothesis separation

Hard separation required:

1. facts: verified current state only
2. hypotheses: unverified assumptions
3. proposed changes: bounded future action

Forbidden:

1. presenting hypotheses as facts
2. mixing speculative text into completion claims

## 4) Bounded invention model

Allowed creativity:

1. only within requested scope and allowed paths
2. only with explicit risk statement for non-canonical ideas
3. only with rollback/containment plan for risky changes

Forbidden creativity:

1. architecture drift hidden as "improvement"
2. side work outside task contract
3. policy bypass through creative framing

## 5) Execution gate by label

1. `CANONICAL`: executable if all gates pass.
2. `EXPERIMENTAL`: executable only with explicit experimental boundary and validation plan.
3. `HYPOTHESIS`: not directly executable; requires conversion to testable task first.
4. `RISKY IMPROVEMENT`: executable only with explicit risk acceptance, containment, and post-check.
5. `OPTIONAL INVENTION`: non-mandatory; cannot block required canonical deliverables.

## 6) Completion constraints

Completion output must:

1. separate delivered canonical result from optional ideas
2. include explicit label for each non-canonical proposal
3. never use non-canonical ideas as evidence of completed mandatory scope
