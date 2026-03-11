# UI Build Rules

Проект: `shortform_core` desktop workspace  
Назначение: единый стандарт сборки UI без деградации layout/UX.

## 1. Grid rules
- Основной shell использует фиксированный outer margin и предсказуемый gap.
- CTA и карточки обязаны жить внутри layout-контейнеров, не “вешаться” на root без сетки.
- Запрещены самопроизвольные absolute/floating позиции для ключевых действий.

## 2. Spacing rules
- Единые токены отступов (`PAGE_GAP`, `ROW_GAP`, `GRID_GAP`, `CARD_INSET`).
- Нельзя смешивать случайные константы в одном экране.
- Вертикальный ритм должен быть равномерным внутри экранов и между экранами.

## 3. CTA placement rules
- Для каждого экрана должна быть явная иерархия: primary / secondary / outline.
- Критические CTA видимы без hover.
- Запрещены hover-only critical controls.

## 4. Typography rules
- Заголовки, body и secondary текст должны иметь устойчивую иерархию.
- Длинные русские строки обязаны иметь safe strategy: wrap/elide/короткие метки.
- Запрещены грубые typographic collisions и резкие контрастные скачки.

## 5. Panel composition rules
- Карточки и панели строятся по уровням поверхности: background -> panel -> elevated.
- Запрещены грубые толстые outlines и хаотичный glow.
- Визуальный стиль не должен ломать читаемость данных.

## 6. DPI/scaling rules
- Минимум обязательной проверки: `100%`, `125%`, `150%`.
- Проверка включает: clipping, overlap, out-of-bounds, CTA visibility.
- Любая правка UI считается завершённой только после machine-run проверки.

## 7. Layout invariants
- Нет налезаний блоков.
- Нет отрицательных координат интерактивных контролов.
- Нет незавершённых opacity/effect состояний на страницах.
- Нет “мёртвых зон” из-за сломанной анимации переключения.

## 8. Screen acceptance rules
- Dashboard: структура + быстрые действия + читаемая сводка.
- Profiles: сканируемость статусов и режимов.
- Sessions: рабочая 9:16 зона без визуального среза.
- Content: понятный flow валидация -> очередь.
- Analytics: считываемые инсайты и action direction.
- AI Studio: рекомендации и next-step логика.
- Audit/Updates/Settings: operational clarity без developer-only шума.

## 9. Validation standard
- Обязательный инструмент: `scripts/ui_doctor.py`.
- Артефакты: `ui_validation_summary.json`, `ui_validation_summary.md`, `ui_screenshots_manifest.json`.
- Gate: `FAIL` блокирует ручной acceptance.

## 10. Customization layer
- Разрешена кастомизация только через токены/пресеты, а не через хаотичные локальные правки.
- Базовые токены: colors, spacing, radius, glow, typography scale.
- Пресеты: button presets, panel presets, layout mode.
- Источник override: `runtime/ui/theme_overrides.json` (или env `SHORTFORM_UI_THEME_OVERRIDES`).
- Критично: кастомизация не должна изменять layout-инварианты и CTA-доступность.
