# UI Acceptance Checklist

## 1. Premium product feel
- [ ] Тёмная premium-подача без декоративного перегруза.
- [ ] Чёткая иерархия: navigation -> status -> workspace -> context.
- [ ] Нет ощущения debug-shell.

## 2. Grid / geometry discipline
- [ ] Нет overlaps.
- [ ] Нет clipping важного текста/CTA.
- [ ] Нет floating CTA.
- [ ] Центр и правая панель не конфликтуют на `1540x920`, `1366x768`, `1280x800`.

## 3. CTA quality
- [ ] Критичные кнопки не hover-only.
- [ ] Primary/secondary/context actions читаются как система.
- [ ] CTA не выпадают из сетки при resize.

## 4. Экранные проверки
- [ ] Dashboard: виден state ядра + next actions.
- [ ] Profiles: быстро читаются identity/state/mode.
- [ ] Sessions: 9:16 зона не выглядит пустым placeholder.
- [ ] Content: queue/validation/readiness логичны.
- [ ] Analytics: top/weak/recommendations считываются с первого взгляда.
- [ ] AI Studio: recommendations/rationale/confidence не перегружены.
- [ ] Audit: timeline + severity читабельны.
- [ ] Updates: update/patch/post-verify путь очевиден.
- [ ] Settings: диагностические ссылки и runtime контекст видны.

## 5. Локализация и типографика
- [ ] Русские тексты естественные и единообразные.
- [ ] Нет случайного RU/EN микса без причины.
- [ ] Нет грубых typographic collisions.

## 6. DPI / scaling
- [ ] `100%` — stable
- [ ] `125%` — stable
- [ ] `150%` — stable

## 7. Machine gate
- [ ] `ui_snapshot_runner` -> `PASS`
- [ ] `ui_validate` -> `PASS`
- [ ] `ui_doctor` -> `PASS`
- [ ] `manual_testing_allowed=true` в `ui_validation_summary.json`
