# FACTORY_THEME_SYSTEM_V1

Статус:
- version: `v1`
- layer_type: `theme_system`
- labels_used: `ACTIVE | RECOMMENDED | FUTURE | NOT YET IMPLEMENTED | STYLE-LAYER ONLY`

## 1) Truth layer vs style layer

Truth layer (не ломается темой):
1. source classes (`SOURCE_EXACT`, `DERIVED_CANONICAL`, `VIEW_ONLY`, `HUMAN_INTERPRETATION`);
2. panel hierarchy;
3. role visibility;
4. trace links;
5. status semantics.

Style layer (можно менять):
1. color tokens;
2. surface/material treatment;
3. typography style;
4. motion expression;
5. icon styling.

## 2) Что можно менять свободно (`STYLE-LAYER ONLY`)

1. оттенки темы и палитру;
2. glow/fog intensity внутри safe ranges;
3. card material appearance;
4. transition feel.

## 3) Что менять нельзя (`ACTIVE`)

1. truth-class mapping и визуальные маркеры этих классов;
2. приоритеты критичности/предупреждений;
3. структура role-based observation modes;
4. кликабельная трассировка к source artifact.

## 4) Theme pack lifecycle

1. register pack in `FACTORY_THEME_PACK_REGISTRY_V1.json`;
2. validate required token coverage;
3. run traceability contrast checks;
4. mark status (`ACTIVE`/`FUTURE`).

## 5) Alternate skins policy (`RECOMMENDED`)

Разрешено иметь alternate skins, если:
1. сохранена readability;
2. не потеряна status clarity;
3. не сломана evidence traceability.

## 6) Current primary pack

`NEBULA_METALLIC_COMMAND_STYLE_V1` (`ACTIVE`).
