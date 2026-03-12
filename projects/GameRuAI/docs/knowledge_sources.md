# Knowledge Sources (Source-of-Truth Manager)

## Modules
- `app/knowledge/source_registry.py`
- `app/knowledge/glossary_source.py`
- `app/knowledge/tm_source.py`
- `app/knowledge/locale_rules_source.py`
- `app/knowledge/voice_profile_source.py`
- `app/knowledge/external_reference_source.py`
- `app/knowledge/source_refresh.py`

## Storage
- Table: `knowledge_sources`
- Tracks:
  - source key/type
  - version tag
  - status and health state
  - metadata
  - created/updated timestamps

## Current Usage
- Project creation registers locale/glossary/TM/voice/external reference sources.
- Glossary/TM/voice updates refresh corresponding source metadata.

## Honest Status
- Working: local source registry persistence and refresh hooks.
- Foundation only: distributed/remote source syncing.

