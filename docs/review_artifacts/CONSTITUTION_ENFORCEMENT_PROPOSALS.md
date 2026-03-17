# CONSTITUTION_ENFORCEMENT_PROPOSALS

## Scope
Lightweight, low-risk enforcement proposals for Constitution-first phase. No new brain layer, no large refactor.

## Proposals

| proposal | problem | mechanism | expected effect | implementation weight | risk | do now / later |
| --- | --- | --- | --- | --- | --- | --- |
| contradiction scan before completion | canonical surfaces can silently diverge | add grep-based pre-completion check for phase/step/mission-baseline contradictions | prevents false completion under narrative drift | low | low | later |
| registry/doc drift guard | docs examples and registry ids can drift | small script/check comparing mission ids/classes in docs vs `operator_mission_registry.json` | keeps docs operationally accurate | low | low | later |
| proof-output naming discipline | runtime proof files have inconsistent names over time | freeze naming pattern (`creator_*`, `wave*_...`) in one policy note | predictable bundles and lower export mistakes | low | low | do now |
| runtime truth pointer block | operators need fast access to volatile truth files | add short pointer block in one canonical surface only | faster operator orientation, less duplication | low | low | later |
| canonical pointer checks | constitution/vocabulary paths may be omitted from manifests | add lightweight check for constitution/vocabulary presence in manifests and core docs | stronger constitution binding and lower silent drift | low | low | later |
| constitution-phase hygiene check | phase can drift after future changes | add a minimal check in `repo_control_center` or validation script for `next-step-constitution-first-phase-v0` while phase is active | keeps phase routing explicit | low | medium | later |

## Minimal Immediate Set
1. Document proof-output naming discipline in canonical vocabulary/constitution companion docs.
2. Keep constitution path present in manifests and canonical narrative surfaces.
3. Preserve clean sync + evidence refresh discipline as existing hard gate.

## Deferred Set (Post-Stabilization)
1. contradiction scan hook
2. registry/doc drift guard
3. canonical pointer checks
4. constitution-phase hygiene check

## Recommendation
Proceed with low-risk documentation-level enforcement first; add script checks only after Constitution V1 hardening scope is approved.
