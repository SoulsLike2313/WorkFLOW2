# Learning / Adaptation Flow

## Goal
Make improvement decisions observable in UI and persisted in SQLite.

## Loop
1. Initial translation is produced.
2. User edits translated text (`Translation` tab).
3. Correction is saved into:
   - `correction_history`,
   - `translation_memory`,
   - optionally `glossary_terms`.
4. `adaptation_events` records why/how change happened.
5. Next similar line reuses TM/glossary and improves output.

## Voice adaptation
1. `voice_profiles` describe per-speaker synthesis preferences.
2. User tweaks style/rate in `Voice` tab.
3. Updates are logged in `adaptation_events`.
4. Next voice attempts for that speaker use updated profile.

## Visibility in UI
- `Translation` tab: source, lang, ru output, quality, correction actions.
- `Learning` tab: before/after corrections + adaptation timeline.
- `Glossary` tab: learned terms.
- `Voice` tab: profile-driven voice attempt metadata and statuses.
