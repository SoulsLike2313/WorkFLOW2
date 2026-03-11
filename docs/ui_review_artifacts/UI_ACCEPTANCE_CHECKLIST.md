# UI Acceptance Checklist

## A. Product-grade baseline
- [ ] Интерфейс выглядит как premium command center, не как debug shell.
- [ ] Dashboard честно отражает состояние ядра (не пустые декоративные блоки).
- [ ] Пользователь сразу понимает “где я” и “что делать дальше”.

## B. Layout integrity
- [ ] Нет overlaps.
- [ ] Нет clipping ключевых CTA/метрик.
- [ ] Нет floating CTA вне своей панели.
- [ ] Main workspace и context panel устойчивы на resize.
- [ ] Нет broken/empty page states после быстрых переключений.

## C. Interaction quality
- [ ] Нет hover-only critical controls.
- [ ] Hover/focus/pressed читаемы и стабильны.
- [ ] CTA hierarchy понятна: primary / secondary / contextual.

## D. Screen-specific checks
- [ ] Dashboard: core-state + next-actions читаются быстро.
- [ ] Profiles: profile identity и quick actions считываются без перегруза.
- [ ] Sessions: frame и surrounding controls выглядят устойчиво.
- [ ] Content: queue/validation/readiness логично связаны.
- [ ] Analytics: top/weak/recommendations читаются как actionable блоки.
- [ ] AI Studio: rationale/confidence/ideas читаются без шума.
- [ ] Audit: timeline и severity читаются мгновенно.
- [ ] Updates: update flow и post-verify статус понятны.
- [ ] Settings: ссылки на runtime/diagnostics не теряются.

## E. Localization / readability
- [ ] Русский текст естественный и продуктовый.
- [ ] Нет случайного RU/EN микса без причины.
- [ ] Длинные русские строки не ломают layout.

## F. Scaling / DPI
- [ ] Проверка 100% пройдена.
- [ ] Проверка 125% пройдена.
- [ ] Проверка 150% пройдена.

## G. Final gate
- [ ] `ui_doctor` -> PASS.
- [ ] `ui_snapshot_runner` -> PASS.
- [ ] `ui_validate` -> PASS.
- [ ] Только после этого разрешён final human sign-off.
