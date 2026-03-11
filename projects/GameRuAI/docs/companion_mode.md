# Companion Mode (Safe Sidecar MVP)

## Scope (Implemented)
Companion mode is a safe sidecar flow:
- launch external game/process
- track session per `project_id`
- watch game folder for file changes
- store watched events
- trigger quick re-index for changed text/config files
- show session and events in UI

Modules:
- `app/companion/launcher.py`
- `app/companion/process_monitor.py`
- `app/companion/file_watch_service.py`
- `app/companion/session_registry.py`

## Security Boundaries
Companion mode does **not** do:
- runtime injection
- memory hacking
- code injection
- game binary modification

## Data Persistence
Tables:
- `companion_sessions`
- `watched_file_events`

Stored fields include:
- `project_id`, `session_id`, `executable_path`, `watched_path`
- process status / pid / start-end timestamps
- watched event type and file path

## UI Flow
1. Open `Companion` tab.
2. Set executable path and watched path.
3. Launch session.
4. Edit files in watched folder.
5. Poll session.

Visible results:
- session status widget
- quick re-index counter
- sessions table
- watched file events table

## Quick Re-Index Behavior
When modified/created files are detected:
- classifier checks file type
- only text/config files are re-indexed
- changed files are re-extracted
- language detection and translation are refreshed for those entries
- backend run metadata is stored in `translation_backend_runs`

## Working vs Fallback/Demo
Working now:
- process launch/monitor/stop lifecycle
- watched file capture
- quick re-index on changed fixture files

Current limitations:
- watcher is polling-based (not OS-native event API)
- no binary/runtime hooks
- quick re-index focuses on textual pipeline only
