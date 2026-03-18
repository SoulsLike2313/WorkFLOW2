# PROOF_OUTPUT_NAMING_POLICY_V1

## Scope
Naming discipline for proof outputs used in verification, certification, and safe-share bundles.

## What Is A Proof Output
- machine-readable or report artifact that proves gate/verdict/check result.
- typical location: `runtime/repo_control_center/` and related runtime evidence paths.

## Canonical Naming Patterns
- creator-mode proofs:
  - `creator_detect_machine_mode_output.json`
  - `creator_repo_control_bundle_output.json`
  - `creator_repo_control_full_check_output.json`
  - `creator_authority_env_output.txt`
- wave-specific proofs:
  - `wave<id>_<surface>_<check>_output.json`
  - example: `wave3c_operator_mission_consistency_output.json`
- consistency outputs:
  - `*_consistency*.json`
- status snapshots:
  - `*_status.json`
- report snapshots:
  - `*_report.md`

## Allowed Suffixes
- `_output.json`
- `_status.json`
- `_report.md`
- `_checkpoint.json`
- `_history.json`
- `_audit_trail.json`
- `_consistency.json`

## Forbidden Naming Behaviors
- ambiguous generic names (`result.json`, `out.md`, `tmp_report.md`)
- conflicting names for different checks in same directory
- names without surface/check context

## Legacy Tolerance
- Existing legacy runtime names are tolerated if already referenced by policy/manifests/reports.
- Legacy files must not be used as naming template for new proof outputs.

## Low-Risk Rename Candidates (Do Not Execute Automatically)
- `wave3_operator_mission_*` style names can be normalized to explicit `wave3a|wave3b|wave3c`.
- mixed `repo_control_*` and `rcc_*` aliases can be harmonized to `repo_control_*`.

## Operational Rule
New verification/certification proofs must follow canonical patterns above unless explicitly documented exception is approved.
