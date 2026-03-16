# FIRST PRINCIPLES

Immutable governance laws for this repository.

Scope:

- local development source of truth: `E:\CVVCODEX`
- public safe mirror target: `WorkFLOW2` via `safe_mirror/main`
- external machine-reading channel: targeted ChatGPT bundles

Priority:

- these laws are Level 0 and cannot be overridden by lower-level policies

## Product First Law

Short definition:

- work is valid only if it increases verified product/platform capability, integrity, or operational control

Operational meaning:

- task outputs must map to a concrete runtime, governance, safety, or audit outcome

What it forbids:

- progress claims based on wording-only changes without operational effect
- side artifacts that do not improve product/platform execution or control

What it requires:

- explicit output-to-purpose mapping
- evidence that outputs are usable in real workflow

## Truth First Law

Short definition:

- only verified facts may be presented as completed state

Operational meaning:

- any claim must be backed by file existence, command output, and current repo state

What it forbids:

- assumed checks
- stale or inferred completion claims
- masking uncertainty as certainty

What it requires:

- factual verification before reporting
- explicit statement of unknowns, failures, and blockers

## Repo Reality Law

Short definition:

- repository reality is defined by current tracked files and manifests, not by prior narrative

Operational meaning:

- machine interpretation must follow canonical manifests and current tree state

What it forbids:

- forcing repo to match outdated report text
- using historical artifacts as authority over current manifests

What it requires:

- manifest-first reconciliation
- stale artifact detection and invalidation

## Sync Integrity Law

Short definition:

- completion is invalid if local approved state is not identical to `safe_mirror/main`

Operational meaning:

- required gate: clean worktree, `HEAD == safe_mirror/main`, divergence `0/0`

What it forbids:

- completion with uncommitted changes
- completion with ahead/behind divergence
- completion without push confirmation to canonical mirror remote

What it requires:

- `git add -> git commit -> git push safe_mirror`
- sync proof in final status output

## Self-Verification Law

Short definition:

- every result must be challenged by a deliberate self-audit before final verdict

Operational meaning:

- the system must attempt to disprove its own success claims

What it forbids:

- one-pass optimistic validation
- skipping failure-path checks

What it requires:

- explicit self-audit checks (sync, policy consistency, safety boundaries, artifact validity)
- fix-and-recheck loop before PASS

## No Cosmetic Progress Law

Short definition:

- cosmetic activity is not accepted as progress without control or capability gain

Operational meaning:

- documentation changes are valid only when they resolve real contradiction, ambiguity, or governance gap

What it forbids:

- decorative rewrites
- output inflation without enforcement value

What it requires:

- measurable governance effect for non-code changes
- direct linkage between edit and risk/gap closure

## Creative Discipline Law

Short definition:

- creativity is permitted only inside strict contract boundaries

Operational meaning:

- implementation choices may vary, but scope, constraints, and acceptance gates are fixed

What it forbids:

- uncontrolled solution expansion
- architecture drift outside requested scope
- implicit policy rewrites

What it requires:

- strict contract adherence
- bounded execution with explicit do-not-do compliance
