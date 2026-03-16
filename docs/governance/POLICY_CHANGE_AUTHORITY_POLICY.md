# POLICY CHANGE AUTHORITY POLICY

Policy class: Governance v1.1 hardening control.

Authority inputs:

- `docs/governance/FIRST_PRINCIPLES.md`
- `docs/governance/GOVERNANCE_HIERARCHY.md`
- `docs/governance/ADMISSION_GATE_POLICY.md`

## 1) Change authority by layer

### Level 0 (`FIRST_PRINCIPLES`)

- Automatic change: forbidden.
- Required authority: explicit owner approval in task contract.
- Mandatory review: full self-audit + contradiction scan + sync proof.

### Hierarchy (`GOVERNANCE_HIERARCHY`)

- Automatic change: forbidden.
- Required authority: explicit owner approval.
- Mandatory review: layer impact review + read-order impact review + full-check evidence.

### Control layer policies

- Automatic change: allowed only for contradiction/incident fixes with explicit task scope.
- Required authority: task-level approval with strict acceptance criteria.
- Mandatory review: self-verification + sync + admission gate proof.

### Evolution/creative layer policies

- Automatic change: allowed for evidence-backed hardening tasks.
- Required authority: strict contract with evidence target.
- Mandatory review: evolution impact check + promotion threshold compatibility.

## 2) What can be changed automatically

Allowed in ordinary execution when explicitly scoped:

1. typo fixes without semantic effect
2. missing path references in read-order/manifests
3. contradiction corrections where higher-level authority is clear
4. stale legacy marking when evidence is explicit

## 3) What requires explicit approval

1. any Level 0 change
2. any hierarchy precedence change
3. admission gate rule relaxation
4. sync/completion gate relaxation
5. promotion threshold reduction

## 4) Forbidden in ordinary task execution

1. implicit law rewrites via wording changes
2. removing mandatory checks from completion gate
3. changing source-of-truth identity without explicit architecture decision
4. changing canonical mirror target without explicit approval

## 5) Mandatory review conditions before merge/push

1. changed-file scope review
2. contradiction control check
3. `repo_control_center.py full-check`
4. `scripts/check_repo_sync.py --remote safe_mirror --branch main`
5. explicit blocker disclosure if any condition fails