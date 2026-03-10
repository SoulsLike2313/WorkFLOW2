# CODEX.md

## Project identity

This repository is a modular Python core for short-form content operations.
It is designed as a decision-support and orchestration base for TikTok / Reels / Shorts style workflows.

This project is not an anti-detection tool, not a traffic obfuscation system, and not a platform evasion framework.

Its purpose is to:
- track account and content state
- store creatives, metrics, hypotheses, references, and tasks
- evaluate creatives with structured logic
- generate action plans
- remain easy to extend into API, UI, persistence, and agent runtime layers

## Expected structure

app/
  __init__.py
  models.py
  config.py
  analytics.py
  registry.py
  planner.py
  demo_data.py
  io_utils.py
  main.py
  db.py
  repository.py
  schemas.py
  api.py
  bootstrap_v2.py
README.md
CODEX.md
PROMPT_FOR_CODEX.txt
requirements.txt

## Design rules

Keep these layers separated:
- data models
- config
- analytics / decision logic
- state storage
- planning
- I/O and serialization
- transport / API
- UI

Do not mix business logic with UI, transport, or persistence code.