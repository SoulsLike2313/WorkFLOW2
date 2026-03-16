# SELF VERIFICATION POLICY

Policy class: Level 2 control policy (bounded by Level 0 first principles).

Authority inputs:

- `docs/governance/FIRST_PRINCIPLES.md`
- `docs/governance/GOVERNANCE_HIERARCHY.md`
- `docs/governance/GOVERNANCE_GAP_AUDIT.md`

## 1) Mandatory falsification rule

Before any completion claim, the executor must attempt to disprove its own result.

Required behavior:

1. run positive-path validation
2. run contradiction checks against canonical sources
3. run failure-path checks for critical gates
4. only then issue verdict

## 2) When self-check is mandatory

Self-check is mandatory for:

1. any code/config/document change in tracked state
2. any sync/completion claim
3. any manifest/report generation
4. any policy/governance update
5. any exported artifact marked safe for external reading

## 3) Required self-check scope

Minimum required checks:

1. git integrity:
   - `git status --short --branch`
   - `git rev-parse HEAD`
   - `git rev-parse safe_mirror/main`
   - `git rev-list --left-right --count HEAD...safe_mirror/main`
2. sync gate:
   - `python scripts/check_repo_sync.py --remote safe_mirror --branch main`
3. contradiction gate:
   - compare `README.md`, manifests, and governance policy for canonical consistency
4. artifact integrity:
   - required outputs exist at declared paths
   - generated manifests/reports match current state assumptions
5. safety gate (if export/public-facing safe artifact involved):
   - blocked categories not included
   - secret-pattern checks show no critical hit

## 4) PASS-prohibited conditions

PASS is forbidden if any is true:

1. unresolved critical contradiction exists
2. worktree is not clean at completion boundary
3. `HEAD != safe_mirror/main` or divergence not `0/0`
4. required output file is missing
5. required validation step was not executed
6. stale artifact is used as canonical truth
7. blocker is present but not explicitly declared

## 5) Required output of self-verification

Every self-check cycle must produce explicit status lines:

1. findings
2. fixes (if any)
3. current status
4. head SHA
5. divergence
6. final PASS/FAIL verdict

If defect is found:

1. fix defect
2. rerun all affected checks
3. only then emit final verdict

## 6) First-principles linkage

This policy operationalizes:

1. `Truth First Law` (claims must be verified)
2. `Sync Integrity Law` (no completion without mirror parity)
3. `Self-Verification Law` (mandatory falsification attempt)
4. `No Cosmetic Progress Law` (no PASS without operational proof)

