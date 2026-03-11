# README Before/After Summary

## Before (previous root README)
- already cleaned of old absolute paths, but still mixed map-level and module-level concerns;
- repository-map role was implicit, not explicit;
- launch/update guidance was valid but less normalized against active module docs.

## After (new root README)
- root README is strictly repository map + canonical entrypoint guide;
- active module explicitly declared as `projects/wild_hunt_command_citadel/shortform_core`;
- environment setup is shown before launcher commands;
- user mode and developer mode are clearly separated;
- verification gate policy is explicit and strict;
- update flow is split into user-facing local script path and developer integration note;
- canonical deep docs are explicitly referenced (`shortform_core/README.md`, `shortform_core/CODEX.md`).

## Removed or normalized section behavior
- normalized vague secondary/legacy framing into explicit component responsibility;
- reduced root-level endpoint detail overload to avoid root/module drift;
- replaced mixed launch wording with deterministic run sequence.
