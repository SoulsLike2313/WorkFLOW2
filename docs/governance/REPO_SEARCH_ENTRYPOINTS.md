# REPO_SEARCH_ENTRYPOINTS

Status:
- version: `v1`
- scope: `P2 search acceleration fallback`
- root: `E:\CVVCODEX`
- objective: `faster policy-safe search/read without broad unrestricted scans`

## 1) Friction Model (Observed)

1. `rg` calls can fail in this environment (`Access is denied`) even when binary is present.
2. broad recursive shell search patterns increase policy rejection risk.
3. repeated full-surface rereads cause avoidable latency and context churn.
4. heavy documents (manifests/review archives/runtime) should be staged, not scanned first.

## 2) Search Surface Classes

### FAST ENTRY

Use first:
1. `README.md`
2. `MACHINE_CONTEXT.md`
3. `REPO_MAP.md`
4. `docs/INSTRUCTION_INDEX.md`
5. `docs/CURRENT_PLATFORM_STATE.md`
6. `docs/NEXT_CANONICAL_STEP.md`

### LOAD-BEARING

Primary policy/contracts/scripts:
1. `docs/governance/*`
2. `workspace_config/*`
3. `scripts/*`
4. `scripts/validation/*`

### SECONDARY / HISTORICAL

Only when needed:
1. `docs/review_artifacts/*`
2. runtime export/staging/history surfaces

### LARGE / HEAVY (staged reading)

Stage in chunks:
1. `workspace_config/codex_manifest.json`
2. `workspace_config/workspace_manifest.json`
3. `runtime/repo_control_center/*`
4. `docs/review_artifacts/*`

## 3) Canonical Search Zone Manifest

Machine-readable anchor:
1. `workspace_config/search_zone_manifest.json`

This manifest defines:
1. zone ids,
2. path sets,
3. safety blocks,
4. default search order,
5. heavy-surface controls.

## 4) Canonical Safe Search Helper

Entrypoint:
1. `scripts/search_repo_safe.py`

Purpose:
1. search bounded zones first,
2. enforce disallowed path patterns,
3. avoid unrestricted broad scans,
4. provide JSON evidence output.

## 5) Fallback Hierarchy

1. Read FAST ENTRY surfaces.
2. Read workspace manifests/maps (`workspace_manifest`, `codex_manifest`) in staged manner.
3. Search bounded load-bearing zones via `search_repo_safe.py`.
4. Expand to heavy/secondary zones only if unresolved.
5. Use bundle index/reading-order surfaces before raw deep sweep.

## 6) Usage Patterns

List zones:

```powershell
python scripts/search_repo_safe.py --show-zones
```

Default bounded search:

```powershell
python scripts/search_repo_safe.py --query "governance_acceptance" --json-only
```

Specific zone search:

```powershell
python scripts/search_repo_safe.py --query "Analytics Department" --zone governance_core --json-only
```

Heavy/secondary opt-in:

```powershell
python scripts/search_repo_safe.py --query "stale" --zone review_artifacts --include-secondary --include-heavy --max-results 50 --json-only
```

## 7) Safe/Unsafe Search Shape Guidance

Safe by default:
1. bounded zone search via helper,
2. narrow file/path targets,
3. staged expansion.

Risky/high-friction:
1. unrestricted recursive scans over whole repo,
2. heavy chained one-liners,
3. direct traversal of blocked runtime/export/import zones.

## 8) Quality Constraint

Acceleration must not reduce evidence quality.
Preserve:
1. context density,
2. contradiction visibility,
3. gaps visibility,
4. `OBSERVED/INFERRED/NOT-PROVEN` discipline in reports.

## 9) Anchors

1. `docs/governance/CODEX_ACCELERATION_PLAN_SAFE_MODE_V1.md`
2. `workspace_config/search_zone_manifest.json`
3. `scripts/search_repo_safe.py`
