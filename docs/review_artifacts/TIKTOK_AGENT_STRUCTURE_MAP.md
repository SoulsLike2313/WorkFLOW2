# TikTok Agent Structure Map

## Product Root

`projects/wild_hunt_command_citadel/tiktok_agent_platform`

## Layered Layout

```text
tiktok_agent_platform/
  PROJECT_MANIFEST.json
  README.md
  CODEX.md
  run_project.ps1
  core/
    PROJECT_MANIFEST.json
    README.md
    CODEX.md
    app/
    scripts/
    runtime/
    external_data/
    run_setup.ps1
    run_user.ps1
    run_developer.ps1
    run_verify.ps1
    run_update.ps1
  agent/
    PROJECT_MANIFEST.json
    README.md
    app.py
    ui_main.py
    automation_engine.py
    worker.py
    run_project.ps1
    run_setup.ps1
    runtime/
```

## Responsibility Split

Core layer (`core/`):

- verification gate and readiness model
- update/patch flow
- structured diagnostics and audit services
- UI-QA toolchain and artifacts

Agent layer (`agent/`):

- operator UX and control surface
- profile/session scheduling and queue execution
- TikTok action orchestration
- integration calls into core layer

## Shared Product Contracts

- Root manifest and workspace registry are now product-level, not layer-level.
- Layer manifests remain for local machine readability and tooling transparency.
- Product run entrypoint delegates into layer-specific scripts.
