# UI Build Rules

Канонические правила сборки и проверки desktop UI для active module:
`projects/wild_hunt_command_citadel/shortform_core`.

## 1. Grid Rules
- Единая колонная логика: sidebar -> workspace -> context panel.
- Единые внешние отступы shell.
- Единые внутренние отступы контейнеров и карточек.
- Компоненты выравниваются по edges/baselines, не “плавают” в пустоте.
- Split-панели обязаны иметь безопасные минимальные размеры.

## 2. Spacing Rules
- Использовать scale-токены, а не случайные значения.
- Согласованные gaps между секциями, карточками, строками действий.
- Вертикальный rhythm не должен “сжиматься” при resize.
- Списки/ленты сохраняют читаемость при высокой плотности данных.

## 3. CTA Placement Rules
- Critical CTA не могут быть hover-only.
- Primary CTA должны быть композиционно закреплены в блоках.
- Secondary CTA группируются рядом с релевантным контекстом.
- Нельзя размещать действия без явной привязки к panel purpose.

## 4. Typography Rules
- Чёткая иерархия: title -> section -> body -> helper -> status.
- Метрики имеют отдельный визуальный уровень.
- Русский текст должен быть естественным и продуктовым.
- Контролировать line-height и длину строк (особенно в context panel).

## 5. Layout Invariants
- No overlaps.
- No clipping ключевых данных и CTA.
- No broken/empty zones после навигации.
- No detached action blocks.
- No inconsistent paddings.

## 6. DPI / Scaling Rules
- Обязательные проверки на `100%`, `125%`, `150%`.
- Длинные русские строки не должны ломать layout.
- Status pills и кнопки обязаны сохранять читаемость на всех scale.

## 7. Product Direction Rules
- No Witcher/Wild Hunt/fantasy branding.
- No retro cheap sci-fi.
- No debug-shell look.
- Premium dark metallic purple direction сохраняется без перегруза.
- UX ясность важнее декоративных эффектов.

## 8. Automation Rules
- Перед ручным acceptance запускать:
  - `scripts/ui_doctor.py`
  - `scripts/ui_snapshot_runner.py`
  - `scripts/ui_validate.py`
- Результаты обязаны оставлять machine-readable артефакты.
