# FACTORY_VITAL_SIGNS_VISUAL_MODEL_V1

Статус:
- version: `v1`
- layer_type: `vital_signs`
- labels_used: `ACTIVE | RECOMMENDED | FUTURE | NOT YET IMPLEMENTED | STYLE-LAYER ONLY`

## 1) Signals in scope

1. Reliability
2. Operability
3. UX
4. Architecture
5. Verification
6. Release Readiness
7. Distribution Readiness

## 2) Visual carriers

1. rings (aggregate state);
2. pulse bars (short-term trend);
3. state indicators (critical/warn/stable/improving);
4. health cards (evidence summary);
5. trend arrows (directional confidence).

## 3) State semantics (`ACTIVE`)

1. `stable`: controlled, no critical drift;
2. `improving`: positive trend with evidence;
3. `warning`: unresolved risk rising;
4. `critical`: blocking condition/gate fail.

## 4) Mandatory encoding per sign

Каждый sign должен кодировать:
1. current state;
2. trend direction;
3. last evidence timestamp;
4. source trace link.

## 5) Anti-fake-health rules

1. без source evidence нельзя показывать green/stable;
2. decorative ring without source class badge запрещен;
3. manual override должен быть явно помечен.

## 6) Recommended mapping

1. Reliability: incidents/regression density;
2. Operability: workflow gate health;
3. UX: validated user-flow quality signals;
4. Architecture: debt/risk pressure;
5. Verification: pass/fail and blocker depth;
6. Release Readiness: release gate completeness;
7. Distribution Readiness: narrative/channel/campaign starter completeness.

## 7) `NOT YET IMPLEMENTED`

1. full automated computation of all signs from live pipeline streams.
