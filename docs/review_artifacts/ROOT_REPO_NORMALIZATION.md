# Root Repository Normalization

## Scope
This artifact covers root-level normalization only.

## What Was Wrong In The Old Root README
1. It mixed governance and operations without a strict root-first navigation path.
2. Root folders (`docs`, `projects`, `scripts`) were not presented as a clean operator map.
3. Active module priority was present but not enforced as the default workflow.
4. Secondary projects could still be interpreted as near-equal focus without status-first guidance.
5. Manifest linkage existed but was not framed as the primary source-of-truth route.

## What Was Corrected
1. Root README was fully rewritten as a repository map.
2. Active module was made explicit and primary:
   - `projects/wild_hunt_command_citadel/shortform_core`
3. Root-level responsibilities were clarified for:
   - `docs/`
   - `projects/`
   - `scripts/`
   - `workspace_config/`
   - `runtime/`
4. A strict status model was introduced in the root narrative:
   - active / supporting / experimental / legacy
5. Root README now routes users directly to:
   - `workspace_config/workspace_manifest.json`
   - `workspace_config/codex_manifest.json`
   - project `PROJECT_MANIFEST.json`
   - active module README

## Old Sections Removed or Replaced
The old root README structure was replaced in full.
Legacy or less-effective root sections were removed/replaced by the new map model, including:
- workspace-control-centric blocks without root map clarity
- generic registry prose without explicit operator priority
- verbose verification descriptions not centered on active-module entrypoints
- duplicate root/project detail mixing

In practical terms, the previous layout was replaced with:
- active module first
- root structure map
- project status hierarchy
- manifest-first navigation
- concise root entrypoints

## Why The New Version Is Better
1. It is a true repository map instead of a mixed policy narrative.
2. It enforces active-module-first workflow.
3. It makes secondary projects clearly secondary.
4. It links root navigation to machine-readable manifests.
5. It is portable and environment-agnostic.

## Normalization Validation
- No absolute local disk paths in root README.
- No `.exe` references in root README.
- No legacy launch references as root-default guidance.
