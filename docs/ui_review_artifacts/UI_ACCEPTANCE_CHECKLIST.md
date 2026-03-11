# UI Acceptance Checklist

Использовать для финального ручного просмотра перед sign-off.

## Layout / Grid
- [ ] Нет overlaps между блоками.
- [ ] Нет clipping важных подписей/CTA.
- [ ] Нет floating CTA вне композиции блока.
- [ ] Единая колонная логика и предсказуемые отступы.
- [ ] Context panel и центральная зона не конфликтуют на resize.

## Interaction
- [ ] Нет hover-only critical controls.
- [ ] Hover/focus/pressed состояния читаемы и стабильны.
- [ ] CTA видны в базовом состоянии.
- [ ] Primary/secondary/context action hierarchy понятна.

## Visual Quality
- [ ] Premium feel сохранён (dark graphite + violet metallic).
- [ ] Нет дешёвого retro sci-fi / plastic feel.
- [ ] Карточки/панели имеют понятную surface hierarchy.
- [ ] Glow контролируемый, не перегруженный.

## Typography / Copy
- [ ] Иерархия заголовков и метрик ясная.
- [ ] Русский текст естественный и продуктовый.
- [ ] Нет грубых/колких формулировок.
- [ ] Нет случайного смешения RU/EN в интерфейсе.

## Scaling / Robustness
- [ ] Проверка `100%` пройдена.
- [ ] Проверка `125%` пройдена.
- [ ] Проверка `150%` пройдена.
- [ ] Длинные русские строки не ломают композицию.

## Product Logic
- [ ] Навигация и текущий экран считываются мгновенно.
- [ ] Следующий шаг пользователя понятен.
- [ ] Sessions ощущается как product workspace, не placeholder.
- [ ] Analytics читается быстро и даёт actionable контекст.
- [ ] AI Studio понятен по рекомендациям/rationale/confidence.
- [ ] Остатки старого branding отсутствуют.
