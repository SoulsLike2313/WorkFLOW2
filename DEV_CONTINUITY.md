# Dev Continuity Notes

This project now writes persistent diagnostics into the app storage directory:

- runtime log: `%APPDATA%\\VoiceLauncher\\runtime.log`
- ASR events: `%APPDATA%\\VoiceLauncher\\asr_events.log`
- launcher automation: `%APPDATA%\\VoiceLauncher\\launcher_automation.log`
- session snapshot: `%APPDATA%\\VoiceLauncher\\dev_session_snapshot.json`
- commands db: `%APPDATA%\\VoiceLauncher\\commands.json`
- settings db: `%APPDATA%\\VoiceLauncher\\settings.json`

Quick resume checklist:

1. Read `CHECKPOINT.md`
2. Read the latest `%APPDATA%\\VoiceLauncher\\runtime.log`
3. Read `%APPDATA%\\VoiceLauncher\\asr_events.log`
4. Open `%APPDATA%\\VoiceLauncher\\dev_session_snapshot.json`

Build command:

`C:\\Users\\PC\\.venv312\\Scripts\\python.exe -m PyInstaller --noconfirm VoiceLauncher.spec`

Run command (dev):

`C:\\Users\\PC\\.venv312\\Scripts\\python.exe E:\\CVVCODEX\\voice_launcher.py`
