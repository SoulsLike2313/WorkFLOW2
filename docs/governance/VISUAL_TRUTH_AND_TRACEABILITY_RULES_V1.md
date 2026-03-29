# VISUAL_TRUTH_AND_TRACEABILITY_RULES_V1

Статус:
- version: `v1`
- layer_type: `visual_truth_rules`
- labels_used: `ACTIVE | RECOMMENDED | FUTURE | NOT YET IMPLEMENTED | STYLE-LAYER ONLY`

## 1) Visual truth classes

## `SOURCE_EXACT`

Meaning:
- direct fact from source artifact.

Visual rule:
1. strongest trust badge;
2. explicit source path;
3. click-to-source must be available.

## `DERIVED_CANONICAL`

Meaning:
- canonical derivation from source facts.

Visual rule:
1. derived badge;
2. derivation note;
3. source set references required.

## `VIEW_ONLY`

Meaning:
- visual organization only, no new fact claim.

Visual rule:
1. neutral badge;
2. no authoritative claim styling.

## `HUMAN_INTERPRETATION`

Meaning:
- analytical recommendation layer.

Visual rule:
1. interpretation badge;
2. must remain owner-overridable;
3. cannot be styled as proven fact.

## 2) Trace links (`ACTIVE`)

Each significant panel/card must expose:
1. source file path;
2. source section/member hint;
3. last seen timestamp (if available);
4. open source action.

## 3) Click-to-source behavior (`RECOMMENDED`)

1. click opens source preview or artifact path;
2. if source missing, panel shows explicit missing state;
3. no silent fallback to synthetic text.

## 4) Prohibited visual deception

1. green health without evidence;
2. hiding unresolved blockers behind style layers;
3. blending interpretation into source-exact color coding.

## 5) Theme safety boundary

Theme changes may alter appearance, but cannot alter truth class semantics or traceability affordances.
