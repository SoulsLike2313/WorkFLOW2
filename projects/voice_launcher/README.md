# Voice Launcher

Голосовой запускатор приложений для Windows с безопасным режимом `launcher_play`, поддержкой `admin_task`, логированием и хранением пользовательских данных в AppData.

## Запуск из исходников

1. Установите Python 3.12+.
2. Создайте venv и установите зависимости:
   - `py -3.12 -m venv .venv`
   - `.\.venv\Scripts\Activate.ps1`
   - `python -m pip install --upgrade pip`
   - `pip install pystray pillow SpeechRecognition pyaudio pywinauto faster-whisper numpy`
3. Запуск:
   - `python voice_launcher.py`

## Сборка Portable

- `.\dev_tools\build_portable.ps1 -PythonExe python`
- Результат:
  - `dist\VoiceLauncher.exe`
  - `dist\portable\` (готовый пакет для переноса)

## Сборка Installer

1. Установите Inno Setup 6.
2. Запуск:
   - `.\dev_tools\build_installer.ps1 -PythonExe python`
3. Результат:
   - `installer\output\VoiceLauncherSetup.exe`

## Runtime-данные

- Пользовательские файлы:
  - `%APPDATA%\VoiceLauncher\commands.json`
  - `%APPDATA%\VoiceLauncher\settings.json`
- Логи:
  - `%APPDATA%\VoiceLauncher\logs\`
- Бэкапы и снапшоты:
  - `%APPDATA%\VoiceLauncher\backups\`
  - `%APPDATA%\VoiceLauncher\snapshots\`
- Для отладки можно переопределить путь:
  - `VOICE_LAUNCHER_STORAGE_DIR=C:\Temp\VoiceLauncherData`

## Импорт/экспорт профиля

- В основном окне используйте кнопки:
  - `Экспорт профиля`
  - `Импорт профиля`
- Профиль содержит команды и настройки в одном JSON-файле.
- При импорте доступен выбор:
  - заменить текущие команды или объединить
  - применить настройки из профиля или оставить локальные

## Безопасная настройка launcher_play

1. В мастере добавления команды включите `Режим лаунчера`.
2. Укажите:
   - `Текст кнопки`
   - `Фильтр окна` (часть заголовка)
   - `Уверенность окна` (рекомендуется 0.90+)
3. Сначала выполните `Безопасный тест` (dry-run, без клика).
4. После успешной верификации отключите dry-run при необходимости.

## Тестирование

- Unit/integration:
  - `python -m pytest -q`
- Покрыты:
  - matching
  - storage/config migration
  - profile import/export
  - safe launcher logic
  - smoke import

## Latest Improvements (2026-03-11)

- Added anti-duplicate launch hardening (`inflight` + post-launch cooldown) to reduce accidental multi-open.
- Added premium quick-status card and improved command mode column layout.
- Diagnostics now includes event history and recent backups/snapshots.
- New tests added for audio device service, theme helpers, and event history.
