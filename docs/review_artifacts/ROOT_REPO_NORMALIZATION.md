# Root Repository Normalization

## Scope
This review artifact documents the root-level normalization pass only.

## What Was Wrong In The Previous Root README
1. It did not provide a clear root-level orientation for `docs/`, `projects/`, and `scripts/` as operator-first entry points.
2. It was governance-heavy, but less explicit as a practical repository map for daily usage.
3. Active module priority was present, but not clearly separated from secondary project status in a concise operator view.
4. The flow between root README and workspace manifests was present but not structured as a strict "map -> manifest -> project" navigation path.

## What Was Fixed
1. Root README was fully rewritten as a repository map.
2. Active module was made explicit as the main engineering target:
   - `projects/wild_hunt_command_citadel/shortform_core`
3. A dedicated "Active vs Secondary Modules" section now explains status hierarchy from `workspace_manifest.json`.
4. Root-level responsibilities are now clearly separated:
   - `docs/`
   - `projects/`
   - `scripts/`
   - `workspace_config/`
   - `runtime/`
5. Root README now routes users directly to:
   - workspace manifests,
   - active project README,
   - active project manifest,
   - canonical startup/verify/update entrypoints.

## Removed As Outdated Or Redundant
The previous root README sections were replaced in full. The normalization removed the old structure and rebuilt it around:
- workspace map first,
- active module first,
- manifest-linked navigation,
- concise operational entrypoints.

No absolute local disk paths are used.
No EXE path references are used.
No legacy launch references are used as primary guidance.

## Why The New Version Is Better As A Repository Map
1. It is operator-oriented and task-oriented from the root.
2. It establishes clear priority: active module first, secondary modules by status.
3. It reduces ambiguity by linking root navigation to machine-readable manifests.
4. It avoids duplicated project internals and points readers to project-level docs where details belong.
5. It is portable and environment-agnostic (no machine-specific absolute paths).
