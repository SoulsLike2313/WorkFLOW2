# DEPARTMENT_MAP_V1

Status:
- map_version: `v1.1.0`
- map_type: `activation-aware department map`
- model: `one active department + seed departments`

Evidence status legend:
- `PROVEN`
- `REUSABLE`
- `DESIGNED`
- `NOT YET IMPLEMENTED`

## 1) Activation split

### Active now

1. `Analytics Department` (`PROVEN`)

### Seed now (exists, bounded, not full automation)

1. `Engineering Department` (`REUSABLE`)
2. `Verification Department` (`REUSABLE`)
3. `Release & Integration Department` (`REUSABLE`)
4. `Tooling & Infrastructure Department` (`REUSABLE`)
5. `Product Intelligence / Research Department` (`REUSABLE`)
6. `Growth / Distribution Department` (`ACTIVE` seed layer)

## 2) Department matrix

| Department | Mission | Inputs | Outputs | Required authority | Must never do | Activation rule | State now | Consumes | Emits |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Analytics Department | Intake, primary audit, technical map, initial roadmap | idea/demo/raw app/source bundle | Technical Map Bundle, gap map, routing proposal, department activation proposal | Primarch operational oversight + bounded Astartes execution | claim sovereign acceptance, mutate constitution, fake readiness | default entry head for new product flow | `ACTIVE` | Intake Bundle, prior project evidence | Technical Map Bundle, Department Synthesis Bundle, Handoff Bundle |
| Engineering Department | Convert approved roadmap into implementation changes | approved technical map, bounded tasks | implementation artifacts, build/test deltas, engineering synthesis | Primarch bounded command + Astartes task slots | self-approve release or bypass verification | activates for wave execution after owner-approved checkpoints | `SEED` | Task Bundle, Handoff Bundle | Astartes Result Bundle, Department Synthesis Bundle |
| Verification Department | Validate correctness, reliability, safety, regressions | engineering outputs, test targets | verification report, blocker incidents, pass/fail recommendation | Primarch verification lead + Astartes execution | certify without evidence, ignore red tests | activated when implementation enters validation | `SEED` | Department Synthesis Bundle, Task Bundle | Blocker/Incident Bundle, Completion Bundle candidate |
| Release & Integration Department | Package release, control integration handoff, release evidence | verified candidate, release plan | release package, release readiness report, integration handoff | Primarch release authority under sovereign boundaries | canonical acceptance claim, skip required gates | activated after verification pass candidate | `SEED` | Completion Bundle, verification evidence | Release Bundle, Handoff Bundle |
| Tooling & Infrastructure Department | Improve delivery speed via deterministic tooling, scripts, CI-like local flows | friction reports, recurring bottlenecks | tooling patches, automation helpers, infra recommendations | Primarch tooling direction + bounded execution | force broad migrations without approval | activated when recurring friction blocks throughput | `SEED` | Blocker/Incident Bundle, operational metrics | Task Bundle templates, infra synthesis |
| Product Intelligence / Research Department | Product hypothesis validation, UX/market/context constraints | product goals, analytics maps, user context | decision memos, product constraints, prioritization recommendations | Primarch research direction | claim release readiness by itself | activated when product ambiguity blocks roadmap quality | `SEED` | Intake Bundle, Technical Map Bundle | Department Synthesis Bundle, Handoff Bundle |
| Growth / Distribution Department | Build starter distribution and early sales entry artifacts for hardening-ready products | product technical map, chosen path, owner positioning hints, product assets | Product Narrative Pack, Channel Starter Pack, Campaign Starter Plan, Product Promotion File, Early Sales Readiness Note | Primarch growth oversight + owner gate control | run fake full automation, publish unproven claims, override owner positioning | seed-active after hardening baseline and owner positioning gate | `SEED` | Technical Map Bundle, owner-approved positioning hints | Channel Starter Pack, Campaign Starter Plan, Product Promotion File |

## 3) Canonical boundaries

1. `PROVEN`: current real operational head remains `Analytics Department`.
2. `ACTIVE`: seed departments exist as bounded operational scaffolds, not full autonomous plants.
3. `ACTIVE`: Growth / Distribution is a real seed layer, not a fake fully operational empire.
4. `NOT YET IMPLEMENTED`: automatic interdepartment runtime scheduler and full throughput conveyor.

## 4) Owner-facing explanation

1. Сейчас фабрика не притворяется, что все цеха работают как fully operational units.
2. Один operational head (`Analytics`) ведёт поток, остальные цеха существуют как seed-слой и видимы в owner window.
3. Это снижает хаос и даёт контролируемый переход к масштабированию.
