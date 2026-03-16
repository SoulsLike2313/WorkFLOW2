# Voice Launcher

Р“РѕР»РѕСЃРѕРІРѕР№ Р·Р°РїСѓСЃРєР°С‚РѕСЂ РїСЂРёР»РѕР¶РµРЅРёР№ РґР»СЏ Windows СЃ Р±РµР·РѕРїР°СЃРЅС‹Рј СЂРµР¶РёРјРѕРј `launcher_play`, РїРѕРґРґРµСЂР¶РєРѕР№ `admin_task`, Р»РѕРіРёСЂРѕРІР°РЅРёРµРј Рё С…СЂР°РЅРµРЅРёРµРј РїРѕР»СЊР·РѕРІР°С‚РµР»СЊСЃРєРёС… РґР°РЅРЅС‹С… РІ AppData.

## Р—Р°РїСѓСЃРє РёР· РёСЃС…РѕРґРЅРёРєРѕРІ

1. РЈСЃС‚Р°РЅРѕРІРёС‚Рµ Python 3.12+.
2. РЎРѕР·РґР°Р№С‚Рµ venv Рё СѓСЃС‚Р°РЅРѕРІРёС‚Рµ Р·Р°РІРёСЃРёРјРѕСЃС‚Рё:
   - `py -3.12 -m venv .venv`
   - `.\.venv\Scripts\Activate.ps1`
   - `python -m pip install --upgrade pip`
   - `pip install pystray pillow SpeechRecognition pyaudio pywinauto faster-whisper numpy`
3. Р—Р°РїСѓСЃРє:
   - `python voice_launcher.py`

## РЎР±РѕСЂРєР° Portable

- `.\dev_tools\build_portable.ps1 -PythonExe python`
- Р РµР·СѓР»СЊС‚Р°С‚:
  - `dist\VoiceLauncher.exe`
  - `dist\portable\` (РіРѕС‚РѕРІС‹Р№ РїР°РєРµС‚ РґР»СЏ РїРµСЂРµРЅРѕСЃР°)

## РЎР±РѕСЂРєР° Installer

1. РЈСЃС‚Р°РЅРѕРІРёС‚Рµ Inno Setup 6.
2. Р—Р°РїСѓСЃРє:
   - `.\dev_tools\build_installer.ps1 -PythonExe python`
3. Р РµР·СѓР»СЊС‚Р°С‚:
   - `installer\output\VoiceLauncherSetup.exe`

## Runtime-РґР°РЅРЅС‹Рµ

- РџРѕР»СЊР·РѕРІР°С‚РµР»СЊСЃРєРёРµ С„Р°Р№Р»С‹:
  - `%APPDATA%\VoiceLauncher\commands.json`
  - `%APPDATA%\VoiceLauncher\settings.json`
- Р›РѕРіРё:
  - `%APPDATA%\VoiceLauncher\logs\`
- Р‘СЌРєР°РїС‹ Рё СЃРЅР°РїС€РѕС‚С‹:
  - `%APPDATA%\VoiceLauncher\backups\`
  - `%APPDATA%\VoiceLauncher\snapshots\`
- Р”Р»СЏ РѕС‚Р»Р°РґРєРё РјРѕР¶РЅРѕ РїРµСЂРµРѕРїСЂРµРґРµР»РёС‚СЊ РїСѓС‚СЊ:
  - `VOICE_LAUNCHER_STORAGE_DIR=<LOCAL_STORAGE_DIR>\\VoiceLauncherData`

## РРјРїРѕСЂС‚/СЌРєСЃРїРѕСЂС‚ РїСЂРѕС„РёР»СЏ

- Р’ РѕСЃРЅРѕРІРЅРѕРј РѕРєРЅРµ РёСЃРїРѕР»СЊР·СѓР№С‚Рµ РєРЅРѕРїРєРё:
  - `Р­РєСЃРїРѕСЂС‚ РїСЂРѕС„РёР»СЏ`
  - `РРјРїРѕСЂС‚ РїСЂРѕС„РёР»СЏ`
- РџСЂРѕС„РёР»СЊ СЃРѕРґРµСЂР¶РёС‚ РєРѕРјР°РЅРґС‹ Рё РЅР°СЃС‚СЂРѕР№РєРё РІ РѕРґРЅРѕРј JSON-С„Р°Р№Р»Рµ.
- РџСЂРё РёРјРїРѕСЂС‚Рµ РґРѕСЃС‚СѓРїРµРЅ РІС‹Р±РѕСЂ:
  - Р·Р°РјРµРЅРёС‚СЊ С‚РµРєСѓС‰РёРµ РєРѕРјР°РЅРґС‹ РёР»Рё РѕР±СЉРµРґРёРЅРёС‚СЊ
  - РїСЂРёРјРµРЅРёС‚СЊ РЅР°СЃС‚СЂРѕР№РєРё РёР· РїСЂРѕС„РёР»СЏ РёР»Рё РѕСЃС‚Р°РІРёС‚СЊ Р»РѕРєР°Р»СЊРЅС‹Рµ

## Р‘РµР·РѕРїР°СЃРЅР°СЏ РЅР°СЃС‚СЂРѕР№РєР° launcher_play

1. Р’ РјР°СЃС‚РµСЂРµ РґРѕР±Р°РІР»РµРЅРёСЏ РєРѕРјР°РЅРґС‹ РІРєР»СЋС‡РёС‚Рµ `Р РµР¶РёРј Р»Р°СѓРЅС‡РµСЂР°`.
2. РЈРєР°Р¶РёС‚Рµ:
   - `РўРµРєСЃС‚ РєРЅРѕРїРєРё`
   - `Р¤РёР»СЊС‚СЂ РѕРєРЅР°` (С‡Р°СЃС‚СЊ Р·Р°РіРѕР»РѕРІРєР°)
   - `РЈРІРµСЂРµРЅРЅРѕСЃС‚СЊ РѕРєРЅР°` (СЂРµРєРѕРјРµРЅРґСѓРµС‚СЃСЏ 0.90+)
3. РЎРЅР°С‡Р°Р»Р° РІС‹РїРѕР»РЅРёС‚Рµ `Р‘РµР·РѕРїР°СЃРЅС‹Р№ С‚РµСЃС‚` (dry-run, Р±РµР· РєР»РёРєР°).
4. РџРѕСЃР»Рµ СѓСЃРїРµС€РЅРѕР№ РІРµСЂРёС„РёРєР°С†РёРё РѕС‚РєР»СЋС‡РёС‚Рµ dry-run РїСЂРё РЅРµРѕР±С…РѕРґРёРјРѕСЃС‚Рё.

## РўРµСЃС‚РёСЂРѕРІР°РЅРёРµ

- Unit/integration:
  - `python -m pytest -q`
- РџРѕРєСЂС‹С‚С‹:
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

## Workspace Isolation Startup

Use project startup preflight to enforce runtime namespace and port isolation:

```powershell
cd projects/voice_launcher
powershell -ExecutionPolicy Bypass -File .\run_project.ps1 -Mode user -PortMode fixed
```

Optional auto fallback mode (only inside project range `8100-8199`):

```powershell
powershell -ExecutionPolicy Bypass -File .\run_project.ps1 -Mode user -PortMode auto
```

