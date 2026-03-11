# UI Acceptance Checklist

Использовать для финального ручного просмотра после machine-run `PASS`.

- [ ] Premium feel: интерфейс выглядит как premium control center, без debug-shell ощущения.
- [ ] Consistency: единый стиль кнопок, карточек, панелей, pills, хедеров и списков.
- [ ] Navigation clarity: активный раздел считывается мгновенно, пользователь понимает текущий контекст.
- [ ] Button quality: hover/focus/pressed/disabled читаемы и предсказуемы.
- [ ] Card/panel quality: нет тяжёлых грубых рамок, иерархия поверхностей понятна.
- [ ] Typography: заголовки, body и secondary текст читаемы, нет грубых столкновений.
- [ ] Spacing/rhythm: нет налезаний, нет “слипания” блоков, ритм отступов устойчив.
- [ ] Motion quality: анимации аккуратные, не вызывают исчезновения/ломку экрана.
- [ ] Localization: русский текст естественный, без смешения английского без причины.
- [ ] Scaling: проверка на 100% / 125% / 150% без clipping/overflow/overlap.
- [ ] Sessions realism: 9:16 session area не выглядит как пустой placeholder.
- [ ] Analytics storytelling: в аналитике ясно “что происходит” и “что делать дальше”.
- [ ] Sidebar consistency: состояния `default/hover/active` стабильны и контрастны.
- [ ] Context panel consistency: правая панель не конфликтует с центральной зоной.
- [ ] CTA clarity: primary/secondary/outline не перепутаны, нет floating CTA.
- [ ] Hover-only anti-pattern: критичные действия видимы без hover.
- [ ] Old branding absence: нет Witcher/Wild Hunt/лора/игрового брендинга.

## Acceptance gate
- Manual acceptance разрешён только при `ui_doctor` статусе `PASS` или `PASS_WITH_WARNINGS` без critical.
- Если есть `FAIL` или critical-issues: возврат в correction phase обязателен.
