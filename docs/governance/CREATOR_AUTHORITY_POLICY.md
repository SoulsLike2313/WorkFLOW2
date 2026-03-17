# Creator Authority Policy

## Purpose

Define how canonical creator authority is detected without storing sensitive local authority paths in tracked repository files.

## Canonical Detection Contract

- env var name: `CVVCODEX_CREATOR_AUTHORITY_DIR`
- marker filename: `creator_authority.json`
- required marker schema:
  - `authority_mode = "creator"`
  - `profile_version = "v1"`
  - `machine_role = "canonical_creator_machine"`

Detection rules:

1. env var missing -> authority absent
2. env var present but directory missing -> authority absent
3. directory exists but marker missing -> authority absent
4. marker present but invalid -> authority absent
5. env+directory+valid marker -> authority present

## Creator-Only Operations

- declare canonical completion
- declare governance acceptance pass
- perform final integration acceptance/rejection from inbox review
- approve protected governance-layer changes
- approve canonical state transition to next stage

## Forbidden For Non-Creator Modes

- canonical completion claim
- governance override
- final acceptance of external blocks
- direct canonical merge from external helper output without integration gate

## Privacy Rule

- tracked repository must never store real creator authority directory path
- repository stores only detection contract logic (env var, marker name, marker fields)

