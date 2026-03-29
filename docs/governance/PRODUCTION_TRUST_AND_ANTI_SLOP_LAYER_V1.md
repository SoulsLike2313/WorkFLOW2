# PRODUCTION_TRUST_AND_ANTI_SLOP_LAYER_V1

Status:
- layer_version: `v1`
- scope: `anti-fake-completion and anti-unproven-claim protections for production flow`

Assertion labels:
- `PROVEN`
- `REUSABLE`
- `DESIGNED`
- `NOT YET IMPLEMENTED`

## 1) Why this layer exists

Production system is useless if it allows:
1. fake completion;
2. unsupported broad claims;
3. scope drift by executors;
4. passing broken outputs upstream.

This layer makes those behaviors non-canonical.

## 2) Core anti-slop rules

1. No completion without evidence.
2. No high-level claim without proof path.
3. No Astartes scope expansion.
4. No department pass without synthesis evidence.
5. No final product pass without full gate chain.

## 3) Claim discipline

Every claim must carry:
1. claim text;
2. certainty class;
3. evidence refs;
4. unresolved unknowns.

Allowed certainty classes:
1. `PROVEN`
2. `PARTIAL`
3. `NOT PROVEN`

## 4) Astartes anti-improvisation controls

1. Task must be written and bounded.
2. Out-of-scope condition triggers blocker return.
3. Unauthorized command decisions are rejected.

## 5) Primarch synthesis controls

Primarch cannot emit department PASS unless:
1. all mandatory sub-bundles exist;
2. contradictions are resolved or explicitly escalated;
3. critical blockers are not hidden.

## 6) Product-level trust controls

Product readiness claim requires:
1. verification evidence;
2. release evidence;
3. known limits section;
4. rollback or fallback note where relevant.

## 7) Failure handling

If department fails gate:
1. emit Blocker/Incident Bundle;
2. reopen queue item(s);
3. keep stage as non-complete.

Only Primarch may:
1. decide local rework strategy;
2. escalate unresolved gate failures to Emperor.

## 8) Why owner can trust this model

1. "сделано" без доказательств не принимается.
2. каждая эскалация и блокер видимы.
3. итог по продукту нельзя получить через красивую формулировку.

## 9) Current status

1. `REUSABLE`: existing constitutional trust/claim denial stack.
2. `DESIGNED`: production-specific anti-slop rules and gate semantics.
3. `NOT YET IMPLEMENTED`: centralized runtime checker enforcing all anti-slop constraints.

