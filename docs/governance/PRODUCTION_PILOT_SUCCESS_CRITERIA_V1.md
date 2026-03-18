# PRODUCTION_PILOT_SUCCESS_CRITERIA_V1

## Pilot Verdict Model

### PASS
Pilot is `PASS` only if all mandatory conditions hold:
1. admission discipline preserved on all pilot missions
2. no fake completion claims
3. required constitutional checks executed with known status
4. execution evidence complete enough for mission verdict traceability
5. certification/closure path coherent where mission design requires it
6. mirror refresh/full-check stable for closure mission where applicable
7. operator friction is acceptable or explicitly explained with mitigation
8. no major narrative drift introduced in canonical surfaces

### PARTIAL
Pilot is `PARTIAL` when:
- core mission paths execute, but one or more non-critical criteria remain weak; and
- no hard constitutional violation occurred.

Typical PARTIAL cases:
- incomplete closure evidence for optional mission
- friction above target but still diagnosable
- medium-strength evidence where strong evidence was expected

### FAIL
Pilot is `FAIL` if any of the following occurs:
- admission discipline broken
- fake completion or unsupported completion claim
- unresolved critical contradiction during pilot closure
- guarded mission executed without required authority/policy gate PASS
- closure mission claims mirror-safe status without stable post-refresh full-check

## Criterion-to-Evidence Map
| criterion | evidence | pass condition |
| --- | --- | --- |
| admission discipline preserved | mission reports + repo control status | no blocked admission bypass, no silent override |
| constitutional checks run | check outputs in mission report package | contradiction/drift/hygiene states are explicit |
| evidence completeness | runtime mission artifacts + review report | mission verdict reproducible from artifacts |
| closure coherence | closure mission report | completion -> review/certification -> refresh -> full-check chain present |
| operator friction | friction model capture | friction documented, bounded, and actionable |
| narrative stability | canonical surface review | no new phase/state contradictions |
