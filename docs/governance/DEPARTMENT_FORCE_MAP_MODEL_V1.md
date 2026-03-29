# DEPARTMENT_FORCE_MAP_MODEL_V1

Status:
- model_version: `v1`
- scope: `Primarch-readable capability map assembled from Astartes entry manifests`

Assertion labels:
- `PROVEN`
- `REUSABLE`
- `DESIGNED`
- `NOT YET IMPLEMENTED`

## 1) What is Department Force Map

Department Force Map is a synthesized capacity view for one department at a given time window.

It answers:
1. who can execute what now;
2. where capacity is missing;
3. where risk is high if we assign wrong.

## 2) Inputs

1. valid `Astartes Entry Manifest` bundles;
2. current queue load;
3. department roadmap priorities;
4. blocker backlog.

## 3) Outputs

1. assignment-ready slot matrix;
2. overload risk map;
3. skill-gap map;
4. recommended routing policy for upcoming task bundles.

## 4) Core dimensions

1. capability coverage by stack;
2. speed profile by task class;
3. current load;
4. reliability/trust posture;
5. local technical constraints.

## 5) Primarch routing rules based on force map

1. Critical tasks go only to slots with required readiness + acceptable load.
2. Unknown/high-risk tasks require either:
   - split into smaller bounded tasks, or
   - escalated planning before assignment.
3. Overloaded slots are protected from extra assignments until load normalizes.

## 6) Force map confidence classes

1. `HIGH_CONFIDENCE`: fresh manifests + stable evidence.
2. `MEDIUM_CONFIDENCE`: partial freshness or minor missing fields.
3. `LOW_CONFIDENCE`: stale or insufficient manifests.

Low-confidence map cannot be used for aggressive scheduling claims.

## 7) Why this model matters for owner

1. меньше невыполнимых задач;
2. меньше "пинг-понга" из-за неверного назначения;
3. быстрее путь от плана к реальному исполнению.

## 8) Current status

1. `DESIGNED`: force map computation model and routing logic.
2. `NOT YET IMPLEMENTED`: centralized script that auto-builds this map from manifests.

