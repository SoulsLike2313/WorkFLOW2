# Witcher Command Deck (Единая версия)

Единое десктоп-приложение с двумя слоями:

- TikTok automation (UI + Playwright/CDP сценарии)
- shortform_core (аналитика, bootstrap, план действий)

## Что уже реализовано

- Единый Witcher UI на русском языке.
- Темы: `Волк`, `Нильфгаард`, `Скеллиге`.
- Мастер первого запуска:
  - проверка `.venv`
  - проверка зависимостей
  - проверка Chromium для Playwright
  - автонастройка в один клик
- Профили конфигураций:
  - сохранение/обновление/удаление
  - быстрое переключение между профилями
- Планировщик и очередь:
  - задания по времени и дням недели
  - очередь запусков (manual + schedule)
- Мини-дашборд в UI:
  - таблица метрик
  - графики (лайки, подписчики, приоритеты core-плана)
- Расширенная устойчивость движка:
  - ретраи
  - таймауты шагов и селекторов
  - диагностика селекторов (`selector_diagnostics.jsonl`)
  - health-check профиля перед контрактом
- Интеграция с `shortform_core`:
  - bootstrap
  - анализ + план
  - вывод плана прямо в логе UI

## Быстрый запуск

```powershell
cd E:\CVVCODEX\projects\tiktok_automation\tiktok_automation_app
powershell -ExecutionPolicy Bypass -File .\run_setup.ps1
.\.venv\Scripts\python.exe .\app.py
```

Запуск без консольного окна:

- `run.bat`
- `run_silent.vbs`

## One-click EXE сборка

```powershell
cd E:\CVVCODEX\projects\tiktok_automation\tiktok_automation_app
powershell -ExecutionPolicy Bypass -File .\build_exe.ps1 -Clean
```

Итоговый файл:

- `dist\WitcherCommandDeck.exe`

Также можно запустить:

- `build_exe.bat`

## Основные пути

- UI: `E:\CVVCODEX\projects\tiktok_automation\tiktok_automation_app`
- Core: `E:\CVVCODEX\projects\active_projects\shortform_core`

## Важные выходные файлы

- TikTok output:
  - `output\session_events.jsonl`
  - `output\session_stats.jsonl`
  - `output\selector_diagnostics.jsonl`
- Core output:
  - `E:\CVVCODEX\projects\active_projects\shortform_core\runtime\output\analytics_report.json`
  - `E:\CVVCODEX\projects\active_projects\shortform_core\runtime\output\plan_bundle.json`
  - `E:\CVVCODEX\projects\active_projects\shortform_core\runtime\output\bootstrap_v2.json`
