# Voice Pipeline (Preparation Layer)

## What Is Working
- Speaker grouping and sample bank:
  - `app/voice/speaker_grouping.py`
  - `app/voice/voice_sample_bank.py`
- Voice linking + validation:
  - `app/voice/voice_linker.py`
- Mock synthesis attempts with per-speaker profile metadata:
  - `app/voice/synthesis_mock.py`
- Attempt history persistence:
  - `voice_attempt_history` table
- Audio analysis foundation integrated into voice pass:
  - `app/audio/analysis_service.py`
  - `audio_analysis_results` table
- Sync prep integrated into voice pass:
  - `app/sync/*`
  - `sync_plans` table

## New Foundation Blocks
- `app/voice/speaker_profile_bank.py`
- `app/voice/prosody_hints.py`
- `app/voice/dubbing_prep.py`
- `app/voice/voice_comparison.py`

## UI Visibility
- Existing `Voice` tab remains operational.
- New labs:
  - `Audio Analysis Lab` tab
  - `Sync Review` tab

## Honest Status
- Synthesis mode is still `mock_demo_tts_stub`.
- This is a preparation/evidence layer for future dubbing, not final production dubbing.
- No speech cloning/lip-sync/full phoneme alignment claim.

