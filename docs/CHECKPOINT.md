# Project Checkpoint

## 2026-03-10

### Active Goal
- Улучшить точность распознавания коротких русских ключевых фраз (например, "танки") и сохранить стабильный контекст разработки.

### What We Changed
- Добавлена нормализация входного аудио перед ASR:
  - безопасный Mic Gain + авто-дотяжка RMS до рабочего уровня без клиппинга.
- Whisper улучшен в режиме команд:
  - командная подсказка (`initial_prompt`) на основе текущего списка фраз;
  - более устойчивый декод для коротких команд (вторая попытка без VAD, если первая слишком короткая).
- Ускорен путь Whisper:
  - если доступен `numpy`, аудио передается в модель напрямую (без временного файла).
- Мягкая миграция настроек до `settings_version = 4`:
  - слишком низкий `listen_timeout` поднимается до 1.1;
  - слишком короткий `listen_phrase_limit` поднимается до 3.2;
  - слишком высокий `fuzzy_threshold` (>0.8) смягчается до 0.78.
- Улучшено сопоставление очень коротких распознаваний:
  - адаптивный порог снижен для 1-2 символов;
  - увеличен требуемый отрыв от второго совпадения;
  - добавлен штраф при несовпадении первой буквы.
- Добавлен новый режим команды `Лаунчер+Play`:
  - запускает лаунчер;
  - в фоне ждет активную кнопку `Играть` (или любой заданный текст);
  - автоматически нажимает ее после завершения обновлений.
  - Доступен и в ручном добавлении, и в диалоге "Добавить голосом".
- Исправлен UI диалога "Добавить команду голосом":
  - кнопка `Записать` снова видна;
  - параметры `Лаунчер+Play` показываются только при включенном чекбоксе;
  - увеличен базовый размер окна для масштабирования Windows.
- Улучшен режим `Записать` в диалоге добавления команды:
  - калибровка увеличена до 1.0 сек, как в стабильном тесте;
  - увеличен лимит длины фразы при записи (до 5.2+ сек);
  - объединяются варианты от Whisper и Google (`prefer_all_engines=True`);
  - короткие обрезки (`т`, `то`) уходят в конец списка вариантов.
- Исправлен повторный запуск лаунчера в режиме `Лаунчер+Play`:
  - если лаунчер уже висит/свернут, приложение пытается активировать существующее окно;
  - добавлен периодический повторный "kick"-запуск (без duplicate guard), чтобы развернуть окно;
  - это устраняет сценарий "первый запуск работает, второй по голосу не открывает".
- Усилена устойчивость загрузки данных:
  - `load_json` теперь читает `utf-8-sig` (поддержка JSON с BOM);
  - авто-восстановление mojibake для фраз/полей команд при загрузке.
- Дополнительно исправлен авто-фикс mojibake:
  - усилен скоринг декодирования (чтобы `РЈС‚...` надежно превращалось в `Утилиты`);
  - убран агрессивный `errors='ignore'` при декодировании, чтобы не терять символы;
  - добавлена защита для `play_text`: `грать` автоматически корректируется в `Играть`.
- Текущий `commands.json` уже восстановлен:
  - путь `C:/Users/PC/Desktop/Утилиты/...` нормализован;
  - `play_text` возвращен в `Играть`.
- Полный техаудит стабильности `voice_launcher.py`:
  - добавлены атомарные сохранения JSON (`*.tmp` + `os.replace`);
  - чтение JSON теперь не валит приложение при поврежденном файле (создается `.corrupt_*.bak`, запуск продолжается);
  - усилена нормализация `settings.json` (типы, диапазоны, asr_engine/model, имена устройств);
  - добавлен кэш списка аудио-устройств (снижена нагрузка на цикл прослушки);
  - `get_selected_mic_index/get_selected_output_index` теперь используют сохраненный `id` без полного рескана каждый цикл.
- Улучшена совместимость с Python 3.13+:
  - добавлен fallback `audioop_lts`, если стандартный `audioop` недоступен;
  - критичные аудио-операции обернуты в функции с fallback через `numpy`.
- Исправлена таблица команд:
  - элементы таблицы теперь связаны с реальным ключом команды (`iid=phrase`), чтобы удаление/тест не ломались из-за отображаемого текста.
- Безопасность автоклика в `Лаунчер+Play`:
  - поиск кнопки `Играть` ограничен окнами-кандидатами лаунчера (убран риск клика по чужим окнам).
- Сборка и инсталлятор:
  - `VoiceLauncher.spec` переведен на относительный путь `voice_launcher.py` и `pathex=['.']`;
  - добавлены hidden imports для `pywinauto/comtypes/pythoncom/pywintypes`;
  - `installer/VoiceLauncherInstaller.iss` избавлен от абсолютных путей (`OutputDir=output`, source через `..\dist\VoiceLauncher.exe`).
- Добавлен single-instance guard через именованный mutex:
  - повторный запуск второго экземпляра теперь корректно завершается;
  - фокус переносится на уже открытое окно.
- Инициализация трея переведена на `run_detached()` (без отдельного thread-run вызова `run()`).

### Why
- Основная проблема пользователя: модель часто слышала обрезки типа "то" вместо "танки".
- Причины: слишком жесткие пороги + короткие/шумные фрагменты + возможное обрезание VAD.

### Next Check
- Прогнать программу в реальном режиме и проверить 10 повторов фраз:
  - "танки", "запрет", "ключи".
- Если останутся промахи: добавить режим пользовательских алиасов для каждой команды (ручные варианты фразы).

### Validation
- `py -3.12 -m py_compile voice_launcher.py` — OK.
- Smoke-run: приложение стартует и держится в фоне (процесс жил 6 секунд без падения).
- Smoke-run после добавления режима `Лаунчер+Play` — OK (процесс стартует, UI живой).
- В `.venv312` установлено: `pywinauto`, `pywin32`, `comtypes` (автоклик готов к работе).
- Диалог "Добавить команду голосом": кнопка `Записать` снова отображается (launcher-поля скрываются до включения режима).
- `py -3.12 -m py_compile voice_launcher.py` после улучшений записи — OK.
- `py -3.12 -m py_compile voice_launcher.py` после фикса повторного старта лаунчера — OK.
- Проверка зависимостей: `pywinauto 0.6.9`, `SpeechRecognition 3.14.6`, `faster-whisper 1.2.1`, `PyAudio 0.2.14`.
- Повторный запуск второго экземпляра: второй процесс завершает запуск (single-instance работает).
- После фиксов BOM/кодировки фразы команд восстанавливаются корректно (`запрет`, `включи игру`).
- Перезапуск после фикса кракозябр: приложение стартует на чистых данных (PID в текущем запуске подтвержден).
- Полная компиляция `.py` в проекте: `py -3.12 -m compileall -q .` — OK.
- Повторный запуск второго экземпляра: второй запуск завершается в пределах 2 сек (mutex работает).
- Тест поврежденного `commands.json`: приложение запускается и не падает.
- Пересборка exe: `python -m PyInstaller --noconfirm VoiceLauncher.spec` — OK, новый `dist/VoiceLauncher.exe` создан.
- Smoke-тест exe (`dist/VoiceLauncher.exe`): процесс успешно стартует.

### 2026-03-10 04:20 | Launcher Play Reliability Hotfix
- Исправлен сценарий, когда при пустом фильтре окна автоклик не доходил до лаунчера:
  - добавлен многоуровневый выбор окон (title hints + fallback на новые окна + активное окно);
  - улучшен матчинг подсказок (`WarThunder` ↔ `War Thunder`, camelCase/underscore варианты).
- Улучшен поиск и нажатие кнопки `Играть`:
  - ранжирование контролов (Button/Hyperlink/Custom/Text) с fuzzy-сопоставлением подписи;
  - каскад методов клика: `invoke` -> `click_input`/`click` -> клик в центр -> `Enter`/`Space`.
- Добавлен защитный ретрай клика (до 6 попыток с cooldown), чтобы редкие промахи UIA не ломали запуск.
- Добавлена диагностика `launcher_automation.log` (в каталоге данных приложения): старт, клик-метод, kick, timeout, ошибки.

### Validation (2026-03-10 04:20)
- `py -3.12 -m py_compile voice_launcher.py` — OK.
- Smoke-run `voice_launcher.py` — процесс стартует и держится.
- Повторная сборка после финального safety-фикса клика без caption: `python -m PyInstaller --noconfirm VoiceLauncher.spec` — OK.
- Smoke-тест `dist/VoiceLauncher.exe`: стартовый процесс живой через 6 сек, single-instance цепочка запускается корректно.
### 2026-03-10 04:35 | Dev Continuity Logging Pack
- Added persistent runtime diagnostics files in app storage:
  - `runtime.log` (app lifecycle + actions + launch results)
  - `asr_events.log` (recognized candidates / match-no-match)
  - `dev_session_snapshot.json` (startup/save snapshots for quick resume)
  - existing `launcher_automation.log` retained for launcher auto-click flow.
- Added auto log rotation (up to 4 backups) to prevent unlimited file growth.
- Added helper docs: `DEV_CONTINUITY.md`.
- Added helper script: `dev_tools/collect_logs.ps1` to export all key logs/configs into `dev_logs/dump_YYYYMMDD_HHMMSS`.
- Added log files in app storage and verified creation on startup:
  - `%APPDATA%\VoiceLauncher\runtime.log`
  - `%APPDATA%\VoiceLauncher\asr_events.log`
  - `%APPDATA%\VoiceLauncher\dev_session_snapshot.json`
- Added continuity helper files:
  - `DEV_CONTINUITY.md`
  - `dev_tools/collect_logs.ps1`
- Rebuilt `dist/VoiceLauncher.exe` after logging updates and launched it successfully.
- Test export: `dev_tools/collect_logs.ps1` created `dev_logs/dump_20260310_043048`.
### 2026-03-10 04:44 | Anti-Duplicate Launch Gate
- Fixed repeated multi-window launches for one voice phrase.
- Added per-command launch gate:
  - cooldown window (`debounce_seconds`, default 2.8s)
  - single-instance lock (`single_instance`, default true)
  - while target EXE process is running, repeated voice launch is blocked.
- Added Windows process scan cache (`tasklist`) to avoid heavy polling each phrase.
- Gate integrated into `launch_command()` for all modes (normal/admin/launcher_play).
- Expected behavior now: command can launch again only after target app is closed (plus short debounce).
### 2026-03-10 04:55 | Visual Refresh + Desktop Shortcut
- UI restyled to violet metallic palette with orange button borders.
- Fonts enlarged and softened (script-style headers/buttons).
- Hero subtitle text updated with cleaner Russian wording.
- Main window size increased for better readability.
- Table column `Режим запуска` widened to avoid clipping (`Лаунчер + Play` now fully visible).
- Desktop shortcut created:
  - `<USER_HOME>\Desktop\Voice Launcher.lnk`
  - target: `<REPO_ROOT>\dist\VoiceLauncher.exe`
  - icon from local PC image converted to: `<USER_HOME>\AppData\Roaming\VoiceLauncher\desktop_custom_icon.ico`
- Rebuilt exe and launched updated app.
### 2026-03-10 19:10 | Launcher Anti-Spam + Cold Start Fix
- Reduced first-run recognition lag:
  - added cold-start fallback to Google while Whisper warms up asynchronously.
- Hardened launcher mode against duplicate windows:
  - launcher mode debounce raised to at least 12s;
  - if launcher process already exists, command is blocked by launch gate;
  - launcher-play worker no longer aggressively re-launches every 8s;
  - limited re-kick only when no launcher window/process found, max 2 attempts.
- Added voice-trigger duplicate suppression in listener:
  - same phrase repeated within guard window is ignored;
  - guard windows: launcher 18s, admin 6s, normal 2.8s.
- Rebuilt and started updated `dist/VoiceLauncher.exe`.
