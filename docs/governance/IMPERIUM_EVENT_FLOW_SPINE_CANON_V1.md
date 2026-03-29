# IMPERIUM_EVENT_FLOW_SPINE_CANON_V1

Status:
- class: `foundation_event_flow_channel`
- mutability: `immutable_by_default`
- change_authority: `EMPEROR_ONLY`
- implementation_state: `bounded_event_spine_active_not_full_enterprise_bus`

Purpose:
- provide a low-cost truthful event spine for IMPERIUM control surfaces,
- route meaningful state transitions without heavy always-on overhead.
- keep living-flow readability for owner: event -> assessment -> case/insight -> stage movement -> owner review.

Scope:
1. step transitions and checkpoint milestones,
2. product stage movement in Factory of Imperium,
3. evolution signal births and candidate promotion events,
4. inquisition alerts and heresy-case creation,
5. dashboard refresh triggers,
6. diff/preview generation triggers,
7. continuity tracker updates.

Event classes (minimum):
1. `STEP_TRANSITION`,
2. `FACTORY_STAGE_TRANSITION`,
3. `EVOLUTION_SIGNAL`,
4. `INQUISITION_ALERT`,
5. `HERESY_CASE`,
6. `DASHBOARD_REFRESH_TRIGGER`,
7. `DIFF_PREVIEW_TRIGGER`,
8. `CONTINUITY_UPDATE`.

Channel model:
1. default mode: `QUIET_HEARTBEAT`,
2. changed-sector mode: `EVENT_TRIGGER`,
3. deep mode: `EXPLICIT_AUTHORIZATION_ONLY`.

Routing law:
1. pointer/manifest/signal first,
2. avoid bulky payload churn in default operation,
3. event summaries are mandatory,
4. changed-sector routes are mandatory for dashboard readability,
5. raw logs stay secondary and bounded.

Living-flow minimum:
1. flow-chain state must expose `ACTIVE/WAIT/BLOCKED/PROVEN`,
2. changed-sector routes must expose route status and hit count,
3. owner review trigger count must be explicit,
4. transition markers (latest proof/risk/blocker) must stay source-linked.
5. signal vessels between Factory/Evolution/Inquisition/Owner queue must remain explicit.
6. bloodflow profile (quiet heartbeat + changed-sector trigger) must remain visible.

Persistence law:
1. event tail is persisted to bounded JSONL/live surfaces,
2. summary surfaces are generated for owner readability,
3. runaway logging must be prevented by retention limits.

Boundary:
1. no fake full bus claim while deeper bus is not implemented,
2. no event-class inflation without repo-visible source surface,
3. event spine cannot overwrite sovereign canon by itself.
