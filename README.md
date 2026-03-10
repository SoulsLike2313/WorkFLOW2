# WorkFLOW Repository

Репозиторий приведён к структуре «один проект = одна папка».

## Структура

- `projects/adaptive_trading/`
  - Алготрейдинг-бот и 3 GUI-варианта (`adaptive_trading_bot.py`, `adaptive_trading_gui*.py`)
  - Данные/конфиг для демо-тестов (`demo_wallet.json`, `learned_crypto_model_test.json`)
  - `trading_requirements.txt`

- `projects/voice_launcher/`
  - Голосовой лаунчер (`voice_launcher.py`)
  - Сборка/инсталлятор (`VoiceLauncher.spec`, `build/`, `dist/`, `installer/`)
  - Иконки и утилиты (`assets/`, `dev_tools/`)
  - Локальные runtime-файлы (`commands.json`, `settings.json`, `startup_trace.log`)

- `projects/tiktok_automation/tiktok_automation_app/`
  - Desktop-приложение автоматизации TikTok (GUI + Playwright/CDP)

- `projects/life_rpg_tracker/`
  - Трекер-квестов жизни (`life_rpg_tracker.py`)
  - Данные квестов (`life_rpg_quests.json`)

- `projects/progress_dashboard/`
  - Streamlit-приложение прогресса (`progress_app.py`)

- `projects/razer_area_ui/`
  - Tkinter + Pygame UI расчёта площади (`razer_style_area_ui.py`)

- `projects/march8_turtle/`
  - Демо-графика `turtle` (`march8_turtle.py`)

- `docs/`
  - `CHECKPOINT.md`
  - `DEV_CONTINUITY.md`

## Примечания

- `gitignore` настроен так, чтобы не попадали виртуальные окружения, кэши и runtime-артефакты.
- Внутри каждого проекта сохранены относительные пути, чтобы запуск и сборка не ломались после переноса.
