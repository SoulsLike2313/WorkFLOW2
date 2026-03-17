# WORKFLOW2_CANONICAL_VOCABULARY_V1

## Scope
Canonical vocabulary freeze for Constitution-first phase. Terms below are normative for governance/query/command/task-program/mission surfaces.

## Terms

### `mission`
- definition: bounded work package with explicit scope, non-goals, program plan, checkpoints, and acceptance criteria.
- what it is not: not an open-ended initiative and not free-form planning.
- allowed usage notes: use only for mission-layer units routed via `operator_mission_surface`.
- related states/dependencies: depends on authority/policy/preconditions; may end as `CERTIFIED`, `BLOCKED`, `FAILED`, or `PARTIAL`.

### `program`
- definition: deterministic multi-step execution unit used by mission layer.
- what it is not: not a product feature, and not a mission-level acceptance object.
- allowed usage notes: must come from task/program registry and execute via program surface.
- related states/dependencies: checkpointed; may be resumed per contract.

### `task`
- definition: scoped execution request mapped to command/program/mission surfaces.
- what it is not: not implicit permission to change architecture or authority model.
- allowed usage notes: must have bounded scope and admission-compatible contract.
- related states/dependencies: routed by policy and accepted scope.

### `command`
- definition: controlled single operator action with explicit preconditions and expected outputs.
- what it is not: not an autonomous workflow.
- allowed usage notes: use command class names and execution contract vocabulary.
- related states/dependencies: authority-aware and policy-gated.

### `artifact`
- definition: repo-visible file output produced by execution/review/reporting.
- what it is not: not a verbal claim.
- allowed usage notes: artifact paths must be explicit in reports/manifests.
- related states/dependencies: can participate in evidence chains.

### `evidence`
- definition: sufficient artifact set that verifies a claim or decision.
- what it is not: not a narrative summary without traceable outputs.
- allowed usage notes: evidence must be linkable to runtime reports, manifests, and checks.
- related states/dependencies: required for certification and completion claims.

### `decision`
- definition: explicit accepted/rejected determination with policy basis and evidence.
- what it is not: not an implicit preference.
- allowed usage notes: decisions must name gates/verdicts that were used.
- related states/dependencies: consumes evidence; produces acceptance status.

### `review`
- definition: structured evaluation of artifacts/evidence against policy contracts.
- what it is not: not an informal opinion pass.
- allowed usage notes: review outcome must be represented as decision/verdict.
- related states/dependencies: feeds certification and admission status.

### `certification`
- definition: formal statement that required acceptance criteria and gates are satisfied.
- what it is not: not “looks good”.
- allowed usage notes: requires creator-authorized completion path where policy demands it.
- related states/dependencies: depends on evidence completeness and clean sync discipline.

### `source of truth`
- definition: highest-precedence canonical source applicable to a claim.
- what it is not: not whichever file was edited last.
- allowed usage notes: precedence is governed by canonical source policies and manifests.
- related states/dependencies: contradiction resolution relies on this term.

### `runtime state`
- definition: generated machine-readable execution state (status/checkpoints/history/reports).
- what it is not: not policy authority by itself.
- allowed usage notes: runtime outputs are evidence surfaces, not constitutional overrides.
- related states/dependencies: used by verification and bundle exports.

### `completion`
- definition: gated terminal state where required outputs exist, checks pass, and sync is explicit.
- what it is not: not progress.
- allowed usage notes: never claim completion with unresolved blockers.
- related states/dependencies: requires authority + policy + evidence + sync parity.

### `accepted`
- definition: decision state where requested scope is approved for execution or baseline use.
- what it is not: not certification by default.
- allowed usage notes: use for phase/layer acceptance only when gate criteria are explicit.
- related states/dependencies: may precede `certified`.

### `certified`
- definition: accepted state with completed evidence chain and required gates.
- what it is not: not provisional acceptance.
- allowed usage notes: use for baseline-ready claims only with proof outputs.
- related states/dependencies: strongest accepted state before supersession.

### `stale`
- definition: claim/artifact whose content is outdated relative to newer canonical evidence.
- what it is not: not necessarily false historically.
- allowed usage notes: mark explicitly; stale claims cannot be used for completion.
- related states/dependencies: produced by contradiction/source-precedence resolution.

### `superseded`
- definition: prior accepted/certified item replaced by newer accepted canonical item.
- what it is not: not unresolved contradiction.
- allowed usage notes: keep for history; remove from active routing.
- related states/dependencies: follows explicit phase transition or baseline update.

### `rejected`
- definition: denied state caused by failed authority/policy/preconditions/sync/admission.
- what it is not: not pending.
- allowed usage notes: rejection reason must be explicit and machine-readable.
- related states/dependencies: may require escalation or corrective run before retry.

### `unknown`
- definition: insufficient evidence to classify a claim under canonical states.
- what it is not: not a pass/fail result.
- allowed usage notes: unknown must trigger evidence request, not assumption.
- related states/dependencies: transitions to fact/decision only after evidence capture.

## Usage Constraint
- One term must map to one meaning across README/REPO_MAP/MACHINE_CONTEXT/INSTRUCTION_INDEX/manifests/registries/contracts.
- Narrative aliases are allowed only if they preserve frozen term meaning.
