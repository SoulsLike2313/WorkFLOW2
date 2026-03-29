# ASTARTES_ENTRY_MANIFEST_SPEC

Status:
- spec_version: `v1`
- scope: `mandatory entry manifest for Astartes department binding`
- model: `owner-approved force visibility before task routing`

Assertion labels:
- `PROVEN`
- `REUSABLE`
- `DESIGNED`
- `NOT YET IMPLEMENTED`

## 1) What is Entry Manifest

Entry Manifest is a mandatory capability declaration bundle created when Astartes is bound to a department.

Purpose:
1. Primarch sees real execution capacity before assignment.
2. Task routing is based on facts, not assumptions.
3. Overload and mismatch risk decreases.

## 2) Mandatory fields

1. `manifest_id`
2. `astartes_node_id`
3. `department_binding_id`
4. `timestamp_utc`
5. `hardware_profile`
6. `software_profile`
7. `tooling_profile`
8. `runtime_capability`
9. `stack_readiness`
10. `local_limits`
11. `speed_profile`
12. `supported_languages_frameworks`
13. `current_load_and_availability`
14. `known_risks`
15. `trust_note`
16. `evidence_refs`

## 3) Hardware/software/tooling expectations

### Hardware profile

Must include:
1. CPU class;
2. RAM;
3. storage and free space;
4. optional accelerator/GPU info.

### Software profile

Must include:
1. OS baseline;
2. core runtimes (python/node/etc.);
3. package manager availability.

### Tooling profile

Must include:
1. VCS tooling;
2. build/test tools;
3. static analysis tools;
4. packaging/export tools if relevant.

## 4) Stack readiness format

For each key stack item:
1. `READY`
2. `PARTIAL`
3. `MISSING`

Each non-ready status must include reason and mitigation note.

## 5) Local limits and speed profile

Manifest must explicitly state:
1. max task complexity comfortable range;
2. known bottlenecks;
3. expected turnaround profile (`fast`, `medium`, `slow`) by task class.

## 6) Trust note

Trust note must include:
1. known weak zones of this node;
2. classes of tasks where extra verification is required;
3. confidence posture not overstated.

## 7) Why this helps Primarch

With entry manifests Primarch can:
1. avoid impossible assignments;
2. route high-risk tasks to better-prepared slots;
3. plan realistic sprint/batch schedules;
4. detect capacity gaps early.

## 8) Validation requirements

Entry Manifest is valid only if:
1. mandatory fields are present;
2. evidence refs are resolvable;
3. old/stale manifest is replaced on rebinding or major capability drift.

## 9) Evidence status

1. `DESIGNED`: field schema and required discipline.
2. `NOT YET IMPLEMENTED`: automatic runtime generator/validator for this manifest.

