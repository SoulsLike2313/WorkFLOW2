# Changelog

## 1.1.0-dev (2026-03-11)

- Начат реальный модульный рефакторинг:
  - `voice_launcher_app/app`
  - `voice_launcher_app/core`
  - `voice_launcher_app/asr`
  - `voice_launcher_app/actions`
  - `voice_launcher_app/storage`
  - `voice_launcher_app/profiles`
  - `voice_launcher_app/diagnostics`
  - `voice_launcher_app/ui`
- Дополнительно вынесены бизнес-сервисы:
  - `voice_launcher_app/core/command_manager.py` (валидация/сохранение команд)
  - `voice_launcher_app/actions/launcher_runner.py` (оркестрация безопасного launcher_play)
  - `voice_launcher_app/app/controller.py` (ASR listen loop, антидубль, match/launch orchestration)
  - `voice_launcher_app/ui/controller.py` (simple/advanced mode + история UI-событий)
  - `voice_launcher_app/ui/wizard.py` (мастер добавления команды и безопасный preview launcher)
  - `voice_launcher_app/core/launch_policy.py` (процессный кэш + launch cooldown/single-instance gate)
  - `voice_launcher_app/actions/target_launcher.py` (безопасный запуск файлов + duplicate-guard state)
- Усилен `launcher_play`:
  - strict verification-first алгоритм
  - проверка окна по process path + title patterns + confidence
  - `dry-run` и `highlight-only`
  - мягкий отказ без клика при недостаточной уверенности
  - детальные этапные логи
- Улучшено хранение данных:
  - runtime-логи в `AppData\VoiceLauncher\logs`
  - backups/snapshots в отдельных каталогах
  - миграция настроек до `settings_version = 6`
- Добавлены профили:
  - экспорт/импорт команд и настроек (JSON)
  - валидация профиля
- Добавлена встроенная диагностика:
  - сбор логов/конфигов/окружения в диагностический пакет
- Обновлен UI:
  - переключатель простой/расширенный режим
  - быстрые кнопки (микрофон, логи, профиль, диагностика)
  - нижняя строка “последняя фраза/последнее действие”
  - события в расширенном табе
- Обновлена сборка:
  - новый `VoiceLauncher.spec` (hiddenimports + datas + icon)
  - Inno Setup script с desktop/startup option
  - `dev_tools/build_portable.ps1`
  - `dev_tools/build_installer.ps1`
- Добавлены default/example конфиги:
  - `config/settings.example.json`
  - `config/commands.example.json`
- Добавлены тесты:
  - storage/config migration
  - matching
  - profile import/export
  - safe launcher automation
  - smoke import

## 1.1.0-dev update (2026-03-11)

- Stability hardening:
  - Added `inflight` single-flight guard in `LaunchGate` to prevent repeated concurrent launches of the same command.
  - Added `post_launch_cooldown` behavior for `launcher_play` to avoid multi-window spam after one successful trigger.
  - `voice_launcher.py` now marks launch lifecycle (`mark_launch_started` / `mark_launch_finished`) for normal/admin/launcher modes.
- Diagnostics and history:
  - Integrated `EventHistory` and included it in runtime snapshot and diagnostics bundle.
  - Diagnostics now also bundles recent `logs`, `backups`, `snapshots` and dependency versions.
- Premium UI pass:
  - Updated premium palette/typography and control styles in `voice_launcher_app/ui/theme.py`.
  - Added top "Quick Status" card in commands tab and improved mode-column readability/adaptive sizing.
- Tests:
  - Added `tests/test_audio_devices.py`, `tests/test_event_history.py`, `tests/test_theme.py`.
