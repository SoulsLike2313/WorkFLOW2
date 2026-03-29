# Integration Guide

## Purpose

Run a local-only owner dashboard over bundle truth.

## Quick start

```powershell
powershell -ExecutionPolicy Bypass -File shared_systems/factory_observation_window_v1/run_local.ps1
```

Default active source:

1. `runtime/chatgpt_bundle_exports/tiktok_wave1_tranche1_live_ongoing_checkpoint_manual_safe_bundle_latest.zip`
2. fallback (explicitly secondary): `runtime/chatgpt_bundle_exports/tiktok_wave1_kickoff_checkpoint_manual_safe_bundle_latest.zip`
3. required companion (PATH B): `runtime/chatgpt_bundle_exports/tiktok_agent_owner_gate_review_manual_safe_bundle_20260321T202031Z.zip`

Custom bundle:

```powershell
powershell -ExecutionPolicy Bypass -File shared_systems/factory_observation_window_v1/run_local.ps1 -BundlePath "runtime/chatgpt_bundle_exports/<bundle>.zip"
```

Then open:

- [http://127.0.0.1:8777](http://127.0.0.1:8777)

## Security default

- localhost bind only
- no WAN exposure
- no external upload path
