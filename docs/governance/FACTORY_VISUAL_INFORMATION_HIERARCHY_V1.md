# FACTORY_VISUAL_INFORMATION_HIERARCHY_V1

Статус:
- version: `v1`
- layer_type: `visual_information_hierarchy`
- labels_used: `ACTIVE | RECOMMENDED | FUTURE | NOT YET IMPLEMENTED | STYLE-LAYER ONLY`

## 1) First-glance layer (`ACTIVE`)

Owner видит сразу:
1. critical blockers;
2. owner gates waiting;
3. product lanes in trouble;
4. vital signs with red/warn states.

## 2) Second-glance layer (`RECOMMENDED`)

1. department floor states;
2. queue loads;
3. wave progress;
4. trend deltas.

## 3) Drill-down layer (`RECOMMENDED`)

1. source artifacts;
2. contradiction details;
3. before/after diffs;
4. role-level execution context.

## 4) Priority rules

1. blockers > gates > active waves > status cards;
2. product criticality > department vanity metrics;
3. evidence-backed deltas > decorative indicators.

## 5) Overload prevention

1. progressive disclosure;
2. bounded card density per screen;
3. hide non-critical decorative elements during critical state.

## 6) Required visible entities

1. products;
2. departments (including non-active);
3. gates;
4. blockers;
5. deltas;
6. trace links.
