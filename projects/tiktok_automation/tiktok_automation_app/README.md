# Witcher Command Deck (Единая Версия)

Теперь это одна программа с единым UI:

- слой `TikTok automation` (основной сценарий через Playwright/CDP);
- слой `shortform_core` (новое аналитическое ядро и планировщик) в том же окне.

## Что добавлено

В интерфейсе сохранён старый стиль и добавлен блок:

- `Ядро Аналитики (shortform_core)`
- `Core Bootstrap v2`
- `Core Анализ + План`
- `Показать Core План`

## Пути

- UI-приложение: `E:\CVVCODEX\projects\tiktok_automation\tiktok_automation_app`
- Ядро: `E:\CVVCODEX\projects\active_projects\shortform_core`

## Запуск

```powershell
cd E:\CVVCODEX\projects\tiktok_automation\tiktok_automation_app
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m playwright install chromium
python app.py
```

Без консольного окна:

- `run.bat`
- `run_silent.vbs`

## Как работать в объединённом режиме

1. При необходимости запусти обычный сценарий через `Старт Контракта`.
2. В блоке `Ядро Аналитики` оставь галочку `Использовать текущий TikTok output как источник snapshot`.
3. Нажми `Core Анализ + План`.
4. В `Боевом Журнале` появятся строки `[CORE]` с результатами.
5. Нажми `Показать Core План` для повторного вывода плана.

## Файлы результатов ядра

- `E:\CVVCODEX\projects\active_projects\shortform_core\runtime\output\analytics_report.json`
- `E:\CVVCODEX\projects\active_projects\shortform_core\runtime\output\plan_bundle.json`
- `E:\CVVCODEX\projects\active_projects\shortform_core\runtime\output\bootstrap_v2.json`

## Важно

Ядро `shortform_core` — это слой оркестрации и аналитики.  
Оно не реализует функции обхода правил платформ, маскировки трафика или антидетект-эвазию.
