# Shortform Content Ops Core

Модульное Python-ядро для short-form операций (TikTok / Reels / Shorts).

Проект выполняет роль слоя аналитики и оркестрации:
- хранит состояние аккаунта и контента;
- оценивает креативы по настраиваемым порогам;
- формирует машиночитаемые планы действий;
- предоставляет runtime на FastAPI + SQLite.

Проект **не** реализует обход правил платформ, эвазию, маскировку трафика и anti-detection функции.

## Структура

```text
app/
  __init__.py
  models.py
  config.py
  analytics.py
  registry.py
  planner.py
  demo_data.py
  io_utils.py
  main.py
  db.py
  repository.py
  schemas.py
  api.py
  bootstrap_v2.py
external_data/
  tiktok_automation_snapshot/
run_setup.ps1
```

## Совместимость с TikTok automation

Адаптер snapshot читает данные из:
- `external_data/tiktok_automation_snapshot/output/session_stats.jsonl`
- `external_data/tiktok_automation_snapshot/output/session_events.jsonl`

Если snapshot-файлы отсутствуют, используется детерминированный demo seed, чтобы ядро оставалось тестируемым.

## Быстрый старт (Windows)

```powershell
cd E:\CVVCODEX\projects\active_projects\shortform_core
.\run_setup.ps1
```

## Ручной запуск

```powershell
cd E:\CVVCODEX\projects\active_projects\shortform_core
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

python -m app.main
python -m app.bootstrap_v2
python -m uvicorn app.api:app --host 127.0.0.1 --port 8000 --reload
```

## API-эндпоинты

- `GET /health`
- `POST /bootstrap/load-demo`
- `GET /accounts/{account_id}/snapshot`
- `POST /metrics/ingest`
- `POST /plan/generate`
- `GET /plan/{account_id}/latest`
