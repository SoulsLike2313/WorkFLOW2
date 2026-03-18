# EMPEROR_MACHINE_ACCEPTANCE_PREPARATION_MEMO

- generated_at_utc: `2026-03-18T14:16:00Z`
- memo_type: `pre_sovereign_recommendation`
- decision_authority: `Emperor machine only`

## 1) What Emperor Node Must Re-Verify After Return

On Emperor node (`E:\CVVCODEX`) run:

1. `python scripts/validation/detect_node_rank.py`
2. `python scripts/validation/check_sovereign_claim_denial.py` with requested claim classes
3. `python scripts/repo_control_center.py full-check`
4. `python scripts/validation/run_constitution_checks.py`

Required check focus:
1. canonical root validity;
2. sovereign proof presence and validity;
3. rank-consistent claim admissibility;
4. reintegration scope and identity integrity.

## 2) How Emperor Node Confirms Its Rank

1. canonical root context must validate to `E:\CVVCODEX`;
2. Primarch authority path must validate;
3. Emperor local proof marker chain must validate;
4. no ambiguity/unknown states in rank proof chain.

If any fails:
- no Emperor sovereign claims.

## 3) How Primarch/Astartes Documents Should Be Accepted

1. treat Primarch documents as proposals/recommendations, not sovereign decisions;
2. treat Astartes documents as bounded execution evidence only;
3. enforce claim-class + issuer identity/signature status before acting;
4. require reintegration checklist completion prior to any acceptance.

## 4) What Must Not Be Auto-Accepted Yet

1. sovereign policy change claims from non-Emperor issuers;
2. canonical acceptance claims from non-Emperor issuers;
3. unsigned/invalid identity-bound authority documents;
4. warrant/charter-sensitive requests without valid authority chain.

## 5) Hardening Outcomes Already Usable As Recommendations

1. rank detection is now machine-executable and fail-closed by root/authority/proof logic;
2. sovereign claim denial gate is executable and rank-aware;
3. constitutional status surface now includes rank/root/claim-denial signals.

## 6) What Must Be Proved Locally On Emperor Machine

1. true Emperor proof chain validity with local-only proof artifacts;
2. operational correctness of issuer identity/signature checks for sovereign-sensitive documents;
3. warrant/charter enforcement adequacy for Astartes execution admission.

## 7) What Must Be Checked Specifically In `E:\CVVCODEX`

1. root context exact match to canonical path assumption;
2. external authority and sovereign proof paths resolve correctly;
3. no path drift ambiguity in runtime/admission evidence;
4. repo-control and constitution outputs align with rank-aware denial behavior.

## 8) Safe Mirror Use During Emperor Acceptance

`WorkFLOW2` must be used only as:
1. external orientation surface;
2. controlled export/bundle reference surface.

`WorkFLOW2` must not be used as:
1. sovereign rank proof source;
2. sovereign decision authority source.
