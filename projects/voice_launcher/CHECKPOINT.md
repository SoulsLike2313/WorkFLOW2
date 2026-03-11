# Voice Launcher Checkpoint

Дата: 2026-03-11

## Что уже стабилизировано

- Антидубли запуска:
  - `LaunchGate` получил `inflight`-guard (single-flight).
  - для `launcher_play` добавлен post-launch cooldown.
- Безопасный `launcher_play` сохранен:
  - верификация окна/кнопки, `dry-run`, `highlight-only`, этапные логи.
- История и диагностика:
  - `EventHistory` подключен к UI и snapshot.
  - диагностика собирает логи, бэкапы, снапшоты, версии зависимостей.

## UI прогресс

- Премиальная палитра: фиолетовый + желтый + оранжевый.
- Добавлена карточка "Быстрый статус" в простом режиме.
- Улучшена читаемость колонки "Режим".

## Важные технические детали

- Новое поле команды: `post_launch_cooldown` (секунды).
  - хранится в `commands.json`,
  - доступно в мастере добавления команды,
  - участвует в anti-duplicate логике запуска.

## Что покрыто тестами

- `launch_policy` (cooldown + inflight),
- storage normalization/migration,
- wizard payload,
- diagnostics bundle,
- audio device service,
- event history,
- theme helpers.

## Следующий шаг (рекомендуемый)

1. Довести "мастер команды" до полного пошагового wizard-flow с явным шагом preview/highlight/full-test.
2. Добавить отдельный "диагностический отчет" в UI (просмотр ключевых self-check без открытия json).
3. Подготовить финальную pre-release сборку (portable + installer) после ручной smoke-проверки.
