# IMPERIUM_LOW_RESOURCE_CHANNEL_DISCIPLINE_V1

Status:
- class: `foundation_resource_discipline`
- mutability: `immutable_by_default`
- change_authority: `EMPEROR_ONLY`

Purpose:
- keep evolution/inquisition/event-flow/diff-preview channels believable and sustainable on local machine resources.

Operating tiers:
1. `ALWAYS_ON_SAFE`: quiet heartbeat summaries only,
2. `EVENT_TRIGGER_ONLY`: changed-sector refresh logic,
3. `MANUAL_DEEP_MODE`: explicit owner/GPT authorization only.

Mandatory constraints:
1. no whole-world rescans when changed-sector scope is enough,
2. no high-frequency heavy watchers for preview/diff,
3. no heavy pseudo-3D loops,
4. bounded retention for event tails and preview packs,
5. explicit disclosure for not-yet-implemented automation.

Truth boundary:
1. resource-saving must not hide gaps,
2. reduced frequency must not be misrepresented as realtime,
3. control/validation/evidence discipline remains mandatory.

