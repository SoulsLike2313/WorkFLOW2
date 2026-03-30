const MODE_COMMAND = "command";
const MODE_FULL = "fullvision";
const MODE_KEY = "factory_observation_window_mode_v1";
const DEFAULT_COMPANION = "runtime/chatgpt_bundle_exports/tiktok_agent_owner_gate_review_manual_safe_bundle_20260321T202031Z.zip";

let app = {
  state: null,
  live: null,
  stateTimer: null,
  liveTimer: null,
  liveWatchdogTimer: null,
  eventSource: null,
  lastLiveTickAtEpochMs: 0,
  liveChannel: {
    mechanism: "initializing",
    status: "starting",
    note: "channel init",
    lastEventId: "",
    lastUpdateAt: ""
  },
  liveDelta: {
    hasNewEvent: false,
    latestEventId: "",
    latestEventType: "",
    latestChangedNodeId: "",
    activeRouteNodeId: ""
  },
  fullVision: {
    sectorFocus: "core_world",
    layerFocus: "overview",
    subsectorFocus: 0,
    depthFocus: "orbit"
  },
  stateSyncInFlight: false,
  lastStateSyncAtEpochMs: 0
};

const E = (id) => document.getElementById(id);
const J = async (url) => {
  const r = await fetch(url);
  if (!r.ok) throw new Error(`${url} -> ${r.status}`);
  return await r.json();
};
const S = (x) => JSON.stringify(x, null, 2);
const O = (x) => (x && typeof x === "object" ? x : {});
const A = (x) => (Array.isArray(x) ? x : []);
const H = (x) => String(x ?? "");
const esc = (x) => H(x).replace(/[&<>"']/g, (m) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", "\"": "&quot;", "'": "&#39;" }[m]));
const pv = (x) => `<span class="path-value">${esc(x || "n/a")}</span>`;
const vb = (x) => `<span class="value-block">${esc(x || "n/a")}</span>`;
const key = (x) => String(x || "").toLowerCase();

function statusRu(v) {
  const t = String(v || "UNKNOWN").toUpperCase();
  if (t.includes("CLEAN")) return "чисто";
  if (t.includes("DIRTY")) return "грязно";
  if (t.includes("AWAKE")) return "бдительность активна";
  if (t.includes("DORMANT")) return "дежурный режим";
  if (t.includes("LOCK_ASSERTED")) return "жесткий lock";
  if (t.includes("LOCK_RECOMMENDED")) return "рекомендован lock";
  if (t.includes("IN_PROGRESS")) return "идет активная работа";
  if (t.includes("RESOLVED")) return "решение подтверждено";
  if (t.includes("PENDING")) return "ожидает решения";
  if (t.includes("SEED")) return "seed-уровень";
  if (t.includes("PARTIALLY_IMPLEMENTED")) return "частично реализовано";
  if (t.includes("NOT_YET_IMPLEMENTED")) return "еще не реализовано";
  if (t.includes("ACTIVE")) return "активно";
  if (t.includes("PROVEN")) return "доказано";
  if (t.includes("BLOCKED")) return "заблокировано";
  if (t.includes("PASS")) return "проверка пройдена";
  if (t === "OK") return "норма";
  if (t.includes("WARNING")) return "предупреждение";
  return "статус зафиксирован";
}

function processRu(v) {
  const t = String(v || "UNKNOWN").toUpperCase();
  if (t.includes("PROCESS")) return "идет обработка";
  if (t.includes("WAIT")) return "ожидание";
  if (t.includes("ERROR")) return "ошибка процесса";
  if (t.includes("BLOCK")) return "блокировка";
  if (t.includes("IDLE")) return "ожидание запуска";
  return "состояние не классифицировано";
}

function processBadge(v) {
  const t = String(v || "UNKNOWN").toUpperCase();
  if (t.includes("PROCESS")) return "active";
  if (t.includes("WAIT") || t.includes("IDLE")) return "scaffolded";
  if (t.includes("ERROR") || t.includes("BLOCK")) return "nyi";
  return "partial";
}

function unknownReasonRu(v) {
  const k = String(v || "").toLowerCase();
  if (k === "not_implemented") return "не реализовано";
  if (k === "not_mapped") return "не смэпплено";
  if (k === "stale_source") return "источник устарел/недоступен";
  if (k === "owner_decision_pending") return "ожидается решение владельца";
  if (k === "unavailable_in_step_scope") return "вне scope текущего шага";
  return "причина не зафиксирована";
}

function truthClassRu(v) {
  const t = String(v || "").toUpperCase();
  if (t === "SOURCE_EXACT") return "точный источник";
  if (t.startsWith("DERIVED")) return "выведено из источников";
  if (t === "NOT_YET_IMPLEMENTED") return "еще не реализовано";
  if (t === "PLACEHOLDER") return "временная заглушка";
  if (t === "STALE_SOURCE") return "устаревший источник";
  if (t === "UNKNOWN") return "неизвестно";
  return "класс правды не задан";
}

function humanValue(v, fallback = "нет подтвержденных данных") {
  const raw = H(v || "").trim();
  if (!raw) return fallback;
  const upper = raw.toUpperCase();
  if (upper === "UNKNOWN" || upper === "N/A") return fallback;
  if (upper === "NONE") return "нет";
  if (upper === "TRUE") return "да";
  if (upper === "FALSE") return "нет";
  return raw;
}

function normalizedStatus(v, fallback = "NOT_INITIALIZED") {
  const raw = H(v || "").trim();
  if (!raw) return fallback;
  return raw.toUpperCase();
}

function boolRu(v) {
  return v ? "да" : "нет";
}

function asCount(v, fallback = 0) {
  const n = Number(v);
  return Number.isFinite(n) ? n : fallback;
}

function writeCommandSummary(id, lines) {
  if (!E(id)) return;
  E(id).textContent = A(lines).map((line) => H(line)).join("\n");
}

function semanticTone(v) {
  const t = String(v || "").toUpperCase();
  if (!t) return "warning";
  if (t.includes("CONFLICT") || t.includes("CRITICAL") || t.includes("BLOCKED") || t.includes("FAIL")) return "critical";
  if (t.includes("TRUSTED") || t.includes("PASS") || t.includes("PROVEN") || t.includes("STABLE") || t.includes("CLOSED_BY_OWNER")) return "trust";
  return "warning";
}

function worldTone(v) {
  const t = String(v || "").toUpperCase();
  if (!t) return "warning";
  if (t.includes("LOCK_ASSERTED")) return "critical";
  if (t.includes("LOCK_RECOMMENDED")) return "warning";
  if (t.includes("AWAKE")) return "warning";
  if (t.includes("DORMANT")) return "trust";
  if (t.includes("BLOCKED") || t.includes("CRITICAL") || t.includes("FAIL") || t.includes("CONFLICT")) return "critical";
  if (t.includes("ACTIVE") || t.includes("IN_PROGRESS")) return "active";
  if (t.includes("PROVEN") || t.includes("TRUSTED") || t.includes("PASS")) return "trust";
  if (t.includes("WAIT") || t.includes("PLANNED")) return "waiting";
  return "warning";
}

function worldStateRu(v) {
  const t = String(v || "").toUpperCase();
  if (t.includes("AWAKE")) return "бдит";
  if (t.includes("DORMANT")) return "спокойный дозор";
  if (t.includes("LOCK_ASSERTED")) return "жесткий lock";
  if (t.includes("LOCK_RECOMMENDED")) return "lock рекомендован";
  if (t.includes("ACTIVE") || t.includes("IN_PROGRESS")) return "активно";
  if (t.includes("WAIT") || t.includes("PLANNED")) return "ожидание";
  if (t.includes("PROVEN") || t.includes("PASS") || t.includes("TRUSTED")) return "подтверждено";
  if (t.includes("BLOCKED") || t.includes("CRITICAL") || t.includes("FAIL")) return "напряжение/блок";
  return "состояние зафиксировано";
}

function ageText(minutes) {
  const m = Number(minutes);
  if (!Number.isFinite(m) || m < 0) return "n/a";
  if (m < 60) return `${m} мин`;
  const h = Math.floor(m / 60);
  const rem = m % 60;
  return `${h}ч ${rem}м`;
}

function ageFromIso(iso) {
  const raw = H(iso || "");
  if (!raw) return null;
  const ts = Date.parse(raw);
  if (!Number.isFinite(ts)) return null;
  const now = Date.now();
  if (!Number.isFinite(now) || now < ts) return null;
  return Math.floor((now - ts) / 60000);
}

function eventRu(t) {
  const m = {
    wave_started: "Запущена волна работ",
    task_started: "Задача запущена",
    task_completed: "Задача завершена",
    bundle_checkpoint_emitted: "Сформирован checkpoint bundle",
    verification_changed: "Обновлен verification статус",
    contradiction_opened: "Открыто противоречие",
    contradiction_closed: "Противоречие закрыто",
    blocker_detected: "Обнаружен блокер",
    blocker_cleared: "Блокер снят",
    runtime_activity: "Событие runtime-активности агента"
  };
  return m[String(t || "").toLowerCase()] || `Событие: ${t || "event"}`;
}

function deptRu(id, fallbackName = "") {
  const map = {
    analytics_department: "Analytics (разбор и карта продукта)",
    engineering_department: "Engineering (реализация и стабилизация)",
    verification_department: "Verification (проверка и доверие)",
    release_integration_department: "Release & Integration (упаковка и выпуск)",
    tooling_infrastructure_department: "Tooling & Infrastructure (инструменты и контур)",
    product_intelligence_research_department: "Product Intelligence / Research (исследования и гипотезы)",
    growth_distribution_department: "Growth / Distribution (seed-режим)"
  };
  return map[id] || fallbackName || id || "unknown_department";
}

function pathNodeClass(state) {
  const s = key(state);
  if (s.includes("done") || s.includes("proven") || s.includes("resolved")) return "stage-done";
  if (s.includes("active") || s.includes("in_progress")) return "stage-active";
  if (s.includes("next")) return "stage-next";
  if (s.includes("blocked")) return "stage-blocked";
  return "stage-waiting";
}

function stageHint(state) {
  const s = key(state);
  if (s.includes("done") || s.includes("proven") || s.includes("resolved")) return "этап подтвержден";
  if (s.includes("active") || s.includes("in_progress")) return "идет выполнение";
  if (s.includes("next")) return "следующий на запуск";
  if (s.includes("blocked")) return "заблокирован";
  return "ожидает активации";
}

function badgeClass(state) {
  const s = key(state);
  if (s.includes("clean")) return "proven";
  if (s.includes("dirty")) return "nyi";
  if (s.includes("proven") || s.includes("resolved") || s.includes("pass")) return "proven";
  if (s.includes("active") || s.includes("in_progress")) return "active";
  if (s.includes("partial")) return "partial";
  if (s.includes("blocked") || s.includes("critical")) return "nyi";
  return "scaffolded";
}

function moduleLayerClass(state) {
  const s = key(state);
  if (s.includes("proven") || s.includes("resolved") || s.includes("pass")) return "proven";
  if (s.includes("active") || s.includes("in_progress")) return "active";
  if (s.includes("blocked") || s.includes("critical") || s.includes("error")) return "blocked";
  return "";
}

function sortEvents(events) {
  return [...A(events)].sort((a, b) => {
    const ta = Date.parse(String(a?.occurred_at_utc || ""));
    const tb = Date.parse(String(b?.occurred_at_utc || ""));
    if (Number.isNaN(ta) && Number.isNaN(tb)) return 0;
    if (Number.isNaN(ta)) return 1;
    if (Number.isNaN(tb)) return -1;
    return tb - ta;
  });
}

function latestEvent(events) {
  return O(sortEvents(events)[0]);
}

function mergeStateExcerpt(excerpt) {
  if (!excerpt) return;
  const ex = O(excerpt);
  if (!app.state) app.state = {};
  if (ex.bundle_path) app.state.bundle_path = ex.bundle_path;
  if (ex.bundle_name) app.state.bundle_name = ex.bundle_name;
  if (ex.bundle_binding) app.state.bundle_binding = ex.bundle_binding;
  if (ex.source_disclosure) app.state.source_disclosure = ex.source_disclosure;
}

function applyLiveUpdate(live, options = {}) {
  const prevLive = O(app.live);
  const prevTop = latestEvent(A(prevLive.live_change_feed));
  const nextTop = latestEvent(A(O(live).live_change_feed));
  app.liveDelta = {
    hasNewEvent: !!(nextTop.event_id && nextTop.event_id !== prevTop.event_id),
    latestEventId: H(nextTop.event_id || ""),
    latestEventType: H(nextTop.event_type || ""),
    latestChangedNodeId: H(O(live).live_operation_heartbeat?.latest_changed_node_id || ""),
    activeRouteNodeId: H(O(live).live_operation_heartbeat?.active_route_node_id || "")
  };
  app.live = live;
  app.liveChannel.lastEventId = H(nextTop.event_id || app.liveChannel.lastEventId);
  app.liveChannel.lastUpdateAt = H(nextTop.occurred_at_utc || new Date().toISOString());
  if (options.mechanism) app.liveChannel.mechanism = options.mechanism;
  if (options.status) app.liveChannel.status = options.status;
  if (options.note) app.liveChannel.note = options.note;
  if (app.state && app.live) renderAll();
}

async function syncStateSnapshot(reason = "live_sync") {
  if (app.stateSyncInFlight) return;
  const now = Date.now();
  if (now - Number(app.lastStateSyncAtEpochMs || 0) < 1400) return;
  app.stateSyncInFlight = true;
  try {
    const state = await J("/api/state");
    app.state = state;
    app.lastStateSyncAtEpochMs = Date.now();
    if (app.live) renderAll();
  } catch (_err) {
    // Keep current UI payload; live layer remains source for in-place updates.
  } finally {
    app.stateSyncInFlight = false;
  }
}

function shortText(value, max = 120) {
  const text = H(value || "").replace(/\s+/g, " ").trim();
  if (!text) return "n/a";
  if (text.length <= max) return text;
  return `${text.slice(0, Math.max(12, max - 1))}...`;
}

function shortTime(iso) {
  const raw = H(iso || "");
  if (!raw) return "n/a";
  return raw.replace("T", " ").replace("+00:00", "Z");
}

function buildProductionHistorySeedFromFeed(events) {
  const sorted = [...sortEvents(events)].reverse();
  const pick = (predicate) => sorted.find(predicate);
  const nodes = [];
  const addNode = (id, title, eventObj, fallbackNote) => {
    if (!eventObj || !eventObj.event_id) return;
    nodes.push({
      id,
      title,
      summary: shortText(eventObj.summary || fallbackNote, 98),
      at: shortTime(eventObj.occurred_at_utc),
      truthClass: eventObj.truth_class || "SOURCE_EXACT",
      sourcePath: eventObj.source_path || "n/a"
    });
  };

  addNode(
    "kickoff",
    "Kickoff",
    pick((e) => key(e.event_type) === "wave_started"),
    "Запуск Wave 1"
  );
  addNode(
    "truth_binding",
    "Truth binding stabilized",
    pick((e) => key(e.summary).includes("truth binding")),
    "Стабилизация active truth binding"
  );
  addNode(
    "tranche_progression",
    "Tranche progression",
    pick((e) => key(e.summary).includes("w1-tr1") || key(e.summary).includes("tranche")),
    "Прогресс Tranche 1"
  );
  addNode(
    "contradiction_delta",
    "Contradiction delta",
    pick((e) => key(e.summary).includes("ctr-001") || key(e.summary).includes("delta")),
    "Delta по contradiction"
  );
  addNode(
    "checkpoint_shift",
    "Checkpoint posture shift",
    pick((e) => key(e.event_type) === "bundle_checkpoint_emitted"),
    "Сдвиг checkpoint posture"
  );

  return nodes.slice(0, 6);
}

function checkpointRuleRu(ruleId) {
  const map = {
    option_b_locked: "OPTION_B зафиксирован",
    gate_c_visual_direction_locked: "Gate C visual direction зафиксирован",
    wave_1_scope_confirmed: "Wave 1 scope подтвержден",
    tranche_1_evidence_reviewed: "Tranche 1 evidence просмотрен",
    tranche_1_delta_chain_reviewed: "Цепочка delta Tranche 1 просмотрена",
    w1_ctr001_partial_closure_delta06_reviewed: "Частичное закрытие W1-CTR-001 (delta06) просмотрено",
    gate_d_owner_decision_pending_acknowledged: "Owner-решение по Gate D зафиксировано",
    owner_checkpoint_review_delta06_consolidated: "Checkpoint review delta06 консолидирован",
    owner_manual_gate_d_and_wave1_closure_recorded: "Ручное закрытие Gate D и Wave 1 записано"
  };
  return map[ruleId] || ruleId || "checkpoint_rule";
}

function modeFromQuery() {
  const q = new URLSearchParams(window.location.search).get("mode");
  if (!q) return null;
  const v = q.toLowerCase();
  if (v === MODE_FULL || v === "full" || v === "vision" || v === "aquarium") return MODE_FULL;
  return MODE_COMMAND;
}

function setMode(mode, persist = true) {
  const m = mode === MODE_FULL ? MODE_FULL : MODE_COMMAND;
  if (m === MODE_FULL) {
    window.location.href = "/eye/";
    return;
  }
  document.body.dataset.mode = m;
  E("modeCommandBtn")?.classList.toggle("active", m === MODE_COMMAND);
  E("modeFullVisionBtn")?.classList.toggle("active", m === MODE_FULL);
  if (E("modeStatusText")) {
    E("modeStatusText").textContent = m === MODE_FULL
      ? "Текущий режим: FULL VISION / AQUARIUM MODE (владелец)"
      : "Текущий режим: COMMAND MODE (контроль и правда)";
  }
  if (persist) localStorage.setItem(MODE_KEY, m);
  const url = new URL(window.location.href);
  url.searchParams.set("mode", m);
  history.replaceState({}, "", url.toString());
}

function initMode() {
  E("modeCommandBtn")?.addEventListener("click", () => setMode(MODE_COMMAND));
  E("modeFullVisionBtn")?.addEventListener("click", () => setMode(MODE_FULL));
  const initial = modeFromQuery() || localStorage.getItem(MODE_KEY) || MODE_COMMAND;
  setMode(initial, false);
}

function card(title, body, cls = "") {
  return `<div class="vision-card ${cls}"><div class="vision-card-title">${title}</div><div class="vision-card-note">${body}</div></div>`;
}

function lane(title, pct, note) {
  return `<div class="vision-kpi"><div class="vision-kpi-label">${title}</div><div class="vision-kpi-value">${pct}% (stage indicator)</div><div class="lane-track"><div class="lane-fill pulse" style="width:${pct}%"></div></div><div class="vision-card-subtle">${note}</div></div>`;
}
function renderCommand(state, live) {
  const binding = O(state.bundle_binding);
  const disclosure = O(state.source_disclosure);
  const control = O(state.imperium_control_gates_state);
  const truthSpine = O(state.imperium_truth_spine_state || live.live_truth_spine_state);
  const dashboardTruth = O(state.imperium_dashboard_truth_engine_state || live.live_dashboard_truth_engine_state);
  const bundleTruth = O(state.imperium_bundle_truth_chamber_state || live.live_bundle_truth_chamber_state);
  const worktreePurity = O(state.imperium_worktree_purity_gate_state || live.live_worktree_purity_gate_state);
  const factoryOverviewState = O(state.factory_overview);
  const liveFactoryState = O(live.live_factory_state);
  const waveControl = O(state.wave1_control_surfaces);
  const waveSurface = O(waveControl.wave_status_surface);
  const trancheSurface = O(waveControl.first_tranche_execution);
  const contradictionLedger = O(waveControl.contradiction_ledger);
  const liveGate = O(live.live_gate_state);

  const waveStatusUpper = normalizedStatus(waveSurface.status, "UNKNOWN");
  const waveClaimUpper = normalizedStatus(waveSurface.claim, "UNKNOWN");
  const waveClosed = waveStatusUpper.includes("CLOSED");
  const openContradictions = A(contradictionLedger.open).length;
  const closedContradictions = A(contradictionLedger.closed).length;
  const hasOpenContradictions = openContradictions > 0;
  const factoryOwnerGateWaiting = A(factoryOverviewState.owner_gates_waiting).length;
  const liveOwnerGateWaiting = asCount(liveFactoryState.pending_owner_gates_count, 0);
  const factoryBlockers = A(factoryOverviewState.blockers).length;
  const liveBlockers = asCount(liveFactoryState.open_blockers_count, 0);
  const ownerGateMismatch = factoryOwnerGateWaiting !== liveOwnerGateWaiting;
  const blockerMismatch = factoryBlockers !== liveBlockers;
  const gateSummary = normalizedStatus(control.gate_summary, "UNKNOWN");
  const controlBlocked = asCount(control.blocked_count, 0);
  const controlWarning = asCount(control.warning_count, 0);

  const wavePosture = waveClosed && hasOpenContradictions
    ? "PARTIAL_CLOSURE_OPEN_CONTRADICTIONS"
    : (waveClosed ? "CLOSED_OWNER_CONFIRMED" : (waveStatusUpper.includes("IN_PROGRESS") ? "ACTIVE_WAVE" : waveStatusUpper));
  const wavePostureClass = waveClosed && hasOpenContradictions ? "partial" : badgeClass(wavePosture);
  const wavePostureNote = waveClosed && hasOpenContradictions
    ? "Волна закрыта владельцем, но contradiction остаются открытыми: это не calm-state."
    : (waveClosed
      ? "Owner closure подтвержден; открытых contradictions нет."
      : "Волна активна/переходная, closure claim не финален.");

  const parity = O(state.parity);
  const fileCounts = O(state.file_counts);
  writeCommandSummary("bundleSummary", [
    `Bundle: ${H(state.bundle_name || "n/a")}`,
    `Path: ${H(state.bundle_path || "n/a")}`,
    `Source mode: ${H(disclosure.selection_mode || binding.selection_mode || "NOT_INITIALIZED")}`,
    `Parity=${H(parity.overall || "UNKNOWN")} | Panels=${String(A(state.panels).length)} | Files=${String(fileCounts.total ?? "n/a")}`,
    `Truth spine=${H(truthSpine.status || "NOT_INITIALIZED")} | Dashboard truth=${H(dashboardTruth.status || "NOT_INITIALIZED")}`,
    `Bundle truth=${H(bundleTruth.status || "NOT_INITIALIZED")} | Transport=${H(O(bundleTruth.transport_integrity).status || "NOT_INITIALIZED")}`,
    `Worktree purity=${H(worktreePurity.status || "NOT_INITIALIZED")} | Cleanliness=${H(worktreePurity.cleanliness_verdict || "NOT_INITIALIZED")}`,
    `Wave posture=${wavePosture} | Contradictions open=${String(openContradictions)} | Gate summary=${gateSummary}`,
  ]);

  if (E("canonStateSync")) {
    const canon = O(state.canon_state_sync);
    const tik = O(canon.tiktok_agent);
    const ownerGates = O(canon.owner_gates);
    const liveLayer = O(canon.live_layer);
    writeCommandSummary("canonStateSync", [
      `Selected option: ${H(tik.selected_option || "UNKNOWN")}`,
      `Wave lane=${H(tik.wave_1_status || "UNKNOWN")} | Gate D=${H(ownerGates.gate_d || "UNKNOWN")}`,
      `Post-wave=${H(O(tik.post_wave1_stage).status || "UNKNOWN")} | Active tranche=${H(O(tik.post_wave1_stage).active_tranche || "UNKNOWN")}`,
      `Live layer=${H(liveLayer.implementation_status || "UNKNOWN")} | Front=${H(liveLayer.front_status || "UNKNOWN")}`,
      `Closure semantics=${wavePosture} (${wavePostureNote})`,
    ]);
  }
  if (E("systemSemanticState")) {
    const semantic = O(state.system_semantic_state_surfaces);
    const liveSemantic = O(live.live_semantic_state);
    const truth = O(liveSemantic.exact_derived_gap_disclosure || semantic.exact_derived_gap_disclosure);
    const brain = O(liveSemantic.brain_reason_control_state || semantic.brain_reason_control_state);
    const constitution = O(liveSemantic.constitution_state || semantic.constitution_state);
    writeCommandSummary("systemSemanticState", [
      `Brain trust=${H(brain.trust_state || "UNKNOWN")} | contradiction=${H(brain.contradiction_state || "UNKNOWN")} | owner_triggers=${String(brain.owner_decision_trigger_count ?? A(brain.owner_decision_trigger_state).length ?? 0)}`,
      `Constitution trust=${H(constitution.trust_status || "UNKNOWN")} | governance=${H(constitution.governance_acceptance || "UNKNOWN")} | drift=${H(constitution.canon_drift_risk || "UNKNOWN")}`,
      `Truth layers: exact=${String(truth.exact_count ?? 0)} | derived=${String(truth.derived_count ?? 0)} | gaps=${String(truth.gap_count ?? 0)} | stale=${String(truth.stale_source_count ?? 0)}`,
      `Semantic mode=${H(liveSemantic.truth_class || semantic.truth_class || "DERIVED_CANONICAL")} | open_contradictions=${String(openContradictions)}`,
    ]);
  }
  if (E("liveFactoryState")) {
    writeCommandSummary("liveFactoryState", [
      `Generated: ${H(live.generated_at_utc || "n/a")} | scope=${H(live.mode_scope || "UNKNOWN")} | visual=${H(live.visual_pack || "UNKNOWN")}`,
      `Products=${String(liveFactoryState.active_products_count ?? A(factoryOverviewState.products_in_work).length)} | Departments=${String(liveFactoryState.active_departments_count ?? A(factoryOverviewState.active_departments).length)}`,
      `Owner gates waiting: state=${String(factoryOwnerGateWaiting)} | live=${String(liveOwnerGateWaiting)}${ownerGateMismatch ? " [MISMATCH_VISIBLE]" : ""} | required=${boolRu(Boolean(liveGate.owner_required))}`,
      `Blockers: state=${String(factoryBlockers)} | live=${String(liveBlockers)}${blockerMismatch ? " [MISMATCH_VISIBLE]" : ""}`,
      `Control gates: summary=${gateSummary} | blocked=${String(controlBlocked)} | warning=${String(controlWarning)}`,
      `Pending markers=${String(liveGate.pending_gate_markers ?? 0)} | pending_ids=${A(liveGate.pending_gate_ids).length}`,
    ]);
  }

  const f = factoryOverviewState;
  if (E("factoryOverview")) {
    E("factoryOverview").innerHTML = `<div class="panel-card"><strong>Factory Status Snapshot</strong>
      <div>Products in work: ${A(f.products_in_work).length}</div>
      <div>Active departments: ${A(f.active_departments).length}</div>
      <div>Owner gates waiting: state=${A(f.owner_gates_waiting).length} | live=${String(liveOwnerGateWaiting)}${ownerGateMismatch ? ' <span class="label-badge partial">MISMATCH</span>' : ''}</div>
      <div>Blockers: state=${A(f.blockers).length} | live=${String(liveBlockers)}${blockerMismatch ? ' <span class="label-badge partial">MISMATCH</span>' : ''}</div>
      <div>Control gates: summary=${esc(gateSummary)} | blocked=${String(controlBlocked)} | warning=${String(controlWarning)}</div>
      <div class="compact-note">Owner gate required=${boolRu(Boolean(liveGate.owner_required))} | pending markers=${String(liveGate.pending_gate_markers ?? 0)} | pending ids=${A(liveGate.pending_gate_ids).length}</div></div>`;
  }

  const w = waveControl;
  const ws = waveSurface;
  const tr = trancheSurface;
  const ctr = contradictionLedger;
  if (E("wave1ControlSurfaces")) {
    E("wave1ControlSurfaces").innerHTML = `<div class="panel-card"><strong>Wave Status</strong>
      <div>Wave: ${esc(w.wave_id || "n/a")} | Status: ${esc(ws.status || "n/a")} | Claim: ${esc(ws.claim || "n/a")}</div>
      <div>Posture: <span class="label-badge ${wavePostureClass}">${esc(wavePosture)}</span> | Tranche state: ${esc(tr.status || ws.active_tranche_state || "UNKNOWN")}</div>
      <div>Active tranche: ${pv(ws.active_tranche_id || tr.tranche_id || "n/a")}</div>
      <div>Open contradictions: ${A(ctr.open).length} | Closed: ${A(ctr.closed).length} | Gate summary: ${esc(gateSummary)}</div>
      <div class="compact-note">${esc(wavePostureNote)}</div></div>`;
  }

  const liveSigns = A(live.live_health_state).map((x) => `<div class="panel-card"><strong>${x.metric_id || "metric"}</strong>
    <span class="truth-badge">${x.state || "unknown"}</span><span class="label-badge ${String(x.implementation_label || "").toLowerCase().replace(/\s+/g, "_")}">${x.implementation_label || "SCAFFOLDED"}</span>
    <div>Value: ${vb(x.value || "n/a")}<span class="compact-note">Trend: ${esc(x.trend || "n/a")}</span></div></div>`).join("");
  if (E("liveVitalSigns")) E("liveVitalSigns").innerHTML = liveSigns || "No live vital signs.";

  const gate = O(live.live_gate_state);
  if (E("liveOwnerGates")) {
    E("liveOwnerGates").innerHTML = `<div class="panel-card"><strong>${gate.gate_id || "owner_gate"}</strong>
      <span class="truth-badge">${gate.status || "unknown"}</span>
      <div>Owner required: ${String(!!gate.owner_required)} | Pending: ${vb(A(gate.pending_gate_ids).join(", ") || "none")}</div>
      <div>Next checkpoint: ${pv(gate.next_checkpoint || "n/a")}</div></div>`;
  }

  const feed = sortEvents(live.live_change_feed).slice(0, 10).map((x) => `<div class="panel-card"><strong>${x.event_type || "event"}</strong>
    <div>${esc(x.occurred_at_utc || "n/a")} | ${vb(x.summary || "")}</div><div>Source: ${pv(x.source_path || "n/a")} | Class: ${esc(x.truth_class || "SOURCE_EXACT")}</div></div>`).join("");
  if (E("liveChangeFeed")) E("liveChangeFeed").innerHTML = feed || "No live change events.";

  const pmeta = O(live.live_preview_meta);
  const diffState = O(Object.keys(O(live.live_diff_preview_state)).length ? live.live_diff_preview_state : state.imperium_diff_preview_state);
  if (E("livePreviews")) E("livePreviews").innerHTML = `<div class="panel-card"><strong>Preview Registry State</strong>
    <span class="truth-badge">${pmeta.status || "PLACEHOLDER"}</span>
    <span class="label-badge ${String(pmeta.implementation_label || "SCAFFOLDED").toLowerCase().replace(/\s+/g, "_")}">${pmeta.implementation_label || "SCAFFOLDED"}</span>
    <div>${vb(pmeta.note || "preview stream note unavailable")}</div>
    <div>Changed sectors: ${vb(String(pmeta.changed_count ?? diffState.changed_count ?? 0))} / Compared: ${vb(String(pmeta.compared_count ?? diffState.compared_count ?? 0))}</div>
    <div>Diff pack: ${pv(pmeta.latest_diff_pack_path || diffState.latest_diff_pack_path || "n/a")}</div>
  </div>`;

  if (E("beforeAfterZone")) E("beforeAfterZone").innerHTML = `
    <div class="panel-card"><strong>Before/After Diff Engine</strong>
      <span class="truth-badge">${esc(diffState.status || "UNKNOWN")}</span>
      <span class="label-badge ${String(O(diffState.pipeline_profile).diff_engine_status || "PARTIALLY_IMPLEMENTED").toLowerCase().replace(/\s+/g, "_")}">${esc(O(diffState.pipeline_profile).diff_engine_status || "PARTIALLY_IMPLEMENTED")}</span>
      <div>Compared sectors: ${vb(String(diffState.compared_count ?? 0))} | Changed sectors: ${vb(String(diffState.changed_count ?? 0))}</div>
      <div>Latest diff manifest: ${pv(diffState.latest_diff_manifest_path || "n/a")}</div>
      <div>Contact sheet: ${pv(diffState.latest_contact_sheet_html || "n/a")}</div>
    </div>
  `;

  const depts = A(state.department_floor).map((d) => `<div class="panel-card"><strong>${d.name || d.id}</strong>
    <span class="truth-badge">${d.status || "UNKNOWN"}</span>
    <div>Load: ${vb(d.current_load || "n/a")}<span class="compact-note">Activation: ${esc(d.activation_level || "n/a")}</span></div></div>`).join("");
  if (E("departmentFloor")) E("departmentFloor").innerHTML = depts || "No department floor model loaded.";

  const prods = A(state.product_lanes).map((p) => `<div class="panel-card"><strong>${p.display_name || p.product_id}</strong>
    <span class="truth-badge">${p.lane_status || "unknown"}</span>
    <div>Stage: ${vb(p.pipeline_stage || "n/a")}<span class="compact-note">Active wave: ${esc(p.active_wave || "n/a")}</span></div>
    <div>Selected option: ${esc(p.selected_option || "n/a")} | Visual doctrine: ${pv(p.visual_doctrine || "n/a")}</div></div>`).join("");
  if (E("productLanes")) E("productLanes").innerHTML = prods || "No product lane model loaded.";

  const queues = A(state.queue_monitor).map((q) => `<div class="panel-card"><strong>${q.title || q.queue_id}</strong>
    <span class="truth-badge">${q.state || "unknown"}</span><div>Items: ${q.items_count ?? "n/a"} | Top: ${vb(q.top_item || "none")}</div></div>`).join("");
  if (E("queueMonitor")) E("queueMonitor").innerHTML = queues || "No queue monitor model loaded.";

  const force = O(state.force_map);
  const emperor = O(force.emperor);
  if (E("forceMap")) E("forceMap").innerHTML = `<div class="panel-card"><strong>Emperor: ${emperor.id || "n/a"}</strong>
    <span class="truth-badge">${emperor.state || "unknown"}</span><div>Rank: ${emperor.rank || "n/a"} | Mode: ${emperor.machine_mode || "n/a"}</div></div>`;

  renderPanels(state);
}

function renderPanels(state) {
  const root = E("panels");
  if (!root) return;
  const panels = A(state.panels);
  if (!panels.length) {
    root.textContent = "No panels available.";
    return;
  }
  root.innerHTML = panels.map((p) => {
    const checks = A(p.source_checks).map((s) => {
      const section = esc(s.source_section_or_member || "whole_document");
      const dclass = esc(s.data_class || "SOURCE_EXACT");
      const src = pv(s.source_path || "n/a");
      if (!s.present_in_bundle) return `<li>${src} [${section}] [${dclass}] (missing in bundle)</li>`;
      return `<li><a href="#" class="source-link" data-member="${s.bundle_member}">${src} [${section}] [${dclass}]</a></li>`;
    }).join("");
    return `<div class="panel-card"><strong>${p.title || p.panel_id}</strong>
      <span class="truth-badge">${p.truth_class || "VIEW_ONLY"}</span><span class="truth-badge">${p.parity_status || "MISSING"}</span>
      <ul>${checks}</ul></div>`;
  }).join("");

  root.querySelectorAll("a.source-link").forEach((a) => {
    a.addEventListener("click", async (e) => {
      e.preventDefault();
      await loadSourcePreview(a.getAttribute("data-member"));
    });
  });
}

async function loadSourcePreview(member) {
  if (!E("sourcePreview")) return;
  E("sourcePreview").textContent = "Loading...";
  try {
    const payload = await J(`/api/source?member=${encodeURIComponent(member)}`);
    E("sourcePreview").textContent = `${payload.member}\n\n${payload.preview || ""}`;
  } catch (err) {
    E("sourcePreview").textContent = `Error: ${err.message}`;
  }
}
function checkpointReadiness(state, live) {
  const c = O(state.canon_state_sync);
  const gates = O(c.owner_gates);
  const w = O(state.wave1_control_surfaces);
  const cp = O(w.owner_gate_checkpoint_surface);
  const req = A(cp.required_owner_confirmations);
  const ws = O(w.wave_status_surface);
  const hasBundleEvt = A(live.live_change_feed).some((e) => String(e.event_type || "").toLowerCase() === "bundle_checkpoint_emitted");
  const checks = req.map((r) => {
    if (r === "option_b_locked") return { r, ready: String(gates.gate_b || "").includes("RESOLVED_OPTION_B"), partial: false };
    if (r === "gate_c_visual_direction_locked") return { r, ready: String(gates.gate_c || "").includes("RESOLVED"), partial: false };
    if (r === "wave_1_scope_confirmed") {
      const wsUpper = String(ws.status || "").toUpperCase();
      return { r, ready: wsUpper === "IN_PROGRESS" || wsUpper.includes("CLOSED_BY_OWNER"), partial: false };
    }
    if (r === "tranche_1_evidence_reviewed") {
      const wsUpper = String(ws.status || "").toUpperCase();
      return { r, ready: wsUpper.includes("CLOSED_BY_OWNER"), partial: hasBundleEvt };
    }
    return { r, ready: false, partial: false };
  });
  return { checks, ready: checks.filter((x) => x.ready).length, partial: checks.filter((x) => x.partial).length, total: checks.length, next: cp.next_checkpoint || "POST_WAVE_1_EVIDENCE_GATE_D" };
}

function renderFullVision(state, live) {
  const canon = O(state.canon_state_sync);
  const tik = O(canon.tiktok_agent);
  const postWaveStage = O(tik.post_wave1_stage);
  const gates = O(canon.owner_gates);
  const grow = O(canon.growth_distribution);
  const layer = O(canon.live_layer);
  const f = O(state.factory_overview);
  const product = O(A(f.products_in_work)[0]);
  const wave = O(state.wave1_control_surfaces);
  const brain = O(state.system_brain_state);
  const semantic = O(state.system_semantic_state_surfaces);
  const promptState = O(state.prompt_lineage_state);
  const runtimeObs = O(state.tiktok_agent_runtime_observability);
  const ws = O(wave.wave_status_surface);
  const tr = O(wave.first_tranche_execution);
  const work = A(tr.active_workset);
  const ctr = O(wave.contradiction_ledger);
  const openCtr = A(ctr.open);
  const closedCtr = A(ctr.closed);
  const risks = O(wave.baseline_risk_board);
  const liveFeed = sortEvents(live.live_change_feed);
  const latestEvt = O(liveFeed[0]);
  const latestProofEvt = O(liveFeed.find((x) => key(x.event_type) === "verification_changed"));
  const latestRiskEvt = O(liveFeed.find((x) => key(x.event_type) === "contradiction_opened" || H(x.summary).toLowerCase().includes("risk")));
  const latestBlockerEvt = O(liveFeed.find((x) => key(x.event_type) === "blocker_detected" || H(x.summary).toLowerCase().includes("blocker")));
  const latestBlocker = O(A(f.blockers)[0]);
  const activeDept = product.current_department || "analytics_department";
  const heartbeat = O(live.live_operation_heartbeat);
  const liveProduct = O(live.live_product_state);
  const liveRuntime = O(live.live_agent_runtime_state);
  const liveBrain = O(live.live_brain_state);
  const livePrompt = O(live.live_prompt_state);
  const liveSemantic = O(live.live_semantic_state);
  const liveFactory = O(live.live_factory_state);
  const semanticConstitution = O(liveSemantic.constitution_state || semantic.constitution_state);
  const semanticBrain = O(liveSemantic.brain_reason_control_state || semantic.brain_reason_control_state);
  const semanticMemory = O(liveSemantic.memory_chronology_knowledge_state || semantic.memory_chronology_knowledge_state);
  const semanticProduct = O(liveSemantic.product_state_integration || semantic.product_state_integration);
  const semanticSecurity = O(liveSemantic.security_sovereignty_posture_state || semantic.security_sovereignty_posture_state);
  const semanticTruth = O(liveSemantic.exact_derived_gap_disclosure || semantic.exact_derived_gap_disclosure);
  const evolutionState = O(state.imperium_evolution_state);
  const inquisitionState = O(state.imperium_inquisition_state);
  const factoryProductionState = O(state.imperium_factory_production_state);
  const productEvolutionMap = O(state.imperium_product_evolution_map);
  const eventFlowState = O(state.imperium_event_flow_state);
  const diffPreviewState = O(state.imperium_diff_preview_state);
  const throneAuthorityState = O(state.imperium_throne_authority_state);
  const goldenThroneState = O(state.imperium_golden_throne_discoverability);
  const trueFormState = O(state.imperium_true_form_state);
  const custodesState = O(state.imperium_custodes_state);
  const mechanicusState = O(state.imperium_mechanicus_state);
  const administratumState = O(state.imperium_administratum_state);
  const forceDoctrineState = O(state.imperium_force_state);
  const palaceArchiveState = O(state.imperium_palace_archive_state);
  const controlGatesState = O(state.imperium_control_gates_state);
  const brainV2State = O(state.imperium_brain_v2_layers || O(brain.brain_v2_layers));
  const machineCapabilityState = O(state.imperium_machine_capability_manifest);
  const organStrengthState = O(state.imperium_organ_strength_surface);
  const activeMissionContractState = O(state.imperium_active_mission_contract);
  const codeBankState = O(state.imperium_code_bank_state);
  const liveWorkState = O(state.imperium_live_work_state);
  const doctrineIntegrityState = O(state.imperium_doctrine_integrity_state);
  const truthSpineState = O(state.imperium_truth_spine_state);
  const dashboardTruthEngineState = O(state.imperium_dashboard_truth_engine_state);
  const bundleTruthChamberState = O(state.imperium_bundle_truth_chamber_state);
  const worktreePurityGateState = O(state.imperium_worktree_purity_gate_state);
  const addressLatticeState = O(state.imperium_address_lattice_state);
  const antiLieModelState = O(state.imperium_anti_lie_model_state);
  const liveTruthSupportLoopState = O(state.imperium_live_truth_support_loop_state);
  const coverageState = O(state.imperium_dashboard_coverage_state);
  const dominanceState = O(state.imperium_truth_dominance_state);
  const storageHealthState = O(state.imperium_storage_health_state);
  const parallelChannels = O(state.imperium_parallel_channels);
  const liveEvolution = O(live.live_evolution_state);
  const liveInquisition = O(live.live_inquisition_state);
  const liveCustodes = O(live.live_custodes_state);
  const liveFactoryProduction = O(live.live_factory_production_state);
  const liveEventFlow = O(live.live_event_flow_state);
  const liveDiffPreview = O(live.live_diff_preview_state);
  const liveThroneAuthority = O(live.live_throne_authority_state);
  const liveGoldenThrone = O(live.live_golden_throne_discoverability);
  const liveMechanicus = O(live.live_mechanicus_state);
  const liveAdministratum = O(live.live_administratum_state);
  const liveForce = O(live.live_force_state);
  const livePalaceArchive = O(live.live_palace_archive_state);
  const liveControlGates = O(live.live_control_gates_state);
  const liveBrainV2 = O(live.live_brain_v2_layers);
  const liveMachineCapability = O(live.live_machine_capability_manifest);
  const liveOrganStrength = O(live.live_organ_strength_surface);
  const liveMissionContract = O(live.live_active_mission_contract);
  const liveCodeBank = O(live.live_code_bank_state);
  const liveWork = O(live.live_work_state);
  const liveDoctrineIntegrity = O(live.live_doctrine_integrity_state);
  const liveTruthSpine = O(live.live_truth_spine_state);
  const liveDashboardTruthEngine = O(live.live_dashboard_truth_engine_state);
  const liveBundleTruthChamber = O(live.live_bundle_truth_chamber_state);
  const liveWorktreePurityGate = O(live.live_worktree_purity_gate_state);
  const liveAddressLattice = O(live.live_address_lattice_state);
  const liveAntiLieModel = O(live.live_anti_lie_model_state);
  const liveTruthSupportLoop = O(live.live_truth_support_loop_state);
  const liveCoverage = O(live.live_dashboard_coverage_state);
  const liveDominance = O(live.live_truth_dominance_state);
  const liveStorage = O(live.live_storage_health_state);
  const evolution = O(Object.keys(liveEvolution).length ? liveEvolution : (Object.keys(evolutionState).length ? evolutionState : parallelChannels.evolution));
  const inquisition = O(Object.keys(liveInquisition).length ? liveInquisition : (Object.keys(inquisitionState).length ? inquisitionState : parallelChannels.inquisition));
  const custodes = O(Object.keys(liveCustodes).length ? liveCustodes : (Object.keys(custodesState).length ? custodesState : parallelChannels.custodes));
  const mechanicus = O(Object.keys(liveMechanicus).length ? liveMechanicus : (Object.keys(mechanicusState).length ? mechanicusState : parallelChannels.mechanicus));
  const administratum = O(Object.keys(liveAdministratum).length ? liveAdministratum : (Object.keys(administratumState).length ? administratumState : parallelChannels.administratum));
  const forceDoctrine = O(Object.keys(liveForce).length ? liveForce : (Object.keys(forceDoctrineState).length ? forceDoctrineState : parallelChannels.force));
  const palaceArchive = O(Object.keys(livePalaceArchive).length ? livePalaceArchive : (Object.keys(palaceArchiveState).length ? palaceArchiveState : parallelChannels.palace_archive));
  const controlGates = O(Object.keys(liveControlGates).length ? liveControlGates : (Object.keys(controlGatesState).length ? controlGatesState : parallelChannels.control_gates));
  const brainV2 = O(Object.keys(liveBrainV2).length ? liveBrainV2 : brainV2State);
  const machineCapability = O(Object.keys(liveMachineCapability).length ? liveMachineCapability : machineCapabilityState);
  const organStrength = O(Object.keys(liveOrganStrength).length ? liveOrganStrength : organStrengthState);
  const activeMissionContract = O(Object.keys(liveMissionContract).length ? liveMissionContract : activeMissionContractState);
  const factoryAssembly = O(Object.keys(liveFactoryProduction).length ? liveFactoryProduction : (Object.keys(factoryProductionState).length ? factoryProductionState : parallelChannels.factory));
  const eventFlow = O(Object.keys(liveEventFlow).length ? liveEventFlow : eventFlowState);
  const diffPreview = O(Object.keys(liveDiffPreview).length ? liveDiffPreview : diffPreviewState);
  const throneAuthority = O(Object.keys(liveThroneAuthority).length ? liveThroneAuthority : (Object.keys(throneAuthorityState).length ? throneAuthorityState : O(brain.throne_authority)));
  const goldenThrone = O(Object.keys(liveGoldenThrone).length ? liveGoldenThrone : goldenThroneState);
  const codeBank = O(Object.keys(liveCodeBank).length ? liveCodeBank : (Object.keys(codeBankState).length ? codeBankState : O(brain.code_bank)));
  const workVisibility = O(Object.keys(liveWork).length ? liveWork : liveWorkState);
  const doctrineIntegrity = O(Object.keys(liveDoctrineIntegrity).length ? liveDoctrineIntegrity : doctrineIntegrityState);
  const truthSpine = O(Object.keys(liveTruthSpine).length ? liveTruthSpine : truthSpineState);
  const dashboardTruthEngine = O(Object.keys(liveDashboardTruthEngine).length ? liveDashboardTruthEngine : dashboardTruthEngineState);
  const bundleTruthChamber = O(Object.keys(liveBundleTruthChamber).length ? liveBundleTruthChamber : bundleTruthChamberState);
  const worktreePurityGate = O(Object.keys(liveWorktreePurityGate).length ? liveWorktreePurityGate : worktreePurityGateState);
  const addressLattice = O(Object.keys(liveAddressLattice).length ? liveAddressLattice : addressLatticeState);
  const antiLieModel = O(Object.keys(liveAntiLieModel).length ? liveAntiLieModel : antiLieModelState);
  const truthSupportLoop = O(Object.keys(liveTruthSupportLoop).length ? liveTruthSupportLoop : liveTruthSupportLoopState);
  const coverage = O(Object.keys(liveCoverage).length ? liveCoverage : (Object.keys(coverageState).length ? coverageState : O(brain.dashboard_coverage)));
  const dominance = O(Object.keys(liveDominance).length ? liveDominance : (Object.keys(dominanceState).length ? dominanceState : O(brain.truth_dominance)));
  const storageHealth = O(Object.keys(liveStorage).length ? liveStorage : storageHealthState);
  const runtimeProcessState = H(runtimeObs.process_state || liveRuntime.process_state || "");
  const productProcessState = H(runtimeProcessState || liveProduct.process_state || product.execution_state || tr.status || "UNKNOWN");
  const runtimeOperation = H(
    runtimeObs.current_operation_code
    || liveRuntime.current_operation_code
    || heartbeat.current_operation_code
    || ws.objective
    || "UNKNOWN_OPERATION"
  );
  const runtimeFailure = H(
    runtimeObs.failure_reason
    || liveRuntime.failure_reason
    || liveProduct.runtime_failure_reason
    || heartbeat.runtime_failure_reason
    || "none"
  );
  const runtimeRecovery = H(
    runtimeObs.recovery_signal
    || liveRuntime.recovery_signal
    || liveProduct.runtime_recovery_signal
    || heartbeat.runtime_recovery_signal
    || "none"
  );
  const runtimeSourceMode = H(
    runtimeObs.source_mode
    || liveRuntime.source_mode
    || liveProduct.runtime_observability_source
    || "DERIVED_RUNTIME_LOG"
  );
  const runtimeLatestSummary = H(
    runtimeObs.latest_change_summary
    || liveRuntime.latest_change_summary
    || heartbeat.latest_milestone_summary
    || ""
  );
  const stageOrder = [
    { id: "analytics_department", label: "ANALYTICS" },
    { id: "engineering_department", label: "ENGINEERING" },
    { id: "verification_department", label: "VERIFICATION" },
    { id: "release_integration_department", label: "RELEASE" },
    { id: "growth_distribution_department", label: "GROWTH" }
  ];
  const activeIdx = Math.max(0, stageOrder.findIndex((x) => x.id === activeDept));
  const cp = checkpointReadiness(state, live);
  const cpMissing = cp.checks.filter((x) => !x.ready).map((x) => checkpointRuleRu(x.r));
  const topRisk = shortText(A(risks.top_risks)[0] || "risk detail pending", 82);
  const topOpen = O(openCtr[0]);
  const primaryWork = O(work.find((x) => key(x.status).includes("active") || key(x.status).includes("in_progress")) || work[0]);
  const latestChangeText = heartbeat.latest_milestone_summary
    ? shortText(heartbeat.latest_milestone_summary, 92)
    : (latestEvt.event_type ? `${eventRu(latestEvt.event_type)}: ${shortText(latestEvt.summary || "", 92)}` : "Новых событий пока нет.");
  const latestProofText = heartbeat.latest_proof_summary
    ? shortText(heartbeat.latest_proof_summary, 96)
    : (latestProofEvt.summary
      ? shortText(latestProofEvt.summary, 96)
      : (closedCtr.length ? `Закрыто contradictions: ${closedCtr.map((x) => x.id).join(", ")}` : "Отдельный proof-event пока не зафиксирован."));
  const latestRiskText = heartbeat.latest_risk_summary
    ? shortText(heartbeat.latest_risk_summary, 96)
    : shortText(latestRiskEvt.summary || topRisk, 96);
  const blockerText = heartbeat.latest_blocker_summary
    ? shortText(heartbeat.latest_blocker_summary, 96)
    : shortText(latestBlockerEvt.summary || latestBlocker.reason || topOpen.title || "Активный blocker пока не зафиксирован.", 96);
  const shortCheckpoint = shortText(cp.next, 64);
  const routeFocusNode = heartbeat.active_route_node_id || activeDept;
  const changedNode = heartbeat.latest_changed_node_id || "";
  const blockerNode = heartbeat.blocker_node_id || "";
  const tiktokEvolutionLine = O(A(productEvolutionMap.lines).find((x) => H(x.product_id) === "tiktok_agent_platform"));
  const tiktokAscentTrack = O(tiktokEvolutionLine.ascent_track);
  const flowPosture = H(heartbeat.event_flow_posture || eventFlow.flow_posture || "WAIT");
  const flowRouteFocus = H(heartbeat.event_flow_route_focus || "");
  const flowSummary = H(heartbeat.event_flow_active_signal_summary || eventFlow.active_signal_summary || "");
  const flowTransitionMarkers = O(heartbeat.event_flow_transition_markers || eventFlow.transition_markers);
  const flowRouteStates = A(heartbeat.event_flow_route_states || eventFlow.changed_sector_routes);
  const flowSignalVessels = A(heartbeat.event_flow_signal_vessels || eventFlow.signal_vessels);
  const ascentStatus = H(heartbeat.tiktok_ascent_status || tiktokAscentTrack.activation_status || "WAIT");
  const ascentBoundary = H(heartbeat.tiktok_ascent_boundary || tiktokAscentTrack.activation_boundary || "release_readiness_proof_required");
  const ascentTarget = H(heartbeat.tiktok_ascent_target || tiktokEvolutionLine.target_point || "VOICE_OF_IMPERIUM_ADVERTISING_DEPARTMENT");
  const ascentLane = A(heartbeat.tiktok_ascent_lane || tiktokAscentTrack.ascent_lane);
  const liveChannel = O(app.liveChannel);
  const liveChannelHuman = liveChannel.mechanism === "sse"
    ? "SSE live-канал"
    : (liveChannel.mechanism === "polling" ? "инкрементальный polling" : H(liveChannel.mechanism || "канал"));
  const binding = O(state.bundle_binding);
  const bindingDisclosure = O(state.source_disclosure);
  const activeBundle = O(binding.active_bundle);
  const presentationBundle = O(binding.presentation_bundle);
  const fallbackBundle = O(binding.fallback_bundle);
  const companion = O(binding.companion_dependency);
  const activeBundleName = activeBundle.bundle_name || state.bundle_name || "n/a";
  const activeBundlePath = activeBundle.repo_relative_path || activeBundle.path || state.bundle_path || "n/a";
  const fallbackState = fallbackBundle.exists ? "configured" : "missing";
  const companionState = companion.required ? (companion.exists ? "connected" : "missing") : "optional";
  const brainConflicts = A(brain.conflicts);
  const oneScreenBrain = O(brain.one_screen);
  const repoControlBrain = O(brain.repo_control);
  const missionConsistency = O(brain.mission_consistency);
  const taskConsistency = O(brain.task_program_consistency);
  const commandSurface = O(brain.command_surface);
  const constitutionCore = O(brain.constitution);
  const controlLimits = O(brain.limits);
  const controlAgeAxis = O(brain.age_axis);
  const promptLineage = O(promptState.lineage);
  const promptSourceBrief = O(promptState.source_brief);
  const promptBoundary = O(promptState.text_boundary);
  const promptObservability = O(promptState.runtime_observability);
  const promptMissing = A(O(promptState.integrity).missing_fields);
  const processReason = heartbeat.latest_milestone_summary || latestEvt.summary || "операция обновляется по live feed";
  const historyNodes = A(O(state.production_history_seed).nodes);
  const historySortedDesc = historyNodes
    .slice()
    .sort((a, b) => Date.parse(String(b.occurred_at_utc || "")) - Date.parse(String(a.occurred_at_utc || "")));
  const oldestHistoryNode = historySortedDesc.length ? O(historySortedDesc[historySortedDesc.length - 1]) : {};
  const newestHistoryNode = O(historySortedDesc[0]);
  const systemAgeMinutes = Number.isFinite(Number(liveFactory.system_age_minutes))
    ? Number(liveFactory.system_age_minutes)
    : ageFromIso(oldestHistoryNode.occurred_at_utc);
  const regimeAgeMinutes = Number.isFinite(Number(liveFactory.regime_age_minutes))
    ? Number(liveFactory.regime_age_minutes)
    : ageFromIso(postWaveStage.started_at_utc);
  const lastStableAgeMinutes = Number.isFinite(Number(liveFactory.last_stable_point_age_minutes))
    ? Number(liveFactory.last_stable_point_age_minutes)
    : ageFromIso(liveFactory.last_stable_point_at_utc || oneScreenBrain.generated_at || repoControlBrain.generated_at);
  const ownerDecisionTriggers = A(liveBrain.owner_decision_triggers);
  const semanticGaps = A(semanticTruth.known_gaps);
  const exactTruthCount = Number.isFinite(Number(semanticTruth.exact_count)) ? Number(semanticTruth.exact_count) : 0;
  const derivedTruthCount = Number.isFinite(Number(semanticTruth.derived_count)) ? Number(semanticTruth.derived_count) : 0;
  const knownGapCount = Number.isFinite(Number(semanticTruth.gap_count)) ? Number(semanticTruth.gap_count) : semanticGaps.length;
  const topSemanticGap = semanticGaps.length
    ? semanticGaps.map((x) => shortText(H(x.id || x.status || "gap"), 28)).slice(0, 3).join(", ")
    : "none";
  const repoHygiene = O(brain.repo_worktree_hygiene || liveBrain.repo_worktree_hygiene);
  const repoHygieneClass = O(state.imperium_repo_hygiene_classification_state || brain.repo_hygiene_classification);
  const repoHygieneClassCounts = O(repoHygieneClass.classification_counts);
  const repoClassCanonical = Number(repoHygieneClassCounts.CANONICAL_MUST_TRACK ?? 0);
  const repoClassReview = Number(repoHygieneClassCounts.REVIEW_ARTIFACT_RETENTION ?? 0);
  const repoClassOwnerDecision = Number(repoHygieneClassCounts.NEEDS_OWNER_DECISION ?? 0);
  const cleanlinessVerdict = H(repoHygiene.cleanliness_verdict || "UNKNOWN");
  const codeSummary = O(codeBank.summary);
  const codeThresholds = O(codeSummary.threshold_counts || {});
  const codePressureIndex = Number(codeSummary.monolith_pressure_index ?? 0);
  const codeLargeStepHint = H(codeSummary.large_step_readiness_hint || "UNKNOWN");
  const codeAnomaly = O(codeBank.anomaly_ledger);
  const topMonoliths = A(codeBank.top_monoliths).slice(0, 3);
  const codeLocTotal = Number(codeSummary.total_loc ?? 0);
  const codeLocMeaningful = Number(codeSummary.meaningful_code_loc ?? codeLocTotal);
  const codeTrackedCount = Number(codeSummary.tracked_code_files_count ?? 0);
  const codeUntrackedCount = Number(codeSummary.untracked_code_files_count ?? 0);
  const codeScannedCount = Number(codeSummary.scanned_code_files_count ?? (codeTrackedCount + codeUntrackedCount));
  const dominanceRules = A(dominance.dominance_rules);
  const staleDominanceCount = Number(dominance.stale_rules_count ?? 0);
  const coverageRows = A(coverage.rows);
  const coverageVerdict = H(coverage.coverage_verdict || "UNKNOWN");
  const coverageMissing = Number(coverage.missing_rows ?? coverage.missing_count ?? 0);
  const coveragePointerOnly = Number(coverage.pointer_only_count ?? 0);
  const fullCoverageClaimable = Boolean(coverage.full_coverage_claimable);
  const custodesVigilance = H(custodes.vigilance_state || "UNKNOWN");
  const custodesLockMode = H(custodes.foundation_lock_mode || "UNKNOWN");
  const custodesThreats = A(custodes.threat_reasons);
  const emperorProof = H(throneAuthority.emperor_status || "UNKNOWN");
  const throneAnchorState = H(throneAuthority.anchor_state || throneAuthority.status || "UNKNOWN");
  const sovereignDisplayRank = H(throneAuthority.sovereign_display_rank || (throneAnchorState === "VALID" ? "EMPEROR" : "UNKNOWN"));
  const sovereignDisplayMode = H(throneAuthority.sovereign_display_machine_mode || (throneAnchorState === "VALID" ? "emperor" : "UNKNOWN"));
  const throneStatus = emperorProof;
  const throneBreach = Boolean(throneAuthority.throne_breach || throneAuthority.emperor_status_blocked);
  const throneAnchorPath = H(throneAuthority.authority_anchor_path || "docs/governance/GOLDEN_THRONE_AUTHORITY_ANCHOR_V1.json");
  const blockerClasses = O(brain.blocker_classes || liveBrain.blocker_classes);
  const governanceBlockers = A(blockerClasses.governance_blockers);
  const trustBlockers = A(blockerClasses.trust_blockers);
  const syncBlockers = A(blockerClasses.sync_blockers);
  const repoBlockers = A(blockerClasses.repo_hygiene_blockers);
  const runtimeBlockers = A(blockerClasses.runtime_transport_blockers);
  const sovereignBlockers = A(blockerClasses.sovereign_proof_blockers);
  const storagePostureState = H(storageHealth.storage_posture || storageHealth.overall_posture || semanticSecurity.sovereignty_posture || "UNKNOWN");
  const evolutionHealth = H(evolution.health || "UNKNOWN");
  const inquisitionIntegrity = H(inquisition.canon_integrity || "UNKNOWN");
  const storagePosture = storagePostureState;
  const mechanicusReadiness = Number(mechanicus.readiness_score ?? 0);
  const mechanicusLargeStep = H(mechanicus.large_step_readiness || "UNKNOWN");
  const mechanicusStopReasons = A(mechanicus.stop_reasons);
  const administratumGateState = H(administratum.gate_state || "UNKNOWN");
  const administratumMissingFields = A(administratum.missing_required_fields);
  const forceReadiness = H(forceDoctrine.readiness_band || "UNKNOWN");
  const forceBottlenecks = A(forceDoctrine.bottlenecks);
  const controlGateSummary = H(controlGates.gate_summary || "UNKNOWN");
  const controlGateRows = A(controlGates.gates);
  const truthSpineStatus = H(truthSpine.status || "UNKNOWN");
  const truthSyncPercentage = Number(O(truthSpine.sync_model).sync_percentage ?? 0);
  const dashboardTruthStatus = H(dashboardTruthEngine.status || "UNKNOWN");
  const bundleTruthStatus = H(bundleTruthChamber.status || "UNKNOWN");
  const worktreePurityStatus = H(worktreePurityGate.status || "UNKNOWN");
  const worktreeCleanliness = H(worktreePurityGate.cleanliness_verdict || cleanlinessVerdict);
  const addressLatticeStatus = H(addressLattice.status || "UNKNOWN");
  const antiLieStatus = H(antiLieModel.status || "UNKNOWN");
  const antiLieCritical = Number(antiLieModel.active_critical_count ?? 0);
  const truthLoopStatus = H(truthSupportLoop.status || "UNKNOWN");
  const truthLoopDrift = Number(truthSupportLoop.active_drift_count ?? 0);
  const palaceMode = H(O(palaceArchive.palace_state).active_palace_mode || "UNKNOWN");
  const archiveRole = H(O(palaceArchive.archive_resurrection_state).hdd_role || "UNKNOWN");
  const brainV2Layer1 = O(brainV2.layer_1_sovereignty);
  const brainV2Layer4 = O(brainV2.layer_4_force_capacity);
  const machineCpu = Number(O(machineCapability.compute_power).cpu_logical_cores ?? 0);
  const machineMemoryGb = O(machineCapability.compute_power).memory_total_gb;
  const organStrengthRows = A(organStrength.organ_strength);
  const missionContractId = H(activeMissionContract.contract_id || "UNKNOWN");
  const liveWorkStep = O(workVisibility.current_active_step);
  const liveWorkPhase = O(workVisibility.current_phase);
  const liveWorkOperation = O(workVisibility.current_operation);
  const liveWorkProgress = O(workVisibility.progress_markers);
  const liveWorkGroups = A(workVisibility.touched_surface_groups).slice(0, 4);
  const liveWorkRecent = A(workVisibility.recent_changes).slice(0, 4);
  const liveWorkBlocker = O(workVisibility.blocker_or_wait);
  const liveWorkGroupText = liveWorkGroups.length
    ? liveWorkGroups.map((item) => `${shortText(H(item.group_id || "group"), 26)}:${String(item.changes_count ?? 0)}`).join(" | ")
    : "groups n/a";
  const liveWorkRecentText = liveWorkRecent.length
    ? liveWorkRecent.map((item) => `${H(item.change_type || "change")} ${shortText(H(item.path || "path"), 40)}`).join(" || ")
    : "recent feed n/a";
  const trueFormProfiles = O(trueFormState.world_profiles);
  const worldProfile = (worldId) => O(trueFormProfiles[worldId]);
  const matryoshkaWorlds = [
    {
      id: "core_world",
      title: "Ядро сознания",
      icon: "CORE",
      state: H(brain.trust_state || "UNKNOWN"),
      summary: H(worldProfile("core_world").summary_ru || "Суверенное ядро: мозг, конституция, owner-границы решений."),
      overview: `trust=${H(brain.trust_state || "UNKNOWN")} | conflict=${H(brain.conflict_state || "UNKNOWN")}`,
      why: shortText(H(worldProfile("core_world").why_ru || oneScreenBrain.trust_reason || constitutionCore.overall_verdict || "ядро сверяет миссию/команды/конституцию"), 150),
      trust: H(worldProfile("core_world").trust_ru || "Можно верить, когда trust и constitution не расходятся."),
      limit: shortText(H(worldProfile("core_world").limit_ru || controlLimits.blocking_reason_detail || "owner-решение обязательно для канон-изменений"), 150),
      proof: [
        `one_screen=${H(oneScreenBrain.trust_verdict || "UNKNOWN")}`,
        `constitution=${H(constitutionCore.overall_verdict || "UNKNOWN")}`,
        `owner_triggers=${String(ownerDecisionTriggers.length)}`
      ],
      technical: [
        `source=runtime/repo_control_center/one_screen_status.json`,
        `command_mode=${H(commandSurface.latest_execution_mode || "UNKNOWN")}`,
        `age_axis=${ageText(controlAgeAxis.control_plane_last_refresh_age_minutes)}`
      ],
      subsectors: [
        { title: "Миссия и команды", state: H(missionConsistency.verdict || "UNKNOWN"), note: shortText("Проверка согласованности миссии и командной поверхности.", 86) },
        { title: "Конституция и канон", state: H(constitutionCore.overall_verdict || "UNKNOWN"), note: shortText("Граница суверенных изменений и owner-gate.", 86) },
        { title: "Триггеры владельца", state: ownerDecisionTriggers.length ? "BLOCKED" : "PROVEN", note: shortText("Эскалационные случаи фиксируются явно, не скрываются.", 86) }
      ]
    },
    {
      id: "custodes_world",
      title: "Adeptus Custodes",
      icon: "CUSTODES",
      state: custodesVigilance,
      summary: H(worldProfile("custodes_world").summary_ru || "Custodes охраняет фундамент, Трон и ментальную целостность канона."),
      overview: `vigilance=${custodesVigilance} | lock=${custodesLockMode}`,
      why: shortText(H(worldProfile("custodes_world").why_ru || "Custodes не выполняет рутину; он держит верхний контур foundation threats."), 150),
      trust: H(worldProfile("custodes_world").trust_ru || "Можно верить, потому что lock-mode и угрозы выводятся явно и не прячутся."),
      limit: shortText(H(worldProfile("custodes_world").limit_ru || "Lock assertion не подменяет owner sovereignty; требуется подтверждение владельца."), 150),
      proof: [
        `vigilance=${custodesVigilance}`,
        `lock_mode=${custodesLockMode}`,
        `threats=${custodesThreats.length}`,
        `throne_status=${throneStatus}`
      ],
      technical: [
        `source=${H(custodes.source_path || "IMPERIUM_ADEPTUS_CUSTODES_STATE_SURFACE_V1.json")}`,
        `guardian_scope=${shortText(A(custodes.guardian_scope).join(","), 78)}`,
        `owner_ack_required=${H(String(custodes.owner_ack_required))}`,
        `throne_anchor=${throneAnchorPath}`
      ],
      subsectors: [
        { title: "Фундамент", state: cleanlinessVerdict === "CLEAN" ? "PROVEN" : "BLOCKED", note: shortText("Lock-контур реагирует на foundation-grade угрозы.", 86) },
        { title: "Трон и authority", state: throneStatus, note: shortText("Authority берется только из canonical anchor path.", 86) },
        { title: "Ack владельца", state: custodes.owner_ack_required ? "BLOCKED" : "PROVEN", note: shortText("Custodes требует owner acknowledgment при серьезной угрозе.", 86) }
      ]
    },
    {
      id: "mechanicus_world",
      title: "Adeptus Mechanicus",
      icon: "MECH",
      state: mechanicusLargeStep,
      summary: "Сердце исполнения: код, архитектура, емкость машины и пределы больших шагов.",
      overview: `readiness=${mechanicusReadiness} | large_step=${mechanicusLargeStep}`,
      why: "Mechanicus оценивает, что реально исполнимо на этой машине, а что должно эскалироваться владельцу.",
      trust: "Можно верить, когда bottleneck и stop reasons показаны явно, без фальшивого green.",
      limit: shortText(mechanicusStopReasons.join("; ") || "явных stop-reason нет", 140),
      proof: [
        `readiness_score=${String(mechanicusReadiness)}`,
        `large_step=${mechanicusLargeStep}`,
        `cpu=${String(machineCpu)} | ram_gb=${String(machineMemoryGb ?? "n/a")}`,
        `organ_strength_rows=${String(organStrengthRows.length)}`
      ],
      technical: [
        `source=${H(mechanicus.source_path || "IMPERIUM_ADEPTUS_MECHANICUS_STATE_SURFACE_V1.json")}`,
        `machine_manifest=${H(forceDoctrine.machine_capability_manifest_path || "runtime/imperium_force/IMPERIUM_MACHINE_CAPABILITY_MANIFEST_V1.json")}`,
        `organ_strength=${H(forceDoctrine.organ_strength_surface_path || "runtime/imperium_force/IMPERIUM_ORGAN_STRENGTH_SURFACE_V1.json")}`
      ],
      subsectors: [
        { title: "Емкость машины", state: forceReadiness, note: shortText(`CPU=${machineCpu}, RAM=${String(machineMemoryGb ?? "n/a")}GB, readiness=${forceReadiness}`, 90) },
        { title: "Риск монолитов", state: H(mechanicus.code_bank_status || codeSummary.status_classification || "UNKNOWN"), note: shortText("Крупные файлы и рост кода видны как ограничение исполнения.", 86) },
        { title: "Stop reasons", state: mechanicusStopReasons.length ? "BLOCKED" : "PROVEN", note: shortText(mechanicusStopReasons.join("; ") || "stop reasons не активны", 86) }
      ]
    },
    {
      id: "administratum_world",
      title: "Administratum",
      icon: "ADMIN",
      state: administratumGateState,
      summary: "Контрактный орган: перевод owner-намерения в строгий исполнимый mission contract.",
      overview: `gate=${administratumGateState} | missing=${String(administratumMissingFields.length)}`,
      why: "Administratum режет неоднозначность и не дает машине достраивать неизвестное молча.",
      trust: "Можно верить, когда required fields, unknowns и assumptions видны как gate-сигналы.",
      limit: shortText(administratumMissingFields.join(", ") || "критичные поля контракта присутствуют", 140),
      proof: [
        `contract_id=${missionContractId}`,
        `gate_state=${administratumGateState}`,
        `missing_fields=${String(administratumMissingFields.length)}`,
        `owner_ack=${String(Boolean(administratum.owner_ack_required))}`
      ],
      technical: [
        `source=${H(administratum.source_path || "IMPERIUM_ADMINISTRATUM_STATE_SURFACE_V1.json")}`,
        `contract_path=${H(administratum.active_contract_path || "runtime/administratum/IMPERIUM_ACTIVE_MISSION_CONTRACT_V1.json")}`,
        `escalation_rule=${shortText(H(administratum.escalation_rule || "n/a"), 92)}`
      ],
      subsectors: [
        { title: "Контракт миссии", state: missionContractId !== "UNKNOWN" ? "ACTIVE" : "BLOCKED", note: shortText(`active_contract=${missionContractId}`, 86) },
        { title: "Stop-and-ask", state: administratumGateState, note: shortText("При RED_BLOCK шаг останавливается и требует owner guidance.", 86) },
        { title: "Неопределенность", state: (Number(administratum.unknowns_count ?? 0) + Number(administratum.assumptions_count ?? 0)) > 0 ? "WARNING" : "PROVEN", note: shortText(`unknowns=${String(administratum.unknowns_count ?? 0)} assumptions=${String(administratum.assumptions_count ?? 0)}`, 86) }
      ]
    },
    {
      id: "factory_world",
      title: "Мир фабрики",
      icon: "FACTORY",
      state: H(factoryAssembly.vector_state || "ACTIVE"),
      summary: H(worldProfile("factory_world").summary_ru || "Завод Империума как промышленный организм линий, камер и gate-колец."),
      overview: `lanes=${String(A(factoryAssembly.conveyor_lanes).length)} | gates=${String(A(factoryAssembly.stage_gates).length)}`,
      why: shortText(H(worldProfile("factory_world").why_ru || O(factoryAssembly.factory_morphology_profile).style_language || "industrial cognition"), 150),
      trust: H(worldProfile("factory_world").trust_ru || "Можно верить, потому что стадии и quality-gates привязаны к source-backed статусам."),
      limit: shortText(H(worldProfile("factory_world").limit_ru || O(factoryAssembly.post_release_split).status || "release boundary еще не доказана"), 150),
      proof: [
        `stage_transition_matrix=${String(A(factoryAssembly.stage_transition_matrix).length)}`,
        `quality_checkpoints=${String(A(factoryAssembly.quality_checkpoints).length)}`,
        `living_flow_relations=${shortText(Object.keys(O(factoryAssembly.living_flow_relations)).join(","), 78)}`
      ],
      technical: [
        `source=${H(factoryAssembly.source_path || "IMPERIUM_FACTORY_PRODUCTION_STATE_V1.json")}`,
        `product_map_source=${H(factoryAssembly.product_map_source_path || "IMPERIUM_PRODUCT_EVOLUTION_MAP_V1.json")}`,
        `resource_rule=${H(O(factoryAssembly.resource_discipline).machine_efficient_visual_rule ? "LOW_COST_REQUIRED" : "UNKNOWN")}`
      ],
      subsectors: [
        { title: "Конвейерные линии", state: H(O(A(factoryAssembly.conveyor_lanes)[0]).state || "ACTIVE"), note: shortText("Каждая линия ведет от анализа до release границы.", 86) },
        { title: "Кольцо gate-проверок", state: H(O(A(factoryAssembly.stage_gates)[0]).status || "ACTIVE"), note: shortText("Gate-статусы показывают, где есть доказательство, а где ожидание.", 86) },
        { title: "Камеры качества", state: H(O(A(factoryAssembly.quality_checkpoints)[0]).status || "ACTIVE"), note: shortText("Качество и trust parity проверяются отдельно от визуала.", 86) }
      ]
    },
    {
      id: "tiktok_world",
      title: "Мир TikTok Agent",
      icon: "TIKTOK",
      state: H(productProcessState || "ACTIVE"),
      summary: H(worldProfile("tiktok_world").summary_ru || "Сборка модулей продукта и ветка восхождения к Voice of Imperium."),
      overview: `process=${H(productProcessState || "UNKNOWN")} | ascent=${H(ascentStatus || "WAIT")}`,
      why: shortText(H(worldProfile("tiktok_world").why_ru || runtimeLatestSummary || latestChangeText || "сборка идет по модульным rails"), 150),
      trust: H(worldProfile("tiktok_world").trust_ru || "Можно верить, когда readiness-gates и proof lane явно видны."),
      limit: shortText(H(worldProfile("tiktok_world").limit_ru || ascentBoundary || "release readiness required"), 150),
      proof: [
        `operation=${H(runtimeOperation || "UNKNOWN")}`,
        `latest_proof=${shortText(latestProofText, 80)}`,
        `prompt_boundary=${H(promptBoundary.trusted_boundary || "UNKNOWN")}`
      ],
      technical: [
        `runtime_source=${H(runtimeSourceMode || "UNKNOWN")}`,
        `failure_reason=${H(runtimeFailure || "none")}`,
        `recovery_signal=${H(runtimeRecovery || "none")}`
      ],
      subsectors: [
        { title: "Сборочный стек", state: H(O(A(O(A(factoryAssembly.products)[0]).assembly_modules)[0]).state || "ACTIVE"), note: shortText("Псевдо-3D слои показывают готовность подсистем.", 86) },
        { title: "Зона блокеров", state: blockerText && blockerText !== "none" ? "BLOCKED" : "PROVEN", note: shortText("Блокер отображается как отдельная операционная зона.", 86) },
        { title: "Ветка восхождения", state: H(ascentStatus || "WAIT"), note: shortText("Будущая роль Voice of Imperium видна как отдельный путь, не как факт.", 86) }
      ]
    },
    {
      id: "evolution_world",
      title: "Мир эволюции",
      icon: "EVOLVE",
      state: evolutionHealth,
      summary: H(worldProfile("evolution_world").summary_ru || "Тихий канал роста: кандидаты, owner-очередь, переносимые gain-линии."),
      overview: `health=${H(evolutionHealth)} | candidates=${String(A(evolution.insight_candidates).length)}`,
      why: H(worldProfile("evolution_world").why_ru || "Эволюция читает только канонические pointer-surfaces, а не весь мир."),
      trust: H(worldProfile("evolution_world").trust_ru || "Можно верить, если кандидат не проходит в канон без owner-решения."),
      limit: shortText(H(worldProfile("evolution_world").limit_ru || O(evolution.channel_mode).deep_review_mode || "OWNER_AUTH_REQUIRED"), 120),
      proof: [
        `stage_map=${String(A(evolution.stage_map || evolution.system_stage_map).length)}`,
        `owner_queue=${String(A(evolution.owner_approval_queue).length)}`,
        `accepted_gains=${String(A(evolution.accepted_transfer_gains).length)}`
      ],
      technical: [
        `source=${H(evolution.source_path || "IMPERIUM_EVOLUTION_STATE_SURFACE_V1.json")}`,
        `resource_profile=${H(O(evolution.channel_mode).resource_profile || "LOW_COST_POINTER_BASED")}`,
        `mode=${H(O(evolution.channel_mode).default || evolution.current_mode || "QUIET_HEARTBEAT")}`
      ],
      subsectors: [
        { title: "Карта стадий", state: H(evolutionHealth), note: shortText("Показывает текущую и целевую стадию по системным фронтам.", 86) },
        { title: "Плодовая очередь", state: A(evolution.owner_approval_queue).length ? "WAIT" : "PROVEN", note: shortText("Кандидаты ждут owner-решения перед канонизацией.", 86) },
        { title: "Переносимые gain-ы", state: A(evolution.accepted_transfer_gains).length ? "PROVEN" : "WAIT", note: shortText("Принятые усиления фиксируются как reusable pattern.", 86) }
      ]
    },
    {
      id: "inquisition_world",
      title: "Мир инквизиции",
      icon: "INQ",
      state: inquisitionIntegrity,
      summary: H(worldProfile("inquisition_world").summary_ru || "Контур бдительности: drift/heresy-кейсы, review holding zone, owner escalation."),
      overview: `integrity=${H(inquisitionIntegrity)} | alerts=${String(A(inquisition.active_heresy_alerts).length)}`,
      why: shortText(H(worldProfile("inquisition_world").why_ru || O(inquisition.current_integrity_state).drift_level || "MEDIUM"), 120),
      trust: H(worldProfile("inquisition_world").trust_ru || "Можно верить, потому что авто-удаление запрещено и review обязателен."),
      limit: H(worldProfile("inquisition_world").limit_ru || "Exterminatus только proposal, никогда auto-action."),
      proof: [
        `heresy_classes=${String(A(inquisition.heresy_classes).length)}`,
        `open_alerts=${String(A(inquisition.active_heresy_alerts).length)}`,
        `review_policy=${H(O(inquisition.review_holding_zone).policy || "NO_AUTO_DELETE")}`
      ],
      technical: [
        `source=${H(inquisition.source_path || "IMPERIUM_INQUISITION_STATE_SURFACE_V1.json")}`,
        `mode=${H(O(inquisition.channel_mode).default || "SILENT_HEARTBEAT_WATCH")}`,
        `drift_level=${H(O(inquisition.current_integrity_state).drift_level || "UNKNOWN")}`
      ],
      subsectors: [
        { title: "Зона ереси", state: A(inquisition.active_heresy_alerts).length ? "ACTIVE" : "PROVEN", note: shortText("Кейсы фиксируются и отправляются в review holding zone.", 86) },
        { title: "Контроль дрейфа", state: H(O(inquisition.current_integrity_state).drift_level || "MEDIUM"), note: shortText("Показывает риск отрыва от канона по активным фронтам.", 86) },
        { title: "Owner escalation", state: "ACTIVE", note: shortText("Инквизиция эскалирует, но не выполняет irreversible action сама.", 86) }
      ]
    },
    {
      id: "memory_world",
      title: "Мир памяти",
      icon: "MEM",
      state: H(semanticMemory.known_state_integrity || "ACTIVE"),
      summary: H(worldProfile("memory_world").summary_ru || "Хронология, текущая цепочка, возраст системы и последняя стабильная точка."),
      overview: `system_age=${ageText(systemAgeMinutes)} | stable_age=${ageText(lastStableAgeMinutes)}`,
      why: H(worldProfile("memory_world").why_ru || "Без памяти система теряет контекст и повторяет expensive bundle-археологию."),
      trust: H(worldProfile("memory_world").trust_ru || "Можно верить, когда chronology узлы имеют source_path и truth_class."),
      limit: shortText(H(worldProfile("memory_world").limit_ru || topSemanticGap || "none"), 120),
      proof: [
        `last_working_step=${H(semanticMemory.last_working_canonical_step_id || "UNKNOWN")}`,
        `history_nodes=${String(historySortedDesc.length)}`,
        `regime_age=${ageText(regimeAgeMinutes)}`
      ],
      technical: [
        `source_mode=${H(bindingDisclosure.selection_mode || binding.selection_mode || "unknown")}`,
        `bundle=${H(activeBundleName)}`,
        `memory_truth=${H(liveSemantic.truth_class || semantic.truth_class || "DERIVED_CANONICAL")}`
      ],
      subsectors: [
        { title: "Хронология", state: historySortedDesc.length ? "PROVEN" : "WAIT", note: shortText("Последовательность подтвержденных шагов с привязкой к source.", 86) },
        { title: "Возраст оси", state: "ACTIVE", note: shortText("Система/режим/последняя стабильная точка читаются как живые метрики.", 86) },
        { title: "Контур continuity", state: "ACTIVE", note: shortText("Капсула и mutable tracker держат вход в текущую вершину.", 86) }
      ]
    },
    {
      id: "canon_world",
      title: "Мир канона",
      icon: "CANON",
      state: H(constitutionCore.overall_verdict || "ACTIVE"),
      summary: H(worldProfile("canon_world").summary_ru || "Конституция, governance, owner law и границы изменений."),
      overview: `canon_drift=${H(semanticConstitution.canon_drift_risk || "UNKNOWN")} | posture=${H(semanticConstitution.doctrine_posture || "UNKNOWN")}`,
      why: H(worldProfile("canon_world").why_ru || "Фундамент и mutable слой не смешиваются: это защита от ложной стабильности."),
      trust: H(worldProfile("canon_world").trust_ru || "Можно верить, если authority boundary и source disclosure сохраняются явно."),
      limit: shortText(H(worldProfile("canon_world").limit_ru || semanticConstitution.active_doctrine_posture || "owner decision required for foundation mutations"), 130),
      proof: [
        `governance_acceptance=${H(constitutionCore.governance_acceptance || "UNKNOWN")}`,
        `breaches=${String(semanticConstitution.breach_count ?? "n/a")}`,
        `warnings=${String(semanticConstitution.warning_count ?? "n/a")}`
      ],
      technical: [
        `entrypoint=docs/governance/SYSTEM_ENTRYPOINT_V1.md`,
        `foundation_index=docs/governance/FOUNDATION_INDEX_V1.md`,
        `authority_map=docs/governance/AUTHORITY_OF_CHANGE_MAP_V1.md`
      ],
      subsectors: [
        { title: "Конституция", state: H(constitutionCore.overall_verdict || "UNKNOWN"), note: shortText("Канон определяет что неизменно и где нужен owner gate.", 86) },
        { title: "Law-output контракт", state: "ACTIVE", note: shortText("Single-artifact handoff и short-first контракт держатся как закон формы.", 86) },
        { title: "Границы authority", state: "ACTIVE", note: shortText("Изменения фундамента разрешены только sovereign решением.", 86) }
      ]
    },
    {
      id: "storage_world",
      title: "Мир целостности",
      icon: "STORAGE",
      state: storagePosture,
      summary: H(worldProfile("storage_world").summary_ru || "Storage/integrity/capsule готовность и восстановимость до последнего шага."),
      overview: `sovereignty=${H(storagePosture)} | exposure=${H(semanticSecurity.external_exposure_state || "UNKNOWN")}`,
      why: H(worldProfile("storage_world").why_ru || "Суверенный локальный контур защищает truth-channel от внешнего перезаписи."),
      trust: H(worldProfile("storage_world").trust_ru || "Можно верить, когда local-only posture и visibility restrictions явно подтверждены."),
      limit: shortText(H(worldProfile("storage_world").limit_ru || semanticSecurity.recovery_readiness_posture || "NOT_VALIDATED"), 120),
      proof: [
        `external_exposure=${H(semanticSecurity.external_exposure_state || "UNKNOWN")}`,
        `visibility=${H(semanticSecurity.visibility_restrictions_posture || "UNKNOWN")}`,
        `recovery=${H(semanticSecurity.recovery_readiness_posture || "UNKNOWN")}`
      ],
      technical: [
        `storage_surface=runtime/imperium_storage_control/IMPERIUM_STORAGE_HEALTH_SURFACE_V1.json`,
        `capsule_root=docs/review_artifacts/ULTIMATE_TRANSFER_CAPSULE_SYSTEM_V1/`,
        `migration_status=${H(semanticSecurity.recovery_readiness_posture || "PLACEHOLDER")}`
      ],
      subsectors: [
        { title: "Суверенность", state: H(storagePosture), note: shortText("Safe mirror не sovereign source, внешний экспорт только вручную.", 86) },
        { title: "Capsule continuity", state: "ACTIVE", note: shortText("Новый чат должен входить в текущую вершину без археологии.", 86) },
        { title: "Migration readiness", state: "WAIT", note: shortText("Двухдисковая миграция пока doctrine-only, не fake validated.", 86) }
      ]
    }
  ];
  const worldById = new Map(matryoshkaWorlds.map((world) => [world.id, world]));
  if (!worldById.has(app.fullVision.sectorFocus)) {
    app.fullVision.sectorFocus = matryoshkaWorlds[0]?.id || "core_world";
  }
  if (!["overview", "proof", "technical"].includes(app.fullVision.layerFocus)) {
    app.fullVision.layerFocus = "overview";
  }
  if (!["orbit", "sector", "subsector"].includes(app.fullVision.depthFocus)) {
    app.fullVision.depthFocus = "orbit";
  }
  const selectedWorld = worldById.get(app.fullVision.sectorFocus) || matryoshkaWorlds[0];
  const selectedLayer = app.fullVision.layerFocus;
  const selectedDepth = app.fullVision.depthFocus;
  const selectedWorldIndex = Math.max(0, matryoshkaWorlds.findIndex((world) => world.id === selectedWorld.id));
  const selectedSubsectors = A(selectedWorld.subsectors);
  let selectedSubsectorIndex = Number(app.fullVision.subsectorFocus);
  if (!Number.isFinite(selectedSubsectorIndex)) selectedSubsectorIndex = 0;
  if (selectedSubsectorIndex < 0 || selectedSubsectorIndex >= selectedSubsectors.length) {
    selectedSubsectorIndex = 0;
  }
  app.fullVision.subsectorFocus = selectedSubsectorIndex;
  const selectedSubsector = O(selectedSubsectors[selectedSubsectorIndex]);
  const selectedLayerTitle = selectedLayer === "proof"
    ? "Proof-слой"
    : (selectedLayer === "technical" ? "Технический слой" : "Owner-объяснение");
  const depthTitle = selectedDepth === "subsector"
    ? "Глубина 3: под-сектор"
    : (selectedDepth === "sector" ? "Глубина 2: сектор" : "Глубина 1: ядро и орбиты");
  const depthHint = selectedDepth === "subsector"
    ? "Вы уже внутри под-сектора: можно вернуться в сектор или в ядро без потери контекста."
    : (selectedDepth === "sector"
      ? "Вы на уровне сектора: видна причина, proof и ограничение перед углублением."
      : "Вы на внешней орбите: сначала обзор системы, затем вход в нужный мир.");
  const activeWorldCount = matryoshkaWorlds.filter((world) => {
    const st = H(world.state).toUpperCase();
    return st.includes("ACTIVE") || st.includes("IN_PROGRESS");
  }).length;
  const blockedWorldCount = matryoshkaWorlds.filter((world) => {
    const st = H(world.state).toUpperCase();
    return st.includes("BLOCK") || st.includes("CRITICAL") || st.includes("FAIL") || st.includes("CONFLICT");
  }).length;
  const provenWorldCount = matryoshkaWorlds.filter((world) => {
    const st = H(world.state).toUpperCase();
    return st.includes("PROVEN") || st.includes("PASS") || st.includes("TRUSTED");
  }).length;
  const orbitNodes = matryoshkaWorlds.map((world, idx) => {
    const angle = -90 + ((360 / Math.max(1, matryoshkaWorlds.length)) * idx);
    const ring = idx % 2 === 0 ? "inner" : "outer";
    const radius = ring === "inner" ? 184 : 234;
    return { world, angle, ring, radius };
  });
  const layerBody = selectedLayer === "proof"
    ? selectedWorld.proof
    : (selectedLayer === "technical" ? selectedWorld.technical : [selectedWorld.overview, selectedWorld.why, selectedWorld.trust, selectedWorld.limit]);
  const layerTitle = selectedLayerTitle;
  const ownerNowText = shortText(H(selectedSubsector.note || selectedWorld.why || selectedWorld.summary), 180);
  const ownerTrustText = shortText(H(selectedWorld.trust || "граница доверия не указана"), 180);
  const ownerLimitText = shortText(H(selectedWorld.limit || "ограничение не указано"), 180);
  const ownerQuestionText = shortText(H(selectedWorld.limit || selectedSubsector.note || "под вопросом, что еще не доказано"), 150);
  const ownerNextAction = selectedWorld.id === "factory_world"
    ? "Проверьте активную линию фабрики и gate-переход, где блокируется release boundary."
    : (selectedWorld.id === "tiktok_world"
      ? "Сверьте readiness-gates TikTok Agent и ветку восхождения к Voice of Imperium без premature claim."
      : (selectedWorld.id === "inquisition_world"
        ? "Проверьте hold-зону кейсов и owner escalation path перед любым irreversible действием."
        : "Уточните proof-слой выбранного сектора и только потом переходите в технический drilldown."));
  const tiktokProduct = O(A(factoryAssembly.products).find((p) => String(p.product_id || "").toLowerCase() === "tiktok_agent_platform") || A(factoryAssembly.products)[0]);
  const worldDeepCards = (() => {
    if (selectedWorld.id === "factory_world") {
      const laneCards = A(factoryAssembly.conveyor_lanes).slice(0, 4).map((lane) => `
        <div class="sector-deep-card ${badgeClass(lane.state || "UNKNOWN")}">
          <div class="sector-deep-title">${esc(lane.title_ru || lane.lane_id || "factory_lane")}</div>
          <div class="sector-deep-note">Стадия: ${esc(lane.active_stage || "n/a")} | Блок: ${esc(lane.blocked_stage || "n/a")}</div>
          <div class="sector-deep-note">${esc(shortText(A(lane.stage_route).join(" -> ") || "route n/a", 120))}</div>
        </div>
      `).join("");
      return laneCards || `<div class="vision-card-subtle">Factory lanes пока не загружены.</div>`;
    }
    if (selectedWorld.id === "tiktok_world") {
      const moduleCards = A(tiktokProduct.assembly_modules).slice(0, 6).map((module) => `
        <div class="sector-deep-card ${badgeClass(module.state || "UNKNOWN")}">
          <div class="sector-deep-title">${esc(module.module_id || "module")}</div>
          <div class="sector-deep-note">state=${esc(module.state || "UNKNOWN")} | gate=${esc(module.gate || "n/a")}</div>
          <div class="sector-deep-note">readiness=${esc(module.readiness_score_label || "n/a")} | truth=${esc(module.truth_class || "UNKNOWN")}</div>
        </div>
      `).join("");
      return moduleCards || `<div class="vision-card-subtle">TikTok assembly modules пока не загружены.</div>`;
    }
    if (selectedWorld.id === "evolution_world") {
      const queueCards = A(evolution.owner_approval_queue).slice(0, 3).map((item) => `
        <div class="sector-deep-card ${badgeClass(item.status || "WAIT")}">
          <div class="sector-deep-title">${esc(item.candidate_id || item.title || "candidate")}</div>
          <div class="sector-deep-note">${esc(shortText(item.reason || item.note || "owner approval required", 120))}</div>
        </div>
      `).join("");
      return queueCards || `<div class="vision-card-subtle">В owner approval queue пока нет новых кандидатов.</div>`;
    }
    if (selectedWorld.id === "inquisition_world") {
      const alertCards = A(inquisition.active_heresy_alerts).slice(0, 3).map((item) => `
        <div class="sector-deep-card ${badgeClass(item.status || "ACTIVE")}">
          <div class="sector-deep-title">${esc(item.alert_id || item.class_id || "heresy_case")}</div>
          <div class="sector-deep-note">${esc(shortText(item.reason || item.description || "дрейф зафиксирован", 120))}</div>
        </div>
      `).join("");
      return alertCards || `<div class="vision-card-subtle">Активных heresy-alert кейсов сейчас нет.</div>`;
    }
    if (selectedWorld.id === "memory_world") {
      const memoryCards = historySortedDesc.slice(0, 3).map((node) => `
        <div class="sector-deep-card ${badgeClass(node.truth_class || "PROVEN")}">
          <div class="sector-deep-title">${esc(node.node_title || node.node_id || "history_node")}</div>
          <div class="sector-deep-note">${esc(shortText(node.summary || node.description || "node summary n/a", 120))}</div>
          <div class="sector-deep-note">at=${esc(shortTime(node.occurred_at_utc || ""))}</div>
        </div>
      `).join("");
      return memoryCards || `<div class="vision-card-subtle">Исторические узлы пока не отображены.</div>`;
    }
    return `<div class="vision-card-subtle">Для этого мира глубокий срез читается через proof и technical layer.</div>`;
  })();

  if (E("visionBundleHealth")) {
    E("visionBundleHealth").innerHTML = `
      <div class="vision-chip-row">
        <div class="vision-chip"><span class="vision-chip-key">Пакет</span><span class="vision-chip-val">${esc(activeBundleName)}</span></div>
        <div class="vision-chip"><span class="vision-chip-key">Состав</span><span class="vision-chip-val">${esc(`${O(state.file_counts).total ?? "n/a"} файлов`)}</span></div>
        <div class="vision-chip"><span class="vision-chip-key">Источник</span><span class="vision-chip-val">${esc(bindingDisclosure.selection_mode || binding.selection_mode || "неизвестно")}</span></div>
        <div class="vision-chip"><span class="vision-chip-key">Резерв</span><span class="vision-chip-val">${esc(fallbackState)}</span></div>
        <div class="vision-chip"><span class="vision-chip-key">Companion</span><span class="vision-chip-val">${esc(companionState === "connected" ? "подключен" : companionState === "missing" ? "отсутствует" : companionState)}</span></div>
        <div class="vision-chip"><span class="vision-chip-key">Паритет</span><span class="vision-chip-val">${esc(O(state.parity).overall || "PARTIAL")}</span></div>
        <div class="vision-chip"><span class="vision-chip-key">Режим</span><span class="vision-chip-val">bundle-first / truth-first</span></div>
      </div>
      <div class="vision-card-subtle">Что происходит: owner-экран читает один активный truth-пакет и показывает его без подмены.</div>
      <div class="vision-card-subtle">Можно ли верить: да, пока source disclosure = SOURCE_EXACT и companion явно указан.</div>
      <details class="vision-inline-details">
        <summary>Технические детали источников</summary>
        <div class="vision-inline-body">
          Активный evidence-source: ${pv(activeBundlePath)}<br>
          Вход presentation-слоя: ${pv(presentationBundle.repo_relative_path || presentationBundle.path || "n/a")}<br>
          Secondary fallback: ${pv(fallbackBundle.repo_relative_path || fallbackBundle.path || "n/a")} [${esc(fallbackState)}]<br>
          Companion (PATH B): ${pv(companion.repo_relative_path || companion.path || DEFAULT_COMPANION)} [${esc(companionState)}]<br>
          Причина выбора: ${esc(bindingDisclosure.selection_reason || binding.selection_reason || "n/a")}<br>
          Адаптер: ${esc(`${O(state.adapter).adapter_id || "n/a"} ${O(state.adapter).adapter_version || ""}`.trim())}
        </div>
      </details>
    `;
  }

  if (E("visionSignalBand")) {
    const signalTrustRaw = H(semanticConstitution.trust_status || liveBrain.trust_state || brain.trust_state || "UNKNOWN");
    const signalConflictRaw = H(brain.conflict_state || liveBrain.conflict_state || "UNKNOWN");
    const decisionPendingCount = cp.total - cp.ready;
    const signalDecisionRaw = decisionPendingCount > 0
      ? `${decisionPendingCount} checkpoint-границ открыто`
      : "критичных checkpoint-границ нет";
    const liveChannelPayload = O(live.live_update_channel);
    const signalLiveRaw = H(liveChannelPayload.primary || liveChannel.mechanism || "UNKNOWN");
    const signalOperationRaw = H(runtimeOperation || ws.objective || "UNKNOWN");
    const signalRecoveryRaw = H(runtimeRecovery || "none");
    const operationTone = runtimeFailure && runtimeFailure !== "none" ? "critical" : (runtimeProcessState && key(runtimeProcessState).includes("process") ? "trust" : "warning");
    const decisionTone = decisionPendingCount > 0 || ownerDecisionTriggers.length ? "warning" : "trust";
    const signalCounters = O(eventFlow.state_counters);
    const signalRoutes = A(eventFlow.changed_sector_routes)
      .filter((route) => Number(route.event_count ?? 0) > 0 || ["ACTIVE", "BLOCKED", "PROVEN"].includes(H(route.status).toUpperCase()))
      .slice(0, 4);
    const signalVessels = A(eventFlow.signal_vessels).slice(0, 4);
    E("visionSignalBand").innerHTML = `
      <div class="signal-band-grid">
        <div class="signal-band-card ${semanticTone(signalTrustRaw)}">
          <div class="signal-band-title">Доверие системы</div>
          <div class="signal-band-value">${esc(humanValue(statusRu(signalTrustRaw), "нет подтвержденного trust-состояния"))}</div>
          <div class="signal-band-note">source: constitution/trust chain</div>
        </div>
        <div class="signal-band-card ${semanticTone(signalConflictRaw)}">
          <div class="signal-band-title">Конфликт управления</div>
          <div class="signal-band-value">${esc(humanValue(statusRu(signalConflictRaw), "конфликтный статус не подтвержден"))}</div>
          <div class="signal-band-note">source: brain/conflict chain</div>
        </div>
        <div class="signal-band-card ${decisionTone}">
          <div class="signal-band-title">Фокус owner-решения</div>
          <div class="signal-band-value">${esc(signalDecisionRaw)}</div>
          <div class="signal-band-note">${esc(ownerDecisionTriggers.length ? ownerDecisionTriggers.join(", ") : "owner-trigger не активен")}</div>
        </div>
        <div class="signal-band-card ${semanticTone(signalLiveRaw)}">
          <div class="signal-band-title">Живой канал</div>
          <div class="signal-band-value">${esc(humanValue(signalLiveRaw))}</div>
          <div class="signal-band-note">fallback: ${esc(humanValue(liveChannelPayload.fallback || "n/a"))} | event_bus: ${esc(humanValue(liveChannelPayload.event_bus || "n/a"))}</div>
        </div>
        <div class="signal-band-card ${operationTone}">
          <div class="signal-band-title">Текущая операция</div>
          <div class="signal-band-value">${esc(humanValue(shortText(signalOperationRaw, 58)))}</div>
          <div class="signal-band-note">recovery: ${esc(humanValue(shortText(signalRecoveryRaw, 46), "нет сигнала восстановления"))}</div>
        </div>
        <div class="signal-band-card ${semanticTone(eventFlow.status || "UNKNOWN")}">
          <div class="signal-band-title">Event-flow spine</div>
          <div class="signal-band-value">${esc(humanValue(eventFlow.status || "UNKNOWN"))}</div>
          <div class="signal-band-note">классов: ${esc(String(A(eventFlow.event_classes).length))} | хвост: ${esc(String(A(eventFlow.event_tail).length))}</div>
        </div>
        <div class="signal-band-card ${semanticTone(diffPreview.status || "UNKNOWN")}">
          <div class="signal-band-title">Diff/Preview</div>
          <div class="signal-band-value">${esc(humanValue(diffPreview.status || "UNKNOWN"))}</div>
          <div class="signal-band-note">changed/compared: ${esc(String(diffPreview.changed_count ?? 0))}/${esc(String(diffPreview.compared_count ?? 0))}</div>
        </div>
      </div>
      <div class="bloodflow-strip">
        <div class="bloodflow-title">Живой кровоток IMPERIUM: event -> review -> shift -> owner consequence</div>
        <div class="bloodflow-metrics">
          <span class="bloodflow-metric active">ACTIVE ${esc(String(signalCounters.active ?? 0))}</span>
          <span class="bloodflow-metric waiting">WAIT ${esc(String(signalCounters.waiting ?? 0))}</span>
          <span class="bloodflow-metric blocked">BLOCKED ${esc(String(signalCounters.blocked ?? 0))}</span>
          <span class="bloodflow-metric proven">PROVEN ${esc(String(signalCounters.proven ?? 0))}</span>
        </div>
        <div class="bloodflow-route-grid">
          ${(signalRoutes.map((route) => `
            <div class="bloodflow-route ${badgeClass(route.status || "UNKNOWN")}">
              <div class="bloodflow-route-head">
                <span>${esc(route.title_ru || route.route_id || "route")}</span>
                <span>${esc(H(route.status || "UNKNOWN"))}</span>
              </div>
              <div class="bloodflow-route-note">${esc(H(route.from_sector || "from"))} -> ${esc(H(route.to_sector || "to"))} | hits=${esc(String(route.event_count ?? 0))}</div>
            </div>
          `).join("")) || `<div class="vision-card-subtle">Активные маршруты не зафиксированы в текущем хвосте событий.</div>`}
        </div>
        <div class="bloodflow-vessel-row">
          ${(signalVessels.map((vessel) => `<span class="bloodflow-vessel ${badgeClass(vessel.status || "UNKNOWN")}">${esc(shortText(H(vessel.title_ru || vessel.vessel_id || "vessel"), 44))}: ${esc(H(vessel.status || "UNKNOWN"))}</span>`).join("")) || `<span class="bloodflow-vessel">vessels=n/a</span>`}
        </div>
      </div>
      <div class="signal-band-footnote">Сигнальный слой ускоряет owner-чтение: сначала решение/доверие/live-контур, затем детали.</div>
    `;
  }

  if (E("visionImperialOverview")) {
    const warningPills = [];
    if (H(brain.conflict_state).toUpperCase().includes("CONFLICT")) warningPills.push("конфликт управления активен");
    if (H(controlLimits.operator_action_required).toLowerCase() === "true") warningPills.push("требуется действие владельца");
    if (ownerDecisionTriggers.length) warningPills.push(`триггеры owner-решения: ${ownerDecisionTriggers.join(", ")}`);
    if (custodesThreats.length) warningPills.push(`custodes threats: ${custodesThreats.join(", ")}`);
    if (throneBreach) warningPills.push(`throne breach: ${throneStatus}`);
    if (cleanlinessVerdict !== "CLEAN") warningPills.push(`worktree: ${cleanlinessVerdict}`);
    if (!warningPills.length) warningPills.push("критичных owner-trigger сигналов не зафиксировано");

    E("visionImperialOverview").innerHTML = `
      <div class="imperial-overview-grid">
        <div class="imperial-kpi trust" title="Главный обзор системы: dashboard не ограничен одним продуктом.">
          <div class="imperial-kpi-title">Система сейчас</div>
          <div class="imperial-kpi-value">Активных продуктов: ${esc(String(liveFactory.active_products_count ?? A(f.products_in_work).length))} | Активных департаментов: ${esc(String(liveFactory.active_departments_count ?? A(state.department_floor).length))}</div>
          <div class="imperial-kpi-note">TikTok = training-ground; контур готов к multi-project расширению без перепаковки смысла.</div>
        </div>
        <div class="imperial-kpi trust" title="Живая ось возраста системы: общий возраст, текущий режим, возраст последней стабильной точки.">
          <div class="imperial-kpi-title">Ось возраста</div>
          <div class="imperial-kpi-value">Система: ${esc(ageText(systemAgeMinutes))} | Режим: ${esc(ageText(regimeAgeMinutes))}</div>
          <div class="imperial-kpi-note">Последняя стабильная точка: ${esc(ageText(lastStableAgeMinutes))} | Обновление мозга: ${esc(ageText(controlAgeAxis.control_plane_last_refresh_age_minutes))}</div>
        </div>
        <div class="imperial-kpi ${semanticTone(semanticConstitution.trust_status || liveBrain.trust_state || brain.trust_state)}" title="Constitution/canon контроль: только repo-visible truth surfaces.">
          <div class="imperial-kpi-title">Канон и конституция</div>
          <div class="imperial-kpi-value">Вердикт: ${esc(humanValue(statusRu(semanticConstitution.overall_verdict || constitutionCore.overall_verdict || "UNKNOWN"), "вердикт не подтвержден"))} | Доверие: ${esc(humanValue(statusRu(semanticConstitution.trust_status || liveBrain.trust_state || brain.trust_state || "UNKNOWN"), "доверие не подтверждено"))}</div>
          <div class="imperial-kpi-note">Риск дрейфа: ${esc(humanValue(semanticConstitution.canon_drift_risk))} | Доктрина: ${esc(humanValue(semanticConstitution.doctrine_posture))}</div>
        </div>
        <div class="imperial-kpi warning" title="Exact/derived/gap boundary: визуал не имеет права выдавать gaps за truth.">
          <div class="imperial-kpi-title">Слои правды</div>
          <div class="imperial-kpi-value">Точные: ${exactTruthCount} | Выведенные: ${derivedTruthCount} | Пробелы: ${knownGapCount}</div>
          <div class="imperial-kpi-note">Ключевой открытый пробел: ${esc(humanValue(topSemanticGap, "пробел не зафиксирован"))}.</div>
        </div>
        <div class="imperial-kpi warning" title="Owner visibility policy: владелец видит полный обзор, рабочие ноды — future role-filtered view.">
          <div class="imperial-kpi-title">Видимость</div>
          <div class="imperial-kpi-value">${esc(humanValue(semanticSecurity.visibility_restrictions_posture, "ограничения видимости не подтверждены"))}</div>
          <div class="imperial-kpi-note">Постура суверенности: ${esc(humanValue(semanticSecurity.sovereignty_posture))} | Внешняя экспозиция: ${esc(humanValue(semanticSecurity.external_exposure_state))}</div>
        </div>
        <div class="imperial-kpi ${ownerDecisionTriggers.length ? "critical" : "warning"}" title="Owner decision escalation signals: не скрываются, выводятся явно.">
          <div class="imperial-kpi-title">Триггеры решения владельца</div>
          <div class="imperial-kpi-value">${esc(ownerDecisionTriggers.length ? ownerDecisionTriggers.join(", ") : "сейчас нет")}</div>
          <div class="imperial-kpi-note">${esc(humanValue(shortText(controlLimits.blocking_reason_detail || "", 110), "причина блокировки не зафиксирована"))}</div>
        </div>
        <div class="imperial-kpi ${semanticTone(cleanlinessVerdict)}" title="Честный статус worktree/repo без маскировки грязи.">
          <div class="imperial-kpi-title">Repo / Worktree гигиена</div>
          <div class="imperial-kpi-value">${esc(statusRu(cleanlinessVerdict))}</div>
          <div class="imperial-kpi-note">tracked_dirty=${esc(String(repoHygiene.tracked_dirty_count ?? 0))} | untracked=${esc(String(repoHygiene.untracked_count ?? 0))} | canonical=${esc(String(repoClassCanonical))} | review=${esc(String(repoClassReview))} | owner_decision=${esc(String(repoClassOwnerDecision))}</div>
        </div>
        <div class="imperial-kpi ${semanticTone(H(codeBank.status || "UNKNOWN"))}" title="Code-bank масса, концентрация и аномалии в видимой зоне мозга.">
          <div class="imperial-kpi-title">Code-bank масса</div>
          <div class="imperial-kpi-value">${esc(humanValue(H(codeBank.status || "UNKNOWN")))} | LOC(code): ${esc(String(codeLocMeaningful))} | LOC(all): ${esc(String(codeLocTotal))}</div>
          <div class="imperial-kpi-note">tracked=${esc(String(codeTrackedCount))} | untracked=${esc(String(codeUntrackedCount))} | scanned=${esc(String(codeScannedCount))} | >=3000: ${esc(String(codeThresholds.ge_3000 ?? 0))}</div>
        </div>
        <div class="imperial-kpi ${semanticTone(coverageVerdict)}" title="Покрытие Full Vision и dominance-правила источников.">
          <div class="imperial-kpi-title">Coverage / Dominance</div>
          <div class="imperial-kpi-value">${esc(coverageVerdict)} | full_claim=${esc(String(fullCoverageClaimable))}</div>
          <div class="imperial-kpi-note">missing=${esc(String(coverageMissing))} | pointer_only=${esc(String(coveragePointerOnly))} | stale_rules=${esc(String(staleDominanceCount))}</div>
        </div>
      </div>
      <div class="vision-card-subtle">Что происходит: система показывает общий operational-срез, а не один продукт.</div>
      <div class="vision-card-subtle">Почему так: owner-режим держит канон, риски и возраст системы в одном экране.</div>
      <div class="vision-card-subtle">Можно ли верить: только в пределах exact/derived/gap disclosure и source-linked surfaces.</div>
      <div class="vision-card-subtle">Что ограничивает: отсутствующие реализации и owner-trigger зоны не скрываются.</div>
      <div class="truth-pill-row">${warningPills.map((x) => `<span class="truth-pill warning">${esc(shortText(x, 80))}</span>`).join("")}</div>
    `;
  }

  if (E("visionCanonState")) {
    E("visionCanonState").innerHTML = `
      <div class="status-line"><span class="line-label">Путь:</span><span class="line-value" title="Выбранный продуктовый путь из canonical truth (owner gate B).">${esc(tik.selected_option || "UNKNOWN")}</span></div>
      <div class="status-line"><span class="line-label">Волна:</span><span class="line-value" title="Статус Wave 1 по control surfaces и owner closure sync.">${esc(tik.wave_1_status || "UNKNOWN")} (${statusRu(tik.wave_1_status)})</span></div>
      <div class="status-line"><span class="line-label">Gate D:</span><span class="line-value" title="Owner-gate boundary; completion claim разрешен только при явном owner evidence.">${esc(gates.gate_d || "UNKNOWN")}</span></div>
      <div class="status-line"><span class="line-label">Визуальная доктрина:</span><span class="line-value" title="Активный style-pack; визуал вторичен относительно truth surfaces.">${esc(O(canon.visual_doctrine).active_pack || "UNKNOWN")} (активный стиль)</span></div>
      <div class="status-line"><span class="line-label">Growth:</span><span class="line-value" title="Состояние Growth/Distribution департамента в текущем каноне.">${esc(grow.department_status || "UNKNOWN")} (seed-уровень)</span></div>
      <div class="status-line"><span class="line-label">Live layer:</span><span class="line-value" title="Степень реализации live-слоя; full realtime не заявляется без evidence.">${esc(layer.implementation_status || "UNKNOWN")} (без fake complete)</span></div>
    `;
  }

  if (E("visionOwnerBrief")) {
    E("visionOwnerBrief").innerHTML = `
      <div class="owner-brief-grid">
        <div class="owner-brief-item"><div class="owner-brief-title">Сейчас</div><div class="owner-brief-text">${esc(shortText(`Активно: ${postWaveStage.active_tranche || tr.tranche_id || "TRANCHE_UNKNOWN"} | статус: ${postWaveStage.status || "UNKNOWN"}`, 86))}</div></div>
        <div class="owner-brief-item"><div class="owner-brief-title">Зачем</div><div class="owner-brief-text">${esc(shortText(postWaveStage.focus || "bounded hardening без scope drift", 88))}</div></div>
        <div class="owner-brief-item"><div class="owner-brief-title">Следующий checkpoint</div><div class="owner-brief-text">${esc(shortCheckpoint)} | ${cp.ready}/${cp.total}</div></div>
      </div>
    `;
  }

  if (E("visionMatryoshkaCore")) {
    const ringButtons = orbitNodes.map(({ world, angle, ring, radius }, idx) => `
      <button
        type="button"
        class="matryoshka-sector-btn orbit-node ${worldTone(world.state)} ${world.id === selectedWorld.id ? "is-selected" : ""}"
        data-matryoshka-sector="${esc(world.id)}"
        style="--orbit-angle:${angle}deg; --orbit-radius:${radius}px; --orbit-order:${idx};"
        title="${esc(shortText(world.summary, 160))}">
        <span class="matryoshka-sector-icon">${esc(world.icon)}</span>
        <span class="matryoshka-sector-title">${esc(world.title)}</span>
        <span class="matryoshka-sector-state">${esc(worldStateRu(world.state))}</span>
        <span class="matryoshka-sector-brief">${esc(shortText(world.overview || world.summary, 72))}</span>
      </button>
    `).join("");
    const layerButtons = [
      { id: "overview", title: "Owner-объяснение" },
      { id: "proof", title: "Proof-слой" },
      { id: "technical", title: "Технический слой" }
    ].map((layer) => `
      <button type="button" class="matryoshka-layer-btn ${selectedLayer === layer.id ? "is-selected" : ""}" data-matryoshka-layer="${layer.id}">
        ${esc(layer.title)}
      </button>
    `).join("");
    const depthButtons = [
      { id: "orbit", title: "Уровень 1: обзор" },
      { id: "sector", title: "Уровень 2: сектор" },
      { id: "subsector", title: "Уровень 3: под-сектор" }
    ].map((depth) => `
      <button type="button" class="matryoshka-depth-btn ${selectedDepth === depth.id ? "is-selected" : ""}" data-matryoshka-depth="${depth.id}">
        ${esc(depth.title)}
      </button>
    `).join("");
    E("visionMatryoshkaCore").innerHTML = `
      <div class="matryoshka-shell">
        <div class="matryoshka-orbit-field">
          <div class="matryoshka-ring-track outer"></div>
          <div class="matryoshka-ring-track middle"></div>
          <div class="matryoshka-ring-track inner"></div>
          <div class="matryoshka-core-wrap">
            <div class="matryoshka-core-glow"></div>
            <div class="matryoshka-core-node ${worldTone(selectedWorld.state)}">
              <div class="matryoshka-core-title">Живое ядро IMPERIUM</div>
              <div class="matryoshka-core-state">${esc(worldStateRu(selectedWorld.state))} | ${esc(selectedWorld.title)}</div>
              <div class="matryoshka-core-note">${esc(shortText(flowSummary || selectedWorld.summary, 122))}</div>
              <div class="matryoshka-core-strip">
                <span class="matryoshka-core-chip">ACTIVE: ${esc(String(activeWorldCount))}</span>
                <span class="matryoshka-core-chip">BLOCKED: ${esc(String(blockedWorldCount))}</span>
                <span class="matryoshka-core-chip">PROVEN: ${esc(String(provenWorldCount))}</span>
                <span class="matryoshka-core-chip">GAPS: ${esc(String(knownGapCount))}</span>
              </div>
              <div class="matryoshka-core-lane">Сигнальный маршрут: event -> review -> decision -> consequence</div>
            </div>
          </div>
          <div class="matryoshka-ring-orbits">${ringButtons}</div>
        </div>
        <div class="matryoshka-navigation">
          <div class="matryoshka-nav-title">${esc(depthTitle)}</div>
          <div class="matryoshka-nav-row">${depthButtons}</div>
          <div class="matryoshka-nav-note">${esc(depthHint)}</div>
        </div>
      </div>
      <div class="matryoshka-drill">
        <div class="matryoshka-drill-head">
          <div class="matryoshka-drill-title">${esc(selectedWorld.title)}</div>
          <div class="matryoshka-drill-sub">${esc(selectedWorld.summary)} | Орбита ${esc(String(selectedWorldIndex + 1))}/${esc(String(matryoshkaWorlds.length))}</div>
        </div>
        <div class="matryoshka-layer-row">${layerButtons}</div>
        <div class="matryoshka-layer-body">
          <div class="matryoshka-layer-title">${esc(layerTitle)}</div>
        ${layerBody.map((line) => `<div class="matryoshka-layer-line">${esc(shortText(line, 220))}</div>`).join("")}
        </div>
        <div class="matryoshka-owner-grid">
          <div class="matryoshka-owner-card">
            <div class="matryoshka-owner-title">Что это значит сейчас</div>
            <div class="matryoshka-owner-text">${esc(ownerNowText)}</div>
          </div>
          <div class="matryoshka-owner-card">
            <div class="matryoshka-owner-title">Почему можно верить</div>
            <div class="matryoshka-owner-text">${esc(ownerTrustText)}</div>
          </div>
          <div class="matryoshka-owner-card">
            <div class="matryoshka-owner-title">Что под вопросом</div>
            <div class="matryoshka-owner-text">${esc(ownerQuestionText)}</div>
          </div>
          <div class="matryoshka-owner-card">
            <div class="matryoshka-owner-title">Следующий практичный ход</div>
            <div class="matryoshka-owner-text">${esc(ownerNextAction)}</div>
          </div>
        </div>
        <div class="matryoshka-route" title="Маршрут погружения: сектор -> под-сектор -> слой правды.">
          <span class="matryoshka-route-chip">Сектор: ${esc(selectedWorld.title)}</span>
          <span class="matryoshka-route-chip">Под-сектор: ${esc(selectedSubsector.title || "общий обзор")}</span>
          <span class="matryoshka-route-chip">Слой: ${esc(selectedLayerTitle)}</span>
          <button type="button" class="matryoshka-route-chip action" data-matryoshka-depth="orbit">Вернуться к ядру</button>
        </div>
      </div>
      <div class="vision-card-subtle">Что происходит: ядро стало операционным входом, орбиты ведут в вложенные миры без потери ориентации.</div>
      <div class="vision-card-subtle">Почему так: матрешка = внешний обзор -> сектор -> под-сектор -> proof -> техслой, с явным возвратом.</div>
    `;

    E("visionMatryoshkaCore").querySelectorAll("[data-matryoshka-sector]").forEach((node) => {
      node.addEventListener("click", () => {
        const sector = H(node.getAttribute("data-matryoshka-sector"));
        if (!worldById.has(sector)) return;
        app.fullVision.sectorFocus = sector;
        app.fullVision.subsectorFocus = 0;
        app.fullVision.depthFocus = "sector";
        renderFullVision(state, live);
      });
    });
    E("visionMatryoshkaCore").querySelectorAll("[data-matryoshka-layer]").forEach((node) => {
      node.addEventListener("click", () => {
        const layer = H(node.getAttribute("data-matryoshka-layer"));
        if (!["overview", "proof", "technical"].includes(layer)) return;
        app.fullVision.layerFocus = layer;
        renderFullVision(state, live);
      });
    });
    E("visionMatryoshkaCore").querySelectorAll("[data-matryoshka-depth]").forEach((node) => {
      node.addEventListener("click", () => {
        const depth = H(node.getAttribute("data-matryoshka-depth"));
        if (!["orbit", "sector", "subsector"].includes(depth)) return;
        app.fullVision.depthFocus = depth;
        if (depth === "orbit") app.fullVision.subsectorFocus = 0;
        if (depth === "sector" && selectedSubsectors.length === 0) app.fullVision.depthFocus = "orbit";
        if (depth === "subsector" && selectedSubsectors.length === 0) app.fullVision.depthFocus = "sector";
        renderFullVision(state, live);
      });
    });
  }

  if (E("visionSectorImmersion")) {
    const subsectors = A(selectedWorld.subsectors);
    const immersionWhy = ownerNowText;
    const immersionTrust = ownerTrustText;
    const immersionLimit = ownerLimitText;
    const immersionDepthText = selectedDepth === "subsector"
      ? "Вы внутри под-сектора. Назад: в сектор или к ядру."
      : (selectedDepth === "sector" ? "Вы на уровне сектора. Доступно углубление в под-секторы." : "Вы на орбитальном уровне. Выберите сектор для погружения.");
    E("visionSectorImmersion").innerHTML = `
      <div class="sector-immersion-head">
        <div class="sector-immersion-title">Погружение в сектор: ${esc(selectedWorld.title)}</div>
        <div class="sector-immersion-note">Сейчас: ${esc(worldStateRu(selectedWorld.state))}. ${esc(immersionDepthText)}</div>
      </div>
      <div class="sector-immersion-route-row">
        <button type="button" class="sector-immersion-route-btn" data-matryoshka-depth="orbit">К ядру и орбитам</button>
        <button type="button" class="sector-immersion-route-btn" data-matryoshka-depth="sector">К уровню сектора</button>
        <button type="button" class="sector-immersion-route-btn ${selectedDepth === "subsector" ? "is-selected" : ""}" data-matryoshka-depth="subsector">К под-сектору</button>
        <span class="sector-immersion-route-note">Маршрут: ${esc(depthTitle)} -> ${esc(selectedWorld.title)} -> ${esc(selectedSubsector.title || "общий обзор")}</span>
      </div>
      <div class="sector-immersion-grid">
        ${subsectors.map((zone, idx) => `
          <button type="button" class="sector-immersion-card ${worldTone(zone.state)} ${idx === selectedSubsectorIndex ? "is-selected" : ""}" data-matryoshka-subsector="${idx}" title="${esc(shortText(zone.note, 140))}">
            <div class="sector-immersion-card-head">
              <span>${esc(zone.title)}</span>
              <span class="label-badge ${badgeClass(zone.state)}">${esc(worldStateRu(zone.state))}</span>
            </div>
            <div class="sector-immersion-card-note">${esc(zone.note)}</div>
          </button>
        `).join("")}
      </div>
      <div class="sector-immersion-owner">
        <div class="sector-immersion-owner-block">
          <div class="sector-immersion-owner-title">Что происходит</div>
          <div class="sector-immersion-owner-text">${esc(immersionWhy)}</div>
        </div>
        <div class="sector-immersion-owner-block">
          <div class="sector-immersion-owner-title">Почему можно верить</div>
          <div class="sector-immersion-owner-text">${esc(immersionTrust)}</div>
        </div>
        <div class="sector-immersion-owner-block">
          <div class="sector-immersion-owner-title">Что ограничивает</div>
          <div class="sector-immersion-owner-text">${esc(immersionLimit)}</div>
        </div>
      </div>
      <div class="sector-deep-grid">
        ${worldDeepCards}
      </div>
      <div class="sector-immersion-proof">
        <div class="sector-immersion-proof-title">Proof маршруты</div>
        ${A(selectedWorld.proof).map((line) => `<div class="sector-immersion-proof-line">${esc(shortText(line, 190))}</div>`).join("")}
      </div>
      <details class="vision-inline-details">
        <summary>Технический drilldown по выбранному сектору</summary>
        <div class="vision-inline-body">
          subsector: ${esc(selectedSubsector.title || "overview")} (${esc(worldStateRu(selectedSubsector.state || selectedWorld.state || "UNKNOWN"))})<br>
          ${A(selectedWorld.technical).map((line) => `${esc(shortText(line, 220))}<br>`).join("")}
        </div>
      </details>
    `;
    E("visionSectorImmersion").querySelectorAll("[data-matryoshka-subsector]").forEach((node) => {
      node.addEventListener("click", () => {
        const idx = Number(node.getAttribute("data-matryoshka-subsector"));
        if (!Number.isFinite(idx)) return;
        app.fullVision.subsectorFocus = idx;
        app.fullVision.depthFocus = "subsector";
        renderFullVision(state, live);
      });
    });
    E("visionSectorImmersion").querySelectorAll("[data-matryoshka-depth]").forEach((node) => {
      node.addEventListener("click", () => {
        const depth = H(node.getAttribute("data-matryoshka-depth"));
        if (!["orbit", "sector", "subsector"].includes(depth)) return;
        app.fullVision.depthFocus = depth;
        if (depth === "orbit") app.fullVision.subsectorFocus = 0;
        renderFullVision(state, live);
      });
    });
  }

  if (E("visionProductLive")) {
    E("visionProductLive").innerHTML = `
      <div class="operation-strip">
        <span class="label-badge ${processBadge(productProcessState)}" title="Текущий процесс продукта: показывает активное состояние обработки по runtime/live truth.">${esc(productProcessState)}</span>
        <span class="operation-chip" title="Человеческое объяснение текущего process-state.">${esc(processRu(productProcessState))}</span>
        <span class="operation-chip" title="Текущая стадия продукта в pipeline.">${esc(liveProduct.current_stage || product.pipeline_stage || "этап не задан")}</span>
        <span class="operation-chip" title="Активный wave/контур продукта.">${esc(liveProduct.current_wave || wave.wave_id || "контур не задан")}</span>
      </div>
      <div class="metric-grid">
        <div class="metric-card" title="Что делает агент прямо сейчас: active operation/workset из live heartbeat.">
          <div class="metric-title">Текущая операция</div>
          <div class="metric-value">${esc(runtimeOperation)}</div>
          <div class="metric-note">${esc(shortText(heartbeat.active_workset_title || processReason, 88))}</div>
        </div>
        <div class="metric-card" title="Почему статус именно такой: последний подтвержденный milestone из live feed.">
          <div class="metric-title">Причина статуса</div>
          <div class="metric-value">${esc(shortText(runtimeLatestSummary || processReason, 84))}</div>
          <div class="metric-note">Latest event: ${esc(eventRu(latestEvt.event_type || "event"))}</div>
        </div>
        <div class="metric-card" title="Где можно доверять: SOURCE_EXACT/DERIVED разделены явно, без fake realtime claim.">
          <div class="metric-title">Граница доверия</div>
          <div class="metric-value">${esc(truthClassRu(liveRuntime.truth_class || runtimeObs.truth_class || liveProduct.truth_class || "SOURCE_EXACT"))}</div>
          <div class="metric-note">Сейчас: ${esc(liveProduct.execution_state || "n/a")} | Граница prompt-lineage: ${esc(O(semanticProduct.prompt_lineage_honesty).trusted_boundary || "UNKNOWN")}</div>
        </div>
        <div class="metric-card" title="Диагностика runtime: явная причина ошибки и сигнал восстановления.">
          <div class="metric-title">Runtime диагностика</div>
          <div class="metric-value">${esc(shortText(runtimeFailure, 68))}</div>
          <div class="metric-note">Recovery: ${esc(shortText(runtimeRecovery, 72))}</div>
        </div>
      </div>
      <div class="vision-card-subtle">Что происходит: виден живой процесс агента по событиям и текущей операции.</div>
      <div class="vision-card-subtle">Почему так: статус объясняется последним подтвержденным изменением.</div>
      <div class="vision-card-subtle">Можно ли верить: realtime слой честный — без заявления full-event-bus.</div>
      <details class="vision-inline-details">
        <summary>Технические детали продукта</summary>
        <div class="vision-inline-body">
          runtime source mode: ${esc(runtimeSourceMode)}<br>
          runtime truth class: ${esc(liveRuntime.truth_class || runtimeObs.truth_class || liveProduct.truth_class || "SOURCE_EXACT")}<br>
          active stage code: ${esc(liveProduct.current_stage || product.pipeline_stage || "unknown_stage")}<br>
          active wave code: ${esc(liveProduct.current_wave || wave.wave_id || "unknown_wave")}
        </div>
      </details>
    `;
  }

  if (E("visionCurrentOperation")) {
    E("visionCurrentOperation").innerHTML = `
      <div class="operation-strip">
        <span class="label-badge active">${esc(postWaveStage.status || tr.status || "IN_PROGRESS")}</span>
        <span class="operation-chip">${esc(postWaveStage.active_tranche || tr.tranche_id || "TRANCHE_UNKNOWN")}</span>
        <span class="operation-chip">Step: ${esc(shortText(H(liveWorkStep.step_id || "UNKNOWN_STEP"), 52))}</span>
        <span class="operation-chip">Phase: ${esc(shortText(H(liveWorkPhase.phase_id || "UNKNOWN_PHASE"), 44))}</span>
        <span class="operation-chip">${esc(runtimeOperation)}</span>
        <span class="operation-chip">Op class: ${esc(H(liveWorkOperation.operation_class || "PATCH"))}</span>
        <span class="operation-chip">${esc(liveChannelHuman)} | ${esc(liveChannel.status || "starting")}</span>
        <span class="operation-chip ${badgeClass(flowPosture)}">Flow: ${esc(flowPosture)}</span>
        <span class="operation-chip ${badgeClass(ascentStatus)}">Ascent: ${esc(ascentStatus)}</span>
        <span class="operation-chip">${esc(statusRu(heartbeat.implementation_label || "PARTIALLY_IMPLEMENTED"))}</span>
      </div>
      <div class="owner-brief-grid">
        <div class="owner-brief-item"><div class="owner-brief-title">Текущий workset</div><div class="owner-brief-text">${esc(shortText(primaryWork.work_id || "W1-TR1", 52))}: ${esc(shortText(primaryWork.title || "active tranche work", 72))}</div></div>
        <div class="owner-brief-item"><div class="owner-brief-title">Почему сейчас</div><div class="owner-brief-text">Сначала truth/reliability фундамент, потом расширение.</div></div>
        <div class="owner-brief-item"><div class="owner-brief-title">Последний proof</div><div class="owner-brief-text">${esc(latestProofText)}</div></div>
        <div class="owner-brief-item"><div class="owner-brief-title">Последний risk / blocker</div><div class="owner-brief-text">${esc(latestRiskText)}${blockerText ? ` | ${esc(blockerText)}` : ""} | recovery=${esc(shortText(runtimeRecovery, 34))}</div></div>
        <div class="owner-brief-item"><div class="owner-brief-title">Flow маршрут</div><div class="owner-brief-text">${esc(shortText(flowRouteFocus || "route_focus_not_set", 66))} | ${esc(shortText(flowSummary || "signal summary n/a", 88))}</div></div>
        <div class="owner-brief-item"><div class="owner-brief-title">Ветвь к Voice of Imperium</div><div class="owner-brief-text">Статус: ${esc(ascentStatus)} | boundary: ${esc(shortText(ascentBoundary, 62))} | target: ${esc(shortText(ascentTarget, 64))}</div></div>
        <div class="owner-brief-item"><div class="owner-brief-title">Затронутые группы</div><div class="owner-brief-text">${esc(shortText(liveWorkGroupText, 120))}</div></div>
        <div class="owner-brief-item"><div class="owner-brief-title">Последние изменения</div><div class="owner-brief-text">${esc(shortText(liveWorkRecentText, 120))}</div></div>
        <div class="owner-brief-item"><div class="owner-brief-title">Причина ожидания/блокера</div><div class="owner-brief-text">${esc(shortText(H(liveWorkBlocker.reason_ru || "active progression"), 120))}</div></div>
        <div class="owner-brief-item"><div class="owner-brief-title">Прогресс шага</div><div class="owner-brief-text">phase ${esc(String(liveWorkPhase.phase_index || 0))}/${esc(String(liveWorkPhase.phase_total || 0))} | tracked=${esc(String(liveWorkProgress.tracked_dirty_changes ?? 0))} | untracked=${esc(String(liveWorkProgress.untracked_changes ?? 0))}</div></div>
      </div>
      <details class="vision-inline-details">
        <summary>Технические коды операции</summary>
        <div class="vision-inline-body">
          runtime source mode: ${esc(runtimeSourceMode)}<br>
          heartbeat implementation: ${esc(heartbeat.implementation_label || "PARTIALLY_IMPLEMENTED")}<br>
          workset code: ${esc(primaryWork.work_id || "W1-TR1")}<br>
          tranche code: ${esc(postWaveStage.active_tranche || tr.tranche_id || "TRANCHE_UNKNOWN")}<br>
          event_flow_route_focus: ${esc(flowRouteFocus || "n/a")}<br>
          tiktok_ascent_boundary: ${esc(ascentBoundary)}<br>
          live_work_surface: ${esc(H(workVisibility.source_path || "shared_systems/factory_observation_window_v1/adapters/IMPERIUM_LIVE_WORK_VISIBILITY_SURFACE_V1.json"))}<br>
          live_stream_mode: ${esc(H(O(workVisibility.live_stream_mode).status || "PARTIALLY_IMPLEMENTED"))} | event_bus=${esc(H(O(workVisibility.live_stream_mode).event_bus_status || "NOT_YET_IMPLEMENTED"))}
        </div>
      </details>
    `;
  }

  if (E("visionBrainCore")) {
    const conflictBadge = H(brain.conflict_state || liveBrain.conflict_state || "UNKNOWN");
    const trustBadge = H(brain.trust_state || liveBrain.trust_state || "UNKNOWN");
    const constitutionRankRaw = H(constitutionCore.detected_node_rank || "UNKNOWN");
    const constitutionRankDisplay = throneAnchorState === "VALID" ? "EMPEROR" : constitutionRankRaw;
    const governanceBlockerCount = governanceBlockers.length;
    const trustBlockerCount = trustBlockers.length;
    const syncBlockerCount = syncBlockers.length;
    const repoBlockerCount = repoBlockers.length;
    const runtimeBlockerCount = runtimeBlockers.length;
    const sovereignBlockerCount = sovereignBlockers.length;
    const conflictChipClass = conflictBadge.includes("CONFLICT") ? "critical" : "trust";
    const trustChipClass = trustBadge.includes("TRUSTED") ? "trust" : "warning";
    const ownerTriggerChipClass = ownerDecisionTriggers.length ? "critical" : "trust";
    const conflictList = brainConflicts.slice(0, 4).map((c) => `
      <div class="presence-node" title="Почему есть конфликт: сравнение one_screen/repo_control/mission/task surfaces.">
        <div class="vision-card-title">${esc(c.id || "conflict")}</div>
        <div class="vision-card-note">${esc(shortText(c.reason || "conflict reason missing", 96))}</div>
        <div class="vision-card-subtle">${esc(c.severity || "warning")} | ${esc(c.truth_class || "DERIVED_CANONICAL")}</div>
      </div>
    `).join("");
    E("visionBrainCore").innerHTML = `
      <div class="operation-strip">
        <span class="label-badge ${conflictBadge.includes("CONFLICT") ? "partial" : "proven"}" title="Состояние конфликтов command/rules/mission/task.">${esc(conflictBadge)}</span>
        <span class="label-badge ${trustBadge.includes("TRUSTED") ? "proven" : "partial"}" title="Итог trust-state управляющего ядра на базе repo-visible surfaces.">${esc(trustBadge)}</span>
        <span class="operation-chip ${conflictChipClass}" title="Вердикт one_screen status как оперативный контрольный срез.">Срез контроля: ${esc(oneScreenBrain.trust_verdict || "UNKNOWN")}</span>
        <span class="operation-chip ${trustChipClass}" title="Constitution status как базовый канонический контрольный слой.">Конституция: ${esc(constitutionCore.overall_verdict || "UNKNOWN")}</span>
        <span class="operation-chip ${ownerTriggerChipClass}" title="Возраст контрольного среза управляющего ядра.">Возраст среза: ${esc(ageText(controlAgeAxis.control_plane_last_refresh_age_minutes))}</span>
      </div>
      <div class="metric-grid">
        <div class="metric-card" title="Состояние миссии и её консистентность.">
          <div class="metric-title">Согласованность миссии</div>
          <div class="metric-value">${esc(statusRu(missionConsistency.verdict || "UNKNOWN"))}</div>
          <div class="metric-note">Возраст: ${esc(ageText(missionConsistency.age_minutes))}</div>
        </div>
        <div class="metric-card" title="Состояние task-program слоя и его согласованность.">
          <div class="metric-title">Согласованность task-program</div>
          <div class="metric-value">${esc(statusRu(taskConsistency.verdict || "UNKNOWN"))}</div>
          <div class="metric-note">Возраст: ${esc(ageText(taskConsistency.age_minutes))}</div>
        </div>
        <div class="metric-card" title="Состояние command surface (операторские команды/политики).">
          <div class="metric-title">Командная поверхность</div>
          <div class="metric-value">${esc(statusRu(commandSurface.latest_execution_verdict || "UNKNOWN"))}</div>
          <div class="metric-note">Режим: ${esc(commandSurface.latest_execution_mode || "UNKNOWN")} | Скрипт: ${esc(commandSurface.script_exists ? "есть" : "нет")}</div>
        </div>
        <div class="metric-card" title="Constitution и governance acceptance ограничения.">
          <div class="metric-title">Ограничения конституции</div>
          <div class="metric-value">${esc(statusRu(constitutionCore.governance_acceptance || "UNKNOWN"))} | ${esc(statusRu(constitutionCore.trust_status || "UNKNOWN"))}</div>
          <div class="metric-note">governance=${esc(String(governanceBlockerCount))} | trust=${esc(String(trustBlockerCount))} | sync=${esc(String(syncBlockerCount))}</div>
        </div>
        <div class="metric-card" title="Суверенная authority-цепочка отделена от governance/trust/sync blockers.">
          <div class="metric-title">Суверенный контур</div>
          <div class="metric-value">${esc(statusRu(emperorProof))} | ${esc(statusRu(throneAnchorState))}</div>
          <div class="metric-note">rank=${esc(sovereignDisplayRank)} | mode=${esc(sovereignDisplayMode)} | sovereign_blockers=${esc(String(sovereignBlockerCount))}</div>
        </div>
        <div class="metric-card" title="Эскалационные триггеры owner-решений.">
          <div class="metric-title">Эскалация владельцу</div>
          <div class="metric-value">${esc(ownerDecisionTriggers.length ? `активно: ${ownerDecisionTriggers.length}` : "триггеров нет")}</div>
          <div class="metric-note">${esc(shortText(controlLimits.blocking_reason_category || "no_block_category", 64))}</div>
        </div>
        <div class="metric-card" title="Честный статус git/worktree без авто-очистки и фальшивого green.">
          <div class="metric-title">Гигиена репозитория</div>
          <div class="metric-value">${esc(statusRu(cleanlinessVerdict))}</div>
          <div class="metric-note">tracked=${esc(String(repoHygiene.tracked_dirty_count ?? 0))} | untracked=${esc(String(repoHygiene.untracked_count ?? 0))} | blockers=${esc(String(repoBlockerCount))} | branch=${esc(H(repoHygiene.branch || "UNKNOWN"))}</div>
        </div>
        <div class="metric-card" title="Кодовая масса и концентрация в критичных монолитах.">
          <div class="metric-title">Code-bank / монолиты</div>
          <div class="metric-value">${esc(H(codeBank.status || "UNKNOWN"))} | LOC(code) ${esc(String(codeLocMeaningful))}</div>
          <div class="metric-note">tracked=${esc(String(codeTrackedCount))} | untracked=${esc(String(codeUntrackedCount))} | top=${esc(shortText(topMonoliths.map((x) => `${x.path}:${x.loc}`).join("; ") || "n/a", 88))}</div>
        </div>
        <div class="metric-card" title="Покрытие dashboard и dominance-правила свежести.">
          <div class="metric-title">Coverage / dominance</div>
          <div class="metric-value">${esc(coverageVerdict)} | stale_rules=${esc(String(staleDominanceCount))}</div>
          <div class="metric-note">rows=${esc(String(coverageRows.length))} | missing=${esc(String(coverageMissing))} | pointer_only=${esc(String(coveragePointerOnly))}</div>
        </div>
        <div class="metric-card" title="Custodes: верхний guardian-фильтр foundation/throne/mental integrity.">
          <div class="metric-title">Custodes lock-постура</div>
          <div class="metric-value">${esc(custodesVigilance)} | ${esc(custodesLockMode)}</div>
          <div class="metric-note">${esc(custodesThreats.length ? shortText(custodesThreats.join(", "), 84) : "угроз foundation-grade нет")} | throne=${esc(throneStatus)}</div>
        </div>
        <div class="metric-card" title="Adeptus Mechanicus: мощность исполнения и архитектурные пределы.">
          <div class="metric-title">Mechanicus readiness</div>
          <div class="metric-value">${esc(String(mechanicusReadiness))} | ${esc(mechanicusLargeStep)}</div>
          <div class="metric-note">${esc(shortText(mechanicusStopReasons.join("; ") || "stop reasons не активны", 92))}</div>
        </div>
        <div class="metric-card" title="Administratum: контрактная дисциплина и stop-and-ask.">
          <div class="metric-title">Administratum gate</div>
          <div class="metric-value">${esc(administratumGateState)} | missing=${esc(String(administratumMissingFields.length))}</div>
          <div class="metric-note">contract=${esc(shortText(missionContractId, 36))} | owner_ack=${esc(String(Boolean(administratum.owner_ack_required)))}</div>
        </div>
        <div class="metric-card" title="Force doctrine: реальная емкость и bottlenecks текущего шага.">
          <div class="metric-title">Force readiness</div>
          <div class="metric-value">${esc(forceReadiness)} | bottlenecks=${esc(String(forceBottlenecks.length))}</div>
          <div class="metric-note">${esc(shortText(forceBottlenecks.join("; ") || "bottlenecks не активны", 96))}</div>
        </div>
        <div class="metric-card" title="Control gates: состояние трон/доминирование/coverage/runtime gate-слоя.">
          <div class="metric-title">Control gate summary</div>
          <div class="metric-value">${esc(controlGateSummary)} | rows=${esc(String(controlGateRows.length))}</div>
          <div class="metric-note">throne=${esc(H(brainV2Layer1.throne_anchor_state || throneAnchorState))} | runtime_blockers=${esc(String(runtimeBlockerCount))} | force=${esc(H(brainV2Layer4.force_readiness_band || forceReadiness))}</div>
        </div>
        <div class="metric-card" title="Truth Spine как корневой конвергентный источник для dashboard/bundle truth.">
          <div class="metric-title">Truth spine</div>
          <div class="metric-value">${esc(truthSpineStatus)} | sync=${esc(String(truthSyncPercentage))}%</div>
          <div class="metric-note">active_line=${esc(shortText(H(O(truthSpine.authoritative_current_point).active_line || "n/a"), 72))}</div>
        </div>
        <div class="metric-card" title="Честность отображения dashboard и транспортного bundle контура.">
          <div class="metric-title">Dashboard / bundle truth</div>
          <div class="metric-value">${esc(dashboardTruthStatus)} | bundle=${esc(bundleTruthStatus)}</div>
          <div class="metric-note">worktree_gate=${esc(worktreePurityStatus)} | cleanliness=${esc(worktreeCleanliness)}</div>
        </div>
        <div class="metric-card" title="Address Lattice: канонический адресный слой для full-system slice/review/reconstruction.">
          <div class="metric-title">Address lattice</div>
          <div class="metric-value">${esc(addressLatticeStatus)}</div>
          <div class="metric-note">addresses=${esc(String(Object.keys(O(addressLattice.addresses)).length))}</div>
        </div>
        <div class="metric-card" title="Anti-lie foundation: lie-классы должны быть обнаружены, заблокированы и отправлены в remediation-loop.">
          <div class="metric-title">Anti-lie foundation</div>
          <div class="metric-value">${esc(antiLieStatus)} | critical=${esc(String(antiLieCritical))}</div>
          <div class="metric-note">detected=${esc(String(Number(antiLieModel.active_total_count ?? antiLieCritical)))} | mode=${esc(H(antiLieModel.mode || "UNKNOWN"))}</div>
        </div>
        <div class="metric-card" title="Live truth support loop: удержание truthful состояния после PASS и явная фиксация дрейфа.">
          <div class="metric-title">Truth support loop</div>
          <div class="metric-value">${esc(truthLoopStatus)} | drift=${esc(String(truthLoopDrift))}</div>
          <div class="metric-note">profile=${esc(H(truthSupportLoop.loop_profile || "EVENT_OR_INTERVAL"))} | interval=${esc(String(Number(truthSupportLoop.check_interval_seconds ?? 0)))}s</div>
        </div>
      </div>
      <div class="vision-card-subtle">Что происходит: sovereign proof теперь показан отдельно от governance/trust/sync, без ложного смешивания.</div>
      <div class="vision-card-subtle">Почему так: валидный трон не должен визуально деградировать из-за отдельных governance/repo проблем.</div>
      <div class="vision-card-subtle">Что ограничивает: repo/sync/trust/coverage blockers остаются явными и не скрываются.</div>
      <details class="vision-inline-details">
        <summary>Технические коды мозга управления</summary>
        <div class="vision-inline-body">
          one_screen trust: ${esc(oneScreenBrain.trust_verdict || "UNKNOWN")}<br>
          repo_control health: ${esc(repoControlBrain.repo_health || "UNKNOWN")}<br>
          emperor_proof: ${esc(emperorProof)}<br>
          throne_anchor_state: ${esc(throneAnchorState)}<br>
          sovereign_display_rank: ${esc(sovereignDisplayRank)}<br>
          sovereign_display_mode: ${esc(sovereignDisplayMode)}<br>
          throne authority anchor: ${pv(throneAnchorPath)}<br>
          constitution_rank_raw_non_authority: ${esc(constitutionRankRaw)}<br>
          constitution_rank_display: ${esc(constitutionRankDisplay)}<br>
          blocker_counts: governance=${esc(String(governanceBlockerCount))}, trust=${esc(String(trustBlockerCount))}, sync=${esc(String(syncBlockerCount))}, repo=${esc(String(repoBlockerCount))}, runtime=${esc(String(runtimeBlockerCount))}, sovereign=${esc(String(sovereignBlockerCount))}<br>
          command script exists: ${esc(String(Boolean(commandSurface.script_exists)))}<br>
          code_bank_surface: ${pv(H(codeBank.source_path || "shared_systems/factory_observation_window_v1/adapters/IMPERIUM_CODE_BANK_STATE_SURFACE_V1.json"))}<br>
          coverage_surface: ${pv(H(coverage.source_path || "shared_systems/factory_observation_window_v1/adapters/IMPERIUM_DASHBOARD_COVERAGE_SURFACE_V1.json"))}<br>
          dominance_surface: ${pv(H(dominance.source_path || "shared_systems/factory_observation_window_v1/adapters/IMPERIUM_TRUTH_DOMINANCE_SURFACE_V1.json"))}<br>
          custodes_surface: ${pv(H(custodes.source_path || "shared_systems/factory_observation_window_v1/adapters/IMPERIUM_ADEPTUS_CUSTODES_STATE_SURFACE_V1.json"))}<br>
          mechanicus_surface: ${pv(H(mechanicus.source_path || "shared_systems/factory_observation_window_v1/adapters/IMPERIUM_ADEPTUS_MECHANICUS_STATE_SURFACE_V1.json"))}<br>
          administratum_surface: ${pv(H(administratum.source_path || "shared_systems/factory_observation_window_v1/adapters/IMPERIUM_ADMINISTRATUM_STATE_SURFACE_V1.json"))}<br>
          force_surface: ${pv(H(forceDoctrine.source_path || "shared_systems/factory_observation_window_v1/adapters/IMPERIUM_FORCE_DOCTRINE_SURFACE_V1.json"))}<br>
          palace_surface: ${pv(H(palaceArchive.source_path || "shared_systems/factory_observation_window_v1/adapters/IMPERIUM_PALACE_AND_ARCHIVE_STATE_SURFACE_V1.json"))}<br>
          control_gates_surface: ${pv(H(controlGates.source_path || "shared_systems/factory_observation_window_v1/adapters/IMPERIUM_CONTROL_GATES_SURFACE_V1.json"))}<br>
          truth_spine: ${esc(truthSpineStatus)} (sync=${esc(String(truthSyncPercentage))}%) | source=${pv(H(truthSpine.source_path || "shared_systems/factory_observation_window_v1/adapters/IMPERIUM_TRUTH_SPINE_STATE_SURFACE_V1.json"))}<br>
          dashboard_truth_engine: ${esc(dashboardTruthStatus)} | source=${pv(H(dashboardTruthEngine.source_path || "shared_systems/factory_observation_window_v1/adapters/IMPERIUM_DASHBOARD_TRUTH_ENGINE_SURFACE_V1.json"))}<br>
          bundle_truth_chamber: ${esc(bundleTruthStatus)} | source=${pv(H(bundleTruthChamber.source_path || "shared_systems/factory_observation_window_v1/adapters/IMPERIUM_BUNDLE_TRUTH_CHAMBER_SURFACE_V1.json"))}<br>
          worktree_purity_gate: ${esc(worktreePurityStatus)} | cleanliness=${esc(worktreeCleanliness)} | source=${pv(H(worktreePurityGate.source_path || "shared_systems/factory_observation_window_v1/adapters/IMPERIUM_WORKTREE_PURITY_GATE_SURFACE_V1.json"))}<br>
          address_lattice: ${esc(addressLatticeStatus)} | source=${pv(H(addressLattice.source_path || "shared_systems/factory_observation_window_v1/adapters/IMPERIUM_ADDRESS_LATTICE_SURFACE_V1.json"))}<br>
          anti_lie_model: ${esc(antiLieStatus)} | source=${pv(H(antiLieModel.source_path || "shared_systems/factory_observation_window_v1/adapters/IMPERIUM_ANTI_LIE_MODEL_SURFACE_V1.json"))}<br>
          live_truth_support_loop: ${esc(truthLoopStatus)} | source=${pv(H(truthSupportLoop.source_path || "shared_systems/factory_observation_window_v1/adapters/IMPERIUM_LIVE_TRUTH_SUPPORT_LOOP_SURFACE_V1.json"))}
        </div>
      </details>
      ${conflictList || `<div class="vision-card-subtle">Конфликтов по доступным brain surfaces не обнаружено.</div>`}
    `;
  }

  if (E("visionEvolutionChannel")) {
    const stageMap = A(evolution.stage_map || evolution.system_stage_map);
    const candidates = A(evolution.insight_candidates);
    const ownerQueue = A(evolution.owner_approval_queue);
    const gains = A(evolution.accepted_transfer_gains);
    const evoMode = H(evolution.current_mode || O(evolutionState.channel_mode).default || "UNKNOWN");
    const evoResource = H(evolution.resource_profile || O(evolutionState.channel_mode).resource_profile || "UNKNOWN");
    const evoHealth = H(evolution.health || "UNKNOWN");
    const topStage = O(stageMap.find((x) => String(x.system_id || "").toLowerCase() === "tiktok_agent") || stageMap[0]);
    E("visionEvolutionChannel").innerHTML = `
      <div class="operation-strip">
        <span class="label-badge ${badgeClass(evoHealth)}">Состояние: ${esc(statusRu(evoHealth))}</span>
        <span class="operation-chip">Режим: ${esc(evoMode)}</span>
        <span class="operation-chip">Профиль ресурса: ${esc(shortText(evoResource, 44))}</span>
        <span class="operation-chip">Фронтов: ${esc(String(stageMap.length))}</span>
        <span class="operation-chip">Кандидатов: ${esc(String(candidates.length))}</span>
        <span class="operation-chip">Owner queue: ${esc(String(ownerQueue.length))}</span>
      </div>
      <div class="cognition-grid">
        <div class="cognition-node trust" title="Куда эволюция ведет систему сейчас.">
          <div class="cognition-node-title">Текущий вектор</div>
          <div class="cognition-node-value">${esc(shortText(`${topStage.display_name || topStage.system_id || "line"}: ${topStage.current_stage || "UNKNOWN"} -> ${topStage.target_stage || "UNKNOWN"}`, 118))}</div>
          <div class="cognition-node-note">Текущий tranche: ${esc(postWaveStage.active_tranche || "UNKNOWN")}</div>
        </div>
        <div class="cognition-node warning" title="Кандидаты улучшений не входят в канон автоматически.">
          <div class="cognition-node-title">Кандидаты улучшений</div>
          <div class="cognition-node-value">${esc(candidates.length ? shortText(candidates.map((x) => `${x.candidate_id || "cand"}:${x.status || "UNKNOWN"}`).join(" | "), 108) : "новых кандидатов нет")}</div>
          <div class="cognition-node-note">Owner approval обязателен для canon-impacting продвижения.</div>
        </div>
        <div class="cognition-node trust" title="Уже принятые переносимые усиления в системе.">
          <div class="cognition-node-title">Принятые transfer gains</div>
          <div class="cognition-node-value">${esc(String(gains.length))}</div>
          <div class="cognition-node-note">${esc(gains.length ? shortText(gains.map((x) => x.title || x.gain_id || "gain").join("; "), 110) : "пока нет принятых gain-линий")}</div>
        </div>
        <div class="cognition-node warning" title="Связь эволюции с производством: инсайты должны идти из реальных product/factory сигналов.">
          <div class="cognition-node-title">Связь с Фабрикой</div>
          <div class="cognition-node-value">${esc(shortText(`factory_flow=${H(O(factoryAssembly.tiktok_live_flow_markers).active_now || "n/a")} | posture=${H(eventFlow.flow_posture || "WAIT")}`, 106))}</div>
          <div class="cognition-node-note">owner-queue: ${esc(String(ownerQueue.length))} | routes: ${esc(String(A(eventFlow.changed_sector_routes).length))}</div>
        </div>
      </div>
      <div class="vision-card-subtle">Что происходит: канал эволюции читает только канонические surfaces и ведет bounded улучшения.</div>
      <div class="vision-card-subtle">Почему так: quiet heartbeat по умолчанию, deep review только по явной авторизации.</div>
      <details class="vision-inline-details">
        <summary>Технические детали Evolution</summary>
        <div class="vision-inline-body">
          surface_id: ${esc(evolution.surface_id || evolutionState.surface_id || "UNKNOWN")}<br>
          truth_class: ${esc(evolution.truth_class || evolutionState.truth_class || "DERIVED_CANONICAL")}<br>
          source_path: ${pv(evolution.source_path || "shared_systems/factory_observation_window_v1/adapters/IMPERIUM_EVOLUTION_STATE_SURFACE_V1.json")}
        </div>
      </details>
    `;
  }

  if (E("visionInquisitionCore")) {
    const alerts = A(inquisition.active_heresy_alerts);
    const classes = A(inquisition.heresy_classes);
    const exterminatusCandidates = A(inquisition.exterminatus_candidates);
    const unresolved = Number(inquisition.unresolved_review_cases_count ?? alerts.length);
    const driftLevel = H(inquisition.drift_level || "UNKNOWN");
    const integrity = H(inquisition.canon_integrity || "UNKNOWN");
    const topAlert = O(alerts[0]);
    E("visionInquisitionCore").innerHTML = `
      <div class="operation-strip">
        <span class="label-badge ${badgeClass(integrity)}">Целостность: ${esc(statusRu(integrity))}</span>
        <span class="operation-chip inquisition">Drift: ${esc(statusRu(driftLevel))}</span>
        <span class="operation-chip inquisition">Алерты: ${esc(String(alerts.length))}</span>
        <span class="operation-chip inquisition">Неразрешено: ${esc(String(unresolved))}</span>
        <span class="operation-chip inquisition">Классов ереси: ${esc(String(classes.length))}</span>
      </div>
      <div class="cognition-grid">
        <div class="cognition-node critical" title="Активный anti-heresy/cleanup/remediation канал, отделенный от Custodes.">
          <div class="cognition-node-title">Активный кейс</div>
          <div class="cognition-node-value">${esc(topAlert.case_id || "open_case_not_found")}</div>
          <div class="cognition-node-note">${esc(shortText(topAlert.summary || "активные кейсы не зафиксированы", 118))}</div>
        </div>
        <div class="cognition-node warning" title="Default ladder: detect/classify/report -> pre-authorized fix -> severe cases by owner policy.">
          <div class="cognition-node-title">Режим обработки</div>
          <div class="cognition-node-value">detect/classify + holding + bounded remediation</div>
          <div class="cognition-node-note">Exterminatus кандидаты: ${esc(String(exterminatusCandidates.length))} (proposal-only)</div>
        </div>
        <div class="cognition-node trust" title="Последние проверенные сектора инквизиционного контроля.">
          <div class="cognition-node-title">Последние проверенные сектора</div>
          <div class="cognition-node-value">${esc(shortText(A(O(inquisition.current_integrity_state).last_verified_sectors || inquisition.last_verified_sectors).join(", ") || "n/a", 110))}</div>
          <div class="cognition-node-note">owner-bypass запрещен, авто-экстерминатус запрещен.</div>
        </div>
        <div class="cognition-node warning" title="Инквизиция связывает кейсы с каноническими surface paths и factory drift сигналами.">
          <div class="cognition-node-title">Связь с контуром Фабрики</div>
          <div class="cognition-node-value">${esc(shortText(`factory_blocked=${H(O(factoryAssembly.tiktok_live_flow_markers).blocked_by || "none")} | contradictions=${String(openCtr.length)}`, 110))}</div>
          <div class="cognition-node-note">event routes: ${esc(String(A(eventFlow.changed_sector_routes).length))} | owner review queue: ${esc(String(cp.total - cp.ready))}</div>
        </div>
      </div>
      <div class="vision-card-subtle">Что происходит: Инквизиция выполняет активный anti-heresy/cleanup/remediation контур.</div>
      <div class="vision-card-subtle">Можно ли верить: да, потому что severe actions не идут без owner policy, а кейсы не удаляются автоматически.</div>
      <details class="vision-inline-details">
        <summary>Технические детали Inquisition</summary>
        <div class="vision-inline-body">
          surface_id: ${esc(inquisition.surface_id || inquisitionState.surface_id || "UNKNOWN")}<br>
          mode: ${esc(inquisition.current_mode || O(inquisitionState.channel_mode).default || "UNKNOWN")}<br>
          source_path: ${pv(inquisition.source_path || "shared_systems/factory_observation_window_v1/adapters/IMPERIUM_INQUISITION_STATE_SURFACE_V1.json")}
        </div>
      </details>
    `;
  }

  if (E("visionCustodesCore")) {
    const guardianScope = A(custodes.guardian_scope);
    const threatList = custodesThreats.length ? custodesThreats : ["foundation threats not detected"];
    const lockModes = A(O(custodes.foundation_lock_policy).escalation_modes);
    const storageIntegrity = H(storageHealth.integrity_state || storageHealth.storage_integrity || "UNKNOWN");
    E("visionCustodesCore").innerHTML = `
      <div class="operation-strip">
        <span class="label-badge ${badgeClass(custodesVigilance)}">Vigilance: ${esc(statusRu(custodesVigilance))}</span>
        <span class="operation-chip">Lock mode: ${esc(custodesLockMode)}</span>
        <span class="operation-chip">Threats: ${esc(String(custodesThreats.length))}</span>
        <span class="operation-chip">Throne authority: ${esc(throneStatus)}</span>
        <span class="operation-chip">Owner ACK: ${esc(String(Boolean(custodes.owner_ack_required)))}</span>
        <span class="operation-chip">Storage integrity: ${esc(storageIntegrity)}</span>
      </div>
      <div class="cognition-grid">
        <div class="cognition-node trust" title="Custodes охраняет фундамент и Трон, а не занимается рутинной уборкой.">
          <div class="cognition-node-title">Роль Custodes</div>
          <div class="cognition-node-value">${esc(H(custodes.role || "FOUNDATION_AND_THRONE_GUARDIAN"))}</div>
          <div class="cognition-node-note">${esc(shortText(H(O(custodes.character_profile).default_posture || "QUIET_AND_HEAVY"), 106))}</div>
        </div>
        <div class="cognition-node ${custodesThreats.length ? "critical" : "trust"}" title="Foundation-grade угрозы выводятся прямо и не маскируются стилем.">
          <div class="cognition-node-title">Активные сигналы угроз</div>
          <div class="cognition-node-value">${esc(shortText(threatList.join("; "), 114))}</div>
          <div class="cognition-node-note">cleanliness=${esc(cleanlinessVerdict)} | coverage=${esc(coverageVerdict)} | stale_rules=${esc(String(staleDominanceCount))}</div>
        </div>
        <div class="cognition-node warning" title="Foundation lock policy: attestation / recommendation / assertion.">
          <div class="cognition-node-title">Lock policy</div>
          <div class="cognition-node-value">${esc(shortText(lockModes.join(" -> ") || "ATTESTATION", 108))}</div>
          <div class="cognition-node-note">default=${esc(H(O(custodes.foundation_lock_policy).default_mode || "ATTESTATION"))}</div>
        </div>
        <div class="cognition-node trust" title="Сфера охраны Custodes по канону.">
          <div class="cognition-node-title">Контур охраны</div>
          <div class="cognition-node-value">${esc(shortText(guardianScope.join(", ") || "scope n/a", 114))}</div>
          <div class="cognition-node-note">throne_authority=${esc(throneStatus)} | discoverability=${esc(H(goldenThrone.discoverability_status || "UNKNOWN"))} | storage=${esc(storagePosture)}</div>
        </div>
      </div>
      <div class="vision-card-subtle">Что происходит: Custodes отделен от Inquisition и держит верхний guardian-контур канона.</div>
      <div class="vision-card-subtle">Можно ли верить: lock-моды и причины угроз видны явно, без auto-деструкции и без owner-bypass.</div>
      <details class="vision-inline-details">
        <summary>Технические детали Custodes</summary>
        <div class="vision-inline-body">
          surface_id: ${esc(custodes.surface_id || custodesState.surface_id || "UNKNOWN")}<br>
          source_path: ${pv(custodes.source_path || "shared_systems/factory_observation_window_v1/adapters/IMPERIUM_ADEPTUS_CUSTODES_STATE_SURFACE_V1.json")}<br>
          throne_anchor_path: ${pv(throneAnchorPath)}<br>
          throne_breach: ${esc(String(throneBreach))}<br>
          guardian_scope_count: ${esc(String(guardianScope.length))}<br>
          threat_reasons: ${esc(threatList.join(", "))}
        </div>
      </details>
    `;
  }

  if (E("visionMechanicusCore")) {
    E("visionMechanicusCore").innerHTML = `
      <div class="operation-strip">
        <span class="label-badge ${badgeClass(mechanicusLargeStep)}">Large step: ${esc(mechanicusLargeStep)}</span>
        <span class="operation-chip">Readiness: ${esc(String(mechanicusReadiness))}</span>
        <span class="operation-chip">Code-bank: ${esc(H(mechanicus.code_bank_status || codeSummary.status_classification || "UNKNOWN"))}</span>
        <span class="operation-chip">Pressure: ${esc(String(codePressureIndex))}</span>
        <span class="operation-chip">Hint: ${esc(codeLargeStepHint)}</span>
        <span class="operation-chip">Repo hygiene: ${esc(H(mechanicus.repo_hygiene_verdict || cleanlinessVerdict))}</span>
      </div>
      <div class="cognition-grid">
        <div class="cognition-node trust">
          <div class="cognition-node-title">Сердце исполнения</div>
          <div class="cognition-node-value">${esc(H(mechanicus.role || "HEART_OF_CODE_ARCHITECTURE_EXECUTION_CAPACITY"))}</div>
          <div class="cognition-node-note">CPU=${esc(String(machineCpu))} | RAM=${esc(String(machineMemoryGb ?? "n/a"))}GB</div>
        </div>
        <div class="cognition-node ${mechanicusStopReasons.length ? "critical" : "trust"}">
          <div class="cognition-node-title">Stop reasons</div>
          <div class="cognition-node-value">${esc(shortText(mechanicusStopReasons.join("; ") || "не активны", 110))}</div>
          <div class="cognition-node-note">bottleneck=${esc(H(mechanicus.bottleneck || "none"))} | ge1200=${esc(String(codeThresholds.ge_1200 ?? 0))} | ge3000=${esc(String(codeThresholds.ge_3000 ?? 0))}</div>
        </div>
        <div class="cognition-node warning">
          <div class="cognition-node-title">Органическая сила</div>
          <div class="cognition-node-value">rows=${esc(String(organStrengthRows.length))}</div>
          <div class="cognition-node-note">${esc(shortText(forceBottlenecks.join("; ") || "bottlenecks не активны", 104))}</div>
        </div>
      </div>
      <details class="vision-inline-details">
        <summary>Технические детали Mechanicus</summary>
        <div class="vision-inline-body">
          source_path: ${pv(H(mechanicus.source_path || "shared_systems/factory_observation_window_v1/adapters/IMPERIUM_ADEPTUS_MECHANICUS_STATE_SURFACE_V1.json"))}<br>
          machine_manifest: ${pv(H(forceDoctrine.machine_capability_manifest_path || "runtime/imperium_force/IMPERIUM_MACHINE_CAPABILITY_MANIFEST_V1.json"))}<br>
          organ_strength: ${pv(H(forceDoctrine.organ_strength_surface_path || "runtime/imperium_force/IMPERIUM_ORGAN_STRENGTH_SURFACE_V1.json"))}
        </div>
      </details>
    `;
  }

  if (E("visionAdministratumCore")) {
    E("visionAdministratumCore").innerHTML = `
      <div class="operation-strip">
        <span class="label-badge ${badgeClass(administratumGateState)}">Gate: ${esc(administratumGateState)}</span>
        <span class="operation-chip">Contract: ${esc(shortText(missionContractId, 40))}</span>
        <span class="operation-chip">Unknowns: ${esc(String(administratum.unknowns_count ?? 0))}</span>
        <span class="operation-chip">Assumptions: ${esc(String(administratum.assumptions_count ?? 0))}</span>
      </div>
      <div class="cognition-grid">
        <div class="cognition-node trust">
          <div class="cognition-node-title">Роль Administratum</div>
          <div class="cognition-node-value">${esc(H(administratum.role || "OWNER_INTENT_TO_EXECUTION_CONTRACT_NORMALIZATION"))}</div>
          <div class="cognition-node-note">owner intent -> strict mission contract</div>
        </div>
        <div class="cognition-node ${administratumMissingFields.length ? "critical" : "trust"}">
          <div class="cognition-node-title">Обязательные поля</div>
          <div class="cognition-node-value">${esc(administratumMissingFields.length ? administratumMissingFields.join(", ") : "все обязательные поля есть")}</div>
          <div class="cognition-node-note">stop_and_ask=${esc(administratumGateState === "RED_BLOCK" ? "ACTIVE" : "OFF")}</div>
        </div>
        <div class="cognition-node warning">
          <div class="cognition-node-title">Эскалация</div>
          <div class="cognition-node-value">${esc(shortText(H(administratum.escalation_rule || "owner escalation policy"), 108))}</div>
          <div class="cognition-node-note">owner_ack_required=${esc(String(Boolean(administratum.owner_ack_required)))}</div>
        </div>
      </div>
      <details class="vision-inline-details">
        <summary>Технические детали Administratum</summary>
        <div class="vision-inline-body">
          source_path: ${pv(H(administratum.source_path || "shared_systems/factory_observation_window_v1/adapters/IMPERIUM_ADMINISTRATUM_STATE_SURFACE_V1.json"))}<br>
          contract_path: ${pv(H(administratum.active_contract_path || "runtime/administratum/IMPERIUM_ACTIVE_MISSION_CONTRACT_V1.json"))}<br>
          stop_triggers_count: ${esc(String(administratum.stop_triggers_count ?? 0))}
        </div>
      </details>
    `;
  }

  if (E("visionForceDoctrine")) {
    E("visionForceDoctrine").innerHTML = `
      <div class="operation-strip">
        <span class="label-badge ${badgeClass(forceReadiness)}">Force: ${esc(forceReadiness)}</span>
        <span class="operation-chip">Organ rows: ${esc(String(forceDoctrine.organ_strength_count ?? organStrengthRows.length))}</span>
        <span class="operation-chip">Contract gate: ${esc(H(forceDoctrine.contract_gate_state || administratumGateState))}</span>
        <span class="operation-chip">Mechanicus step: ${esc(H(forceDoctrine.mechanicus_large_step_readiness || mechanicusLargeStep))}</span>
      </div>
      <div class="vision-card-subtle">Что происходит: force-слой показывает реальную емкость, а не декоративную уверенность.</div>
      <div class="vision-card-subtle">Ограничение: bottlenecks остаются видимыми и не скрываются ради PASS.</div>
      <div class="metric-grid">
        <div class="metric-card"><div class="metric-title">Compute</div><div class="metric-value">CPU ${esc(String(machineCpu))}</div><div class="metric-note">RAM ${esc(String(machineMemoryGb ?? "n/a"))} GB</div></div>
        <div class="metric-card"><div class="metric-title">Validation</div><div class="metric-value">${esc(H(O(machineCapability.validation_power).coverage_verdict || coverageVerdict))}</div><div class="metric-note">stale_rules=${esc(String(O(machineCapability.validation_power).stale_dominance_rules_count ?? staleDominanceCount))}</div></div>
        <div class="metric-card"><div class="metric-title">Coordination</div><div class="metric-value">${esc(H(O(machineCapability.coordination_power).node_era_deployment_status || "NOT_YET_IMPLEMENTED"))}</div><div class="metric-note">capsule_ready=${esc(String(Boolean(O(machineCapability.coordination_power).capsule_ready)))}</div></div>
      </div>
      <details class="vision-inline-details">
        <summary>Технические детали Force Doctrine</summary>
        <div class="vision-inline-body">
          source_path: ${pv(H(forceDoctrine.source_path || "shared_systems/factory_observation_window_v1/adapters/IMPERIUM_FORCE_DOCTRINE_SURFACE_V1.json"))}<br>
          machine_manifest: ${pv(H(forceDoctrine.machine_capability_manifest_path || "runtime/imperium_force/IMPERIUM_MACHINE_CAPABILITY_MANIFEST_V1.json"))}<br>
          organ_strength: ${pv(H(forceDoctrine.organ_strength_surface_path || "runtime/imperium_force/IMPERIUM_ORGAN_STRENGTH_SURFACE_V1.json"))}<br>
          bottlenecks: ${esc(shortText(forceBottlenecks.join("; ") || "none", 120))}
        </div>
      </details>
    `;
  }

  if (E("visionPalaceArchive")) {
    E("visionPalaceArchive").innerHTML = `
      <div class="operation-strip">
        <span class="label-badge ${badgeClass(H(palaceArchive.status || "UNKNOWN"))}">Palace: ${esc(palaceMode)}</span>
        <span class="operation-chip">Storage posture: ${esc(storagePosture)}</span>
        <span class="operation-chip">Throne status: ${esc(throneStatus)}</span>
        <span class="operation-chip">Node prep: ${esc(H(O(palaceArchive.node_prep_state).distributed_deployment_status || "NOT_YET_IMPLEMENTED"))}</span>
      </div>
      <div class="cognition-grid">
        <div class="cognition-node trust">
          <div class="cognition-node-title">Суверенный дворец</div>
          <div class="cognition-node-value">${esc(palaceMode)}</div>
          <div class="cognition-node-note">move_policy=${esc(H(O(palaceArchive.palace_state).palace_move_policy || "OWNER_ONLY"))}</div>
        </div>
        <div class="cognition-node warning">
          <div class="cognition-node-title">Архив и воскрешение</div>
          <div class="cognition-node-value">${esc(shortText(archiveRole, 110))}</div>
          <div class="cognition-node-note">migration_validation=${esc(H(O(palaceArchive.archive_resurrection_state).migration_validation_status || "PLACEHOLDER_NOT_VALIDATED"))}</div>
        </div>
        <div class="cognition-node warning">
          <div class="cognition-node-title">Node-era подготовка</div>
          <div class="cognition-node-value">${esc(H(O(palaceArchive.node_prep_state).server_form || "COORDINATION_SHELL_FUTURE"))}</div>
          <div class="cognition-node-note">${esc(H(O(palaceArchive.node_prep_state).worker_nodes || "FUTURE_EXECUTORS_NOT_DEPLOYED"))}</div>
        </div>
      </div>
      <details class="vision-inline-details">
        <summary>Технические детали Palace/Archive</summary>
        <div class="vision-inline-body">
          source_path: ${pv(H(palaceArchive.source_path || "shared_systems/factory_observation_window_v1/adapters/IMPERIUM_PALACE_AND_ARCHIVE_STATE_SURFACE_V1.json"))}<br>
          archive_role: ${esc(H(O(palaceArchive.archive_resurrection_state).hdd_role || "UNKNOWN"))}<br>
          authority_boundary: HDD is not sovereign authority source
        </div>
      </details>
    `;
  }

  if (E("visionControlGates")) {
    const gateCards = controlGateRows.map((row) => `
      <div class="flow-route-card ${badgeClass(row.state || "UNKNOWN")}">
        <div class="flow-route-head">
          <span class="flow-route-title">${esc(H(row.title_ru || row.gate_id || "gate"))}</span>
          <span class="label-badge ${badgeClass(row.state || "UNKNOWN")}">${esc(H(row.state || "UNKNOWN"))}</span>
        </div>
        <div class="flow-route-note">gate_id=${esc(H(row.gate_id || "n/a"))}</div>
        <div class="flow-route-note">source=${esc(shortText(H(row.source_path || "n/a"), 92))}</div>
      </div>
    `).join("");
    E("visionControlGates").innerHTML = `
      <div class="operation-strip">
        <span class="label-badge ${badgeClass(controlGateSummary)}">Summary: ${esc(controlGateSummary)}</span>
        <span class="operation-chip">Blocked: ${esc(String(controlGates.blocked_count ?? 0))}</span>
        <span class="operation-chip">Warning: ${esc(String(controlGates.warning_count ?? 0))}</span>
        <span class="operation-chip">Rows: ${esc(String(controlGateRows.length))}</span>
      </div>
      <div class="vision-card-subtle">Gate-слой объединяет Throne/coverage/dominance/runtime/continuity и не дает stale-правде маскироваться под текущую.</div>
      <div class="flow-route-grid">${gateCards || `<div class="vision-card-subtle">Gate rows не загружены.</div>`}</div>
      <details class="vision-inline-details">
        <summary>Технические детали Control Gates</summary>
        <div class="vision-inline-body">
          source_path: ${pv(H(controlGates.source_path || "shared_systems/factory_observation_window_v1/adapters/IMPERIUM_CONTROL_GATES_SURFACE_V1.json"))}<br>
          gate_summary: ${esc(controlGateSummary)}<br>
          contract_gate_state: ${esc(H(administratumGateState))}
        </div>
      </details>
    `;
  }

  if (E("visionEventFlowSpine")) {
    const eventClasses = A(eventFlow.event_classes);
    const flowChainStates = A(eventFlow.flow_chain_states || eventFlow.flow_chain);
    const routeStates = A(eventFlow.changed_sector_routes);
    const signalVessels = A(eventFlow.signal_vessels);
    const bloodflowProfile = O(eventFlow.living_bloodflow_profile);
    const transitionMarkers = O(eventFlow.transition_markers);
    const stateCounters = O(eventFlow.state_counters);
    const classCounts = O(eventFlow.class_counts);
    const sectorCounts = O(eventFlow.sector_counts);
    const eventCards = eventClasses.map((cls) => {
      const cid = H(cls.event_class_id || "event_class");
      const count = Number(classCounts[cid] ?? 0);
      return `
        <div class="event-class-card">
          <div class="event-class-head">
            <span class="event-class-title">${esc(cid)}</span>
            <span class="event-class-count">${esc(String(count))}</span>
          </div>
          <div class="event-class-note">${esc(shortText(cls.description || "event class", 96))}</div>
          <div class="event-class-note">mode=${esc(cls.trigger_mode || "UNKNOWN")} | severity=${esc(cls.default_severity || "info")}</div>
        </div>
      `;
    }).join("");
    const sectorCards = Object.keys(sectorCounts).map((sid) => `
      <div class="event-route-segment">
        <div class="event-route-name">${esc(deptRu(sid, sid))}</div>
        <div class="event-route-value">${esc(String(sectorCounts[sid]))} событий</div>
      </div>
    `).join("");
    const flowSteps = flowChainStates.map((step) => `
      <div class="flow-step-card ${badgeClass(step.state || step.default_state || "UNKNOWN")}">
        <div class="flow-step-head">
          <span class="flow-step-title">${esc(step.title_ru || step.step_id || "flow_step")}</span>
          <span class="label-badge ${badgeClass(step.state || step.default_state || "UNKNOWN")}">${esc(step.state || step.default_state || "UNKNOWN")}</span>
        </div>
        <div class="flow-step-note">${esc(shortText(step.description || "flow step", 110))}</div>
      </div>
    `).join("");
    const routeCards = routeStates.map((route) => `
      <div class="flow-route-card ${badgeClass(route.status || route.default_state || "UNKNOWN")}">
        <div class="flow-route-head">
          <span class="flow-route-title">${esc(route.title_ru || route.route_id || "route")}</span>
          <span class="label-badge ${badgeClass(route.status || route.default_state || "UNKNOWN")}">${esc(route.status || route.default_state || "UNKNOWN")}</span>
        </div>
        <div class="flow-route-note">${esc(H(route.from_sector || "from") + " -> " + H(route.to_sector || "to"))}</div>
        <div class="flow-route-note">hits=${esc(String(route.event_count ?? 0))} | triggers=${esc(shortText(A(route.trigger_classes).join(", ") || "n/a", 84))}</div>
      </div>
    `).join("");
    const vesselCards = signalVessels.map((vessel) => `
      <div class="flow-route-card ${badgeClass(vessel.status || "UNKNOWN")}">
        <div class="flow-route-head">
          <span class="flow-route-title">${esc(vessel.title_ru || vessel.vessel_id || "vessel")}</span>
          <span class="label-badge ${badgeClass(vessel.status || "UNKNOWN")}">${esc(vessel.status || "UNKNOWN")}</span>
        </div>
        <div class="flow-route-note">${esc(shortText(A(vessel.route_sequence).join(" -> ") || "route sequence n/a", 92))}</div>
        <div class="flow-route-note">hits=${esc(String(vessel.event_count ?? 0))}</div>
      </div>
    `).join("");
    const transitionCards = [
      { title: "active_now", value: transitionMarkers.active_now || "n/a" },
      { title: "waiting_on", value: transitionMarkers.waiting_on || "n/a" },
      { title: "blocked_by", value: transitionMarkers.blocked_by || "n/a" },
      { title: "proven_now", value: transitionMarkers.proven_now || "n/a" },
      { title: "route_focus", value: transitionMarkers.route_focus || "n/a" }
    ].map((item) => `
      <div class="diff-card">
        <div class="diff-title">${esc(item.title)}</div>
        <div class="diff-value">${esc(shortText(item.value, 84))}</div>
      </div>
    `).join("");
    const latestEvent = O(eventFlow.latest_event);
    E("visionEventFlowSpine").innerHTML = `
      <div class="operation-strip">
        <span class="operation-chip">Статус: ${esc(eventFlow.status || "UNKNOWN")}</span>
        <span class="operation-chip">Режим: ${esc(O(eventFlow.channel_profile).default_mode || "UNKNOWN")}</span>
        <span class="operation-chip">Diff-triggers: ${esc(String(eventFlow.diff_preview_trigger_count ?? 0))}</span>
        <span class="operation-chip">Источники: ${esc(String(A(eventFlow.event_sources).length))}</span>
        <span class="operation-chip ${badgeClass(eventFlow.flow_posture || "WAIT")}">Flow posture: ${esc(eventFlow.flow_posture || "WAIT")}</span>
      </div>
      <div class="vision-card-subtle">Что происходит: event-flow spine ведет кровь системы по цепочке event -> assessment -> case/insight -> stage movement -> owner review.</div>
      <div class="vision-card-subtle">Профиль кровотока: ${esc(shortText(H(bloodflowProfile.flow_contract || "EVENT_TO_REVIEW_TO_STAGE_TO_OWNER_CONSEQUENCE"), 108))} | режим=${esc(H(bloodflowProfile.always_on_mode || "QUIET_HEARTBEAT"))}.</div>
      <div class="metric-grid">
        <div class="metric-card"><div class="metric-title">ACTIVE</div><div class="metric-value">${esc(String(stateCounters.active ?? 0))}</div><div class="metric-note">выполняется сейчас</div></div>
        <div class="metric-card"><div class="metric-title">WAIT</div><div class="metric-value">${esc(String(stateCounters.waiting ?? 0))}</div><div class="metric-note">ожидает триггер</div></div>
        <div class="metric-card"><div class="metric-title">BLOCKED</div><div class="metric-value">${esc(String(stateCounters.blocked ?? 0))}</div><div class="metric-note">требует вмешательства</div></div>
        <div class="metric-card"><div class="metric-title">PROVEN</div><div class="metric-value">${esc(String(stateCounters.proven ?? 0))}</div><div class="metric-note">подтверждено событием</div></div>
      </div>
      <div class="flow-step-grid">${flowSteps || `<div class="vision-card-subtle">Flow chain пока не объявлен.</div>`}</div>
      <div class="flow-route-grid">${routeCards || `<div class="vision-card-subtle">Changed-sector маршруты пока не объявлены.</div>`}</div>
      <div class="flow-route-grid">${vesselCards || `<div class="vision-card-subtle">Signal vessels пока не объявлены.</div>`}</div>
      <div class="diff-preview-grid">${transitionCards}</div>
      <div class="event-flow-grid">${eventCards || `<div class="vision-card-subtle">Классы событий пока не объявлены.</div>`}</div>
      <div class="event-route-grid">${sectorCards || `<div class="vision-card-subtle">Секторные маршруты пока не зафиксированы.</div>`}</div>
      <div class="presence-node">
        <div class="change-head"><span>Последнее событие spine</span><span class="change-time">${esc(shortTime(latestEvent.occurred_at_utc || ""))}</span></div>
        <div class="vision-card-note">${esc(shortText(latestEvent.summary || "нет события", 98))}</div>
        <div class="vision-card-subtle">${pv(latestEvent.source_path || "n/a")} | ${esc(latestEvent.truth_class || "DERIVED_CANONICAL")}</div>
      </div>
      <details class="vision-inline-details">
        <summary>Технические детали event-flow spine</summary>
        <div class="vision-inline-body">
          surface_id: ${esc(eventFlow.surface_id || eventFlowState.surface_id || "UNKNOWN")}<br>
          resource_profile: ${esc(O(eventFlow.channel_profile).resource_profile || "UNKNOWN")}<br>
          source_path: ${pv(eventFlow.source_path || "shared_systems/factory_observation_window_v1/adapters/IMPERIUM_EVENT_FLOW_SPINE_SURFACE_V1.json")}<br>
          owner_review_trigger_count: ${esc(String(eventFlow.owner_review_trigger_count ?? 0))}<br>
          signal_summary: ${esc(eventFlow.active_signal_summary || "n/a")}<br>
          route_focus: ${esc(H(transitionMarkers.route_focus || "n/a"))}
        </div>
      </details>
    `;
  }

  if (E("visionDiffPreview")) {
    const stages = A(diffPreview.stages);
    const stageCards = stages.map((stage) => `
      <div class="diff-card">
        <div class="diff-title">${esc(stage.stage_id || "stage")}</div>
        <div class="diff-value">${esc(stage.status || "UNKNOWN")}</div>
        <div class="diff-note">${esc(shortText(stage.description || "stage note", 92))}</div>
      </div>
    `).join("");
    const knownGaps = A(diffPreview.known_gaps);
    const gapText = knownGaps.length
      ? knownGaps.map((g) => `${H(g.id || "gap")} (${H(g.status || "UNKNOWN")})`).join(", ")
      : "нет явных gap-записей";
    E("visionDiffPreview").innerHTML = `
      <div class="operation-strip">
        <span class="operation-chip">Pipeline: ${esc(O(diffPreview.pipeline_profile).pipeline_mode || "UNKNOWN")}</span>
        <span class="operation-chip">Compared: ${esc(String(diffPreview.compared_count ?? 0))}</span>
        <span class="operation-chip">Changed: ${esc(String(diffPreview.changed_count ?? 0))}</span>
        <span class="operation-chip">Missing: ${esc(String(diffPreview.missing_count ?? 0))}</span>
      </div>
      <div class="diff-preview-grid">${stageCards || `<div class="vision-card-subtle">Этапы preview-пайплайна не объявлены.</div>`}</div>
      <div class="presence-node">
        <div class="vision-card-title">Последний diff-pack</div>
        <div class="vision-card-note">${pv(diffPreview.latest_diff_pack_path || "n/a")}</div>
        <div class="vision-card-subtle">manifest: ${pv(diffPreview.latest_diff_manifest_path || "n/a")}</div>
        <div class="vision-card-subtle">contact sheet: ${pv(diffPreview.latest_contact_sheet_html || "n/a")}</div>
      </div>
      <div class="vision-card-subtle">Что происходит: before/after обзор теперь идет через повторяемый diff-pack flow, а не вручную по разрозненным скриншотам.</div>
      <div class="vision-card-subtle">Открытые границы: ${esc(shortText(gapText, 140))}</div>
      <details class="vision-inline-details">
        <summary>Технические entrypoints diff/preview</summary>
        <div class="vision-inline-body">
          capture loop: ${pv(O(diffPreview.entrypoints).capture_loop_script || "scripts/imperial_dashboard_visual_audit_loop.py")}<br>
          diff pack: ${pv(O(diffPreview.entrypoints).diff_pack_script || "scripts/imperium_diff_preview_pack.py")}
        </div>
      </details>
    `;
  }

  if (E("visionGoldenThrone")) {
    const mappedPaths = A(goldenThrone.mapped_paths);
    const mappedCards = mappedPaths.map((item) => `
      <div class="golden-path-card">
        <div class="golden-path-head">
          <span class="event-class-title">${esc(item.exists ? "FOUND" : "MISSING")}</span>
          <span class="label-badge ${item.exists ? "proven" : "partial"}">${esc(item.exists ? "SOURCE_PRESENT" : "SOURCE_MISSING")}</span>
        </div>
        <div class="golden-path-value">${pv(item.path || "n/a")}</div>
      </div>
    `).join("");
    E("visionGoldenThrone").innerHTML = `
      <div class="operation-strip">
        <span class="operation-chip">Authority anchor: ${esc(throneStatus)}</span>
        <span class="operation-chip">Discoverability: ${esc(goldenThrone.discoverability_status || "UNKNOWN")}</span>
        <span class="operation-chip">Dedicated bundle: ${esc(String(goldenThrone.dedicated_named_bundle_exists))}</span>
        <span class="operation-chip">Mapped paths: ${esc(String(goldenThrone.existing_path_count ?? 0))}/${esc(String(mappedPaths.length))}</span>
      </div>
      <div class="vision-card-subtle">Правда канона: authority берется только из ${pv(throneAnchorPath)}; discoverability слой не назначает ранг.</div>
      <div class="vision-card-subtle">Surrogate mapping сохранен только как discoverability/поисковый контур без sovereign-authority эффекта.</div>
      <div class="golden-grid">${mappedCards || `<div class="vision-card-subtle">Пути discoverability пока не объявлены.</div>`}</div>
      <details class="vision-inline-details">
        <summary>Маршрут поиска подтверждения</summary>
        <div class="vision-inline-body">${esc(shortText(A(goldenThrone.discovery_route).join(" -> ") || "n/a", 220))}</div>
      </details>
    `;
  }

  if (E("visionFactoryAssembly")) {
    const productLines = A(factoryAssembly.products || factoryProductionState.products);
    const stageLane = A(factoryAssembly.production_stages || factoryProductionState.production_stages);
    const morphologyProfile = O(factoryAssembly.factory_morphology_profile || factoryProductionState.factory_morphology_profile);
    const conveyorLanes = A(factoryAssembly.conveyor_lanes || factoryProductionState.conveyor_lanes);
    const stageMatrix = A(factoryAssembly.stage_transition_matrix || factoryProductionState.stage_transition_matrix);
    const stageGates = A(factoryAssembly.stage_gates || factoryProductionState.stage_gates);
    const qualityChecks = A(factoryAssembly.quality_checkpoints || factoryProductionState.quality_checkpoints);
    const postRelease = O(factoryAssembly.post_release_split || factoryProductionState.post_release_split);
    const livingFlowRelations = O(factoryAssembly.living_flow_relations || factoryProductionState.living_flow_relations);
    const evolutionLines = A(factoryAssembly.product_evolution_lines || productEvolutionMap.lines);
    const laneCards = conveyorLanes.map((lane) => `
      <div class="factory-lane-card ${badgeClass(lane.state || "UNKNOWN")}">
        <div class="factory-lane-head">
          <span class="factory-lane-title">${esc(lane.title_ru || lane.lane_id || "lane")}</span>
          <span class="label-badge ${badgeClass(lane.state || "UNKNOWN")}">${esc(lane.state || "UNKNOWN")}</span>
        </div>
        <div class="factory-lane-route">${esc(shortText(A(lane.stage_route).join(" -> ") || "route n/a", 180))}</div>
        <div class="factory-lane-note">active=${esc(lane.active_stage || "n/a")} | blocked=${esc(lane.blocked_stage || "n/a")}</div>
        <div class="factory-lane-note">proof focus=${esc(shortText(lane.proof_focus || "n/a", 88))}</div>
      </div>
    `).join("");
    const transitionCards = stageMatrix.map((step) => `
      <div class="factory-transition-card ${badgeClass(step.status || "UNKNOWN")}">
        <div class="factory-transition-title">${esc(`${step.from_stage || "from"} -> ${step.to_stage || "to"}`)}</div>
        <div class="factory-transition-note">gate=${esc(step.gate_id || "n/a")} | status=${esc(step.status || "UNKNOWN")}</div>
        <div class="factory-transition-note">${esc(shortText(step.proof_signal || "proof signal n/a", 100))}</div>
      </div>
    `).join("");
    const productCards = productLines.map((p) => {
      const modules = A(p.assembly_modules);
      const readinessChambers = A(p.readiness_chambers);
      const subsystemGroups = A(p.subsystem_groups);
      const rebuildPaths = A(p.rebuild_paths);
      const readinessGates = A(p.readiness_gates);
      const packagingState = O(p.packaging_state);
      const qualityGateVisuals = A(p.quality_gate_visuals);
      const flowMarkers = O(p.live_flow_markers);
      const assemblyCorridors = A(p.assembly_corridors);
      const evolutionLine = O(evolutionLines.find((x) => String(x.product_id || "").toLowerCase() === String(p.product_id || "").toLowerCase()));
      const ascentTrack = O(evolutionLine.ascent_track);
      const ascentLane = A(ascentTrack.ascent_lane || p.ascent_path_stages);
      const layers = modules.map((m) => `
        <div class="assembly-layer ${moduleLayerClass(m.state)}" title="Модуль сборки и его текущий gate-сигнал.">
          <div class="assembly-layer-head">
            <span class="assembly-layer-title">${esc(m.module_id || "module")}</span>
            <span class="label-badge ${badgeClass(m.state)}">${esc(m.state || "UNKNOWN")}</span>
          </div>
          <div class="assembly-layer-note">gate=${esc(m.gate || "n/a")} | truth=${esc(truthClassRu(m.truth_class || "UNKNOWN"))}</div>
        </div>
      `).join("");
      const blockerSummary = A(p.blockers).length ? A(p.blockers).join(", ") : "блокеры не зафиксированы";
      const groupCards = subsystemGroups.map((group) => `
        <div class="assembly-group ${badgeClass(group.state || "UNKNOWN")}">
          <div class="assembly-group-title">${esc(group.title_ru || group.group_id || "group")}</div>
          <div class="assembly-group-note">${esc(shortText(A(group.module_ids).join(", ") || "n/a", 72))}</div>
          <div class="assembly-group-note">gate=${esc(group.readiness_gate || "n/a")} | state=${esc(group.state || "UNKNOWN")}</div>
        </div>
      `).join("");
      const rebuildCards = rebuildPaths.map((path) => `
        <div class="assembly-rebuild-path ${badgeClass(path.status || "UNKNOWN")}">
          <span>${esc(path.path_id || "path")}</span>
          <span>${esc(path.from_module || "from")} -> ${esc(path.to_module || "to")}</span>
          <span>${esc(path.status || "UNKNOWN")}</span>
        </div>
      `).join("");
      const readinessGateText = readinessGates.length
        ? readinessGates.map((gate) => `${H(gate.gate_id)}=${H(gate.status)}`).join(" | ")
        : "gates=n/a";
      const qualityGateText = qualityGateVisuals.length
        ? qualityGateVisuals.map((gate) => `${H(gate.gate_id)}=${H(gate.status)}`).join(" | ")
        : "quality gates n/a";
      const ascentStatusLocal = H(ascentTrack.activation_status || "WAIT");
      return `
        <div class="assembly-product">
          <div class="assembly-head">
            <span class="assembly-title">${esc(p.display_name || p.product_id || "product")}</span>
            <span class="label-badge ${badgeClass(p.current_stage)}">${esc(p.current_stage || "UNKNOWN")}</span>
          </div>
          <div class="assembly-stage">Точка сейчас: ${esc(p.current_stage || "UNKNOWN")} | Цель: ${esc(p.target_point || evolutionLine.target_point || "UNKNOWN")}</div>
          <div class="assembly-rails">${layers || `<div class="assembly-layer"><div class="assembly-layer-title">modules unavailable</div><div class="assembly-layer-note">нет подтвержденных модулей в текущем шаге</div></div>`}</div>
          <div class="assembly-chamber-row">
            ${readinessChambers.map((ch) => `<span class="assembly-chamber ${moduleLayerClass(ch.status)}">${esc(ch.chamber_id || "chamber")}=${esc(ch.status || "UNKNOWN")}</span>`).join("") || `<span class="assembly-chamber">chambers=n/a</span>`}
          </div>
          <div class="assembly-group-grid">${groupCards || `<div class="assembly-group">subsystem groups not declared</div>`}</div>
          <div class="assembly-rebuild-grid">${rebuildCards || `<div class="assembly-rebuild-path">rebuild paths not declared</div>`}</div>
          <div class="assembly-corridor-grid">
            ${(assemblyCorridors.map((corridor) => `
              <div class="assembly-corridor ${badgeClass(corridor.status || "UNKNOWN")}">
                <div class="assembly-corridor-title">${esc(corridor.corridor_id || "corridor")}</div>
                <div class="assembly-corridor-note">${esc(H(corridor.from_group || "from"))} -> ${esc(H(corridor.to_group || "to"))}</div>
                <div class="assembly-corridor-note">status=${esc(H(corridor.status || "UNKNOWN"))}</div>
              </div>
            `).join("")) || `<div class="assembly-corridor">assembly corridors not declared</div>`}
          </div>
          <div class="factory-target-band">Readiness gates: ${esc(shortText(readinessGateText, 140))}</div>
          <div class="factory-target-band">Quality gate visuals: ${esc(shortText(qualityGateText, 140))}</div>
          <div class="factory-target-band">Packaging: ${esc(packagingState.status || "UNKNOWN")} | ${esc(shortText(packagingState.note || "n/a", 82))}</div>
          <div class="factory-target-band">Flow markers: active=${esc(flowMarkers.active_now || "n/a")} | waiting=${esc(flowMarkers.waiting_on || "n/a")} | blocked=${esc(flowMarkers.blocked_by || "n/a")} | proven=${esc(flowMarkers.recent_proven || "n/a")}</div>
          <div class="ascent-path-card ${badgeClass(ascentStatusLocal)}">
            <div class="ascent-path-title">Ascent path: продукт -> Voice of Imperium</div>
            <div class="ascent-path-note">current: ${esc(shortText(ascentTrack.current_product_stage_ru || evolutionLine.current_point || "n/a", 102))}</div>
            <div class="ascent-path-note">future: ${esc(shortText(ascentTrack.future_department_stage_ru || evolutionLine.target_point || "n/a", 102))}</div>
            <div class="ascent-path-note">boundary: ${esc(shortText(ascentTrack.activation_boundary || "release_readiness_proof_required", 88))} | status=${esc(ascentStatusLocal)}</div>
            <div class="ascent-lane-grid">
              ${(ascentLane.map((phase) => `
                <div class="ascent-lane-node ${badgeClass(phase.status || "UNKNOWN")}">
                  <span>${esc(phase.phase_id || phase.stage_id || "phase")}</span>
                  <strong>${esc(shortText(phase.title_ru || "phase", 64))}</strong>
                  <em>${esc(H(phase.status || "UNKNOWN"))}</em>
                </div>
              `).join("")) || `<div class="ascent-lane-node">ascent lane not declared</div>`}
            </div>
          </div>
          <div class="factory-target-band">Blockers: ${esc(shortText(blockerSummary, 104))}</div>
        </div>
      `;
    }).join("");
    const lanePreview = stageLane.length ? stageLane.join(" -> ") : "analysis -> rebuild -> packaging -> readiness";
    E("visionFactoryAssembly").innerHTML = `
      <div class="operation-strip">
        <span class="operation-chip">Factory: ${esc(factoryAssembly.factory_name || factoryAssembly.display_name || "Factory of Imperium")}</span>
        <span class="operation-chip">Вектор: ${esc(factoryAssembly.vector_state || "UNKNOWN")}</span>
        <span class="operation-chip">Продуктов в карте: ${esc(String(productLines.length))}</span>
        <span class="operation-chip">TikTok цель: ${esc(factoryAssembly.tiktok_target_point || "VOICE_OF_IMPERIUM_ADVERTISING_DEPARTMENT")}</span>
        <span class="operation-chip ${badgeClass(ascentStatus)}">Ascent status: ${esc(ascentStatus)}</span>
      </div>
      <div class="vision-card-subtle">Морфология фабрики: ${esc(shortText(H(morphologyProfile.style_language || "industrial cognition"), 110))} | органная схема: ${esc(shortText(A(morphologyProfile.organ_layout).join(" -> ") || "n/a", 130))}</div>
      <div class="vision-card-subtle">Линия сборки: ${esc(shortText(lanePreview, 136))}</div>
      <div class="vision-card-subtle">Гейты: ${esc(shortText(stageGates.map((g) => `${H(g.gate_id)}=${H(g.status)}`).join(", ") || "n/a", 180))}</div>
      <div class="vision-card-subtle">Качество: ${esc(shortText(qualityChecks.map((q) => `${H(q.checkpoint_id)}=${H(q.status)}`).join(", ") || "n/a", 180))}</div>
      <div class="factory-lane-grid">${laneCards || `<div class="vision-card-subtle">Conveyor lanes пока не объявлены.</div>`}</div>
      <div class="factory-transition-grid">${transitionCards || `<div class="vision-card-subtle">Stage transition matrix пока не объявлена.</div>`}</div>
      <div class="factory-assembly-grid">${productCards || `<div class="vision-card-subtle">Factory product карты пока не загружены.</div>`}</div>
      <div class="factory-target-band">Post-release split: ${esc(H(postRelease.status || "UNKNOWN"))} | branch=${esc(H(postRelease.tiktok_future_branch || "n/a"))}</div>
      <div class="factory-target-band">Living flow links: ${esc(shortText(Object.keys(livingFlowRelations).map((k) => `${k}=${livingFlowRelations[k]}`).join(" | ") || "n/a", 180))}</div>
      <div class="vision-card-subtle">Ролевое разделение: Brain = верхний truth/canon organ; Factory = отдельный production organism.</div>
      <div class="vision-card-subtle">Что происходит: показан конвейер сборки и модульные rails без фальшивого full-3D.</div>
      <div class="vision-card-subtle">Почему так: owner видит, где продукт слаб, где gate, и куда ведет следующая стадия.</div>
      <details class="vision-inline-details">
        <summary>Технические детали Factory layer</summary>
        <div class="vision-inline-body">
          surface_id: ${esc(factoryAssembly.surface_id || factoryProductionState.surface_id || "UNKNOWN")}<br>
          source_path: ${pv(factoryAssembly.source_path || "shared_systems/factory_observation_window_v1/adapters/IMPERIUM_FACTORY_PRODUCTION_STATE_V1.json")}<br>
          product_map_source: ${pv(factoryAssembly.product_map_source_path || "shared_systems/factory_observation_window_v1/adapters/IMPERIUM_PRODUCT_EVOLUTION_MAP_V1.json")}
        </div>
      </details>
    `;
  }

  if (E("visionPromptState")) {
    const boundaryLabel = H(promptState.trusted_boundary || livePrompt.trusted_boundary || "UNKNOWN");
    const promptStatus = H(promptState.active_prompt_state || livePrompt.active_prompt_state || "UNKNOWN");
    const promptHttp = promptObservability.workspace_prompt_lineage_http;
    const promptBoundaryHuman = boundaryLabel.includes("PARTIAL")
      ? "частичное доверие"
      : (boundaryLabel.includes("MISSING") ? "граница не подтверждена" : (boundaryLabel.includes("TRUST") ? "доверие подтверждено" : "граница зафиксирована"));
    E("visionPromptState").innerHTML = `
      <div class="operation-strip">
        <span class="label-badge ${boundaryLabel.includes("PARTIAL") ? "partial" : boundaryLabel.includes("MISSING") ? "nyi" : "proven"}" title="Граница доверия prompt-state: full prompt text не подменяется выдумкой.">${esc(promptBoundaryHuman)}</span>
        <span class="operation-chip" title="Текущий active prompt-state по lineage truth.">Состояние prompt: ${esc(statusRu(promptStatus))}</span>
        <span class="operation-chip" title="Проверка observability endpoint /workspace/prompt-lineage в latest verify run.">Проверка HTTP lineage: ${esc(String(promptHttp || "n/a"))}</span>
      </div>
      <div class="metric-grid">
        <div class="metric-card" title="Уникальный lineage id активного prompt-state.">
          <div class="metric-title">Lineage ID</div>
          <div class="metric-value">${esc(promptState.lineage_id || livePrompt.lineage_id || "UNKNOWN")}</div>
          <div class="metric-note">${esc(promptLineage.project_slug || "unknown_slug")} | ${esc(promptLineage.manifest_schema_version || "unknown_schema")}</div>
        </div>
        <div class="metric-card" title="Краткий source brief без раскрытия полного prompt text.">
          <div class="metric-title">Краткий источник prompt</div>
          <div class="metric-value">${esc(shortText(promptSourceBrief.prompt_excerpt || "missing", 84))}</div>
          <div class="metric-note">Полный текст раскрыт: ${esc(String(promptBoundary.full_prompt_text_exposed))}</div>
        </div>
        <div class="metric-card" title="Почему этому можно/нельзя доверять прямо сейчас.">
          <div class="metric-title">Пояснение доверия</div>
          <div class="metric-value">${esc(shortText(promptBoundary.boundary_note || "n/a", 84))}</div>
          <div class="metric-note">${promptMissing.length ? `Отсутствуют поля: ${esc(promptMissing.join(", "))}` : "Отсутствующих полей нет"}</div>
        </div>
      </div>
      <div class="vision-card-subtle">Что происходит: виден активный lineage и текущая граница доверия prompt-состояния.</div>
      <div class="vision-card-subtle">Можно ли верить: только lineage/source brief; полный prompt-текст не выдумывается.</div>
      <details class="vision-inline-details">
        <summary>Технические детали prompt-lineage</summary>
        <div class="vision-inline-body">
          active_prompt_state: ${esc(promptStatus)}<br>
          lineage_id: ${esc(promptState.lineage_id || livePrompt.lineage_id || "UNKNOWN")}<br>
          workspace_prompt_lineage_http: ${esc(String(promptHttp || "n/a"))}<br>
          trusted_boundary: ${esc(boundaryLabel)}
        </div>
      </details>
    `;
  }

  if (E("visionSystemSemantics")) {
    const securityMissing = A(semanticSecurity.doctrine_missing_paths);
    const unknownReasonBreakdown = O(semanticTruth.unknown_reason_breakdown);
    const unknownReasonRegistry = A(semanticTruth.unknown_reason_registry).filter((x) => H(x.unknown_reason));
    const doctrineInventory = O(doctrineIntegrity.doctrine_inventory);
    const doctrineGaps = A(doctrineIntegrity.doctrine_gaps);
    const unknownReasonSummary = [
      `не реализовано=${Number(unknownReasonBreakdown.not_implemented || 0)}`,
      `не смэпплено=${Number(unknownReasonBreakdown.not_mapped || 0)}`,
      `устаревший источник=${Number(unknownReasonBreakdown.stale_source || 0)}`,
      `ожидает owner-решения=${Number(unknownReasonBreakdown.owner_decision_pending || 0)}`,
      `вне scope шага=${Number(unknownReasonBreakdown.unavailable_in_step_scope || 0)}`
    ].join(" | ");
    const unknownReasonRows = unknownReasonRegistry
      .slice(0, 7)
      .map((item) => `${shortText(H(item.field_id || "field"), 42)} -> ${H(item.state || "UNKNOWN")} (${unknownReasonRu(item.unknown_reason)})`);
    E("visionSystemSemantics").innerHTML = `
      <div class="operation-strip">
        <span class="operation-chip" title="Общее состояние семантического слоя системы.">Слой семантики: ${esc(H(liveSemantic.implementation_label || "ACTIVE"))}</span>
        <span class="operation-chip" title="Сколько exact/derived/gap индикаторов сейчас выводится.">Точных: ${esc(String(exactTruthCount))} | Выведенных: ${esc(String(derivedTruthCount))} | Пробелов: ${esc(String(knownGapCount))}</span>
        <span class="operation-chip" title="Сколько semantic полей сейчас помечены как stale source.">Устаревших источников: ${esc(String(Number(semanticTruth.stale_source_count || 0)))}</span>
        <span class="operation-chip" title="Owner decision triggers на базе control/constitution/contradiction surfaces.">Триггеры решения: ${esc(String(A(semanticBrain.owner_decision_trigger_state).length))}</span>
        <span class="operation-chip" title="Целостность doctrine surfaces и явные boundary note.">Doctrine integrity: ${esc(H(doctrineIntegrity.status || "UNKNOWN"))} | gaps=${esc(String(doctrineGaps.length))}</span>
      </div>
      <div class="metric-grid">
        <div class="metric-card" title="Constitution posture, канон-границы и риск слета канона.">
          <div class="metric-title">Состояние конституции</div>
          <div class="metric-value">${esc(semanticConstitution.doctrine_posture || "UNKNOWN")}</div>
          <div class="metric-note">Риск дрейфа: ${esc(semanticConstitution.canon_drift_risk || "UNKNOWN")} | Нарушения: ${esc(String(semanticConstitution.breach_count ?? "n/a"))} | Предупреждения: ${esc(String(semanticConstitution.warning_count ?? "n/a"))}</div>
        </div>
        <div class="metric-card" title="Brain/reason/control consistency и health управления.">
          <div class="metric-title">Состояние мозга управления</div>
          <div class="metric-value">${esc(semanticBrain.control_health_state || "UNKNOWN")}</div>
          <div class="metric-note">Миссия: ${esc(semanticBrain.mission_consistency_verdict || "UNKNOWN")} | Task-program: ${esc(semanticBrain.task_program_consistency_verdict || "UNKNOWN")} | Команды: ${esc(semanticBrain.command_surface_verdict || "UNKNOWN")}</div>
        </div>
        <div class="metric-card" title="Memory/chronology/knowledge: что закреплено, что открыто, куда идем.">
          <div class="metric-title">Память и хронология</div>
          <div class="metric-value">${esc(semanticMemory.last_working_canonical_step_id || "UNKNOWN")}</div>
          <div class="metric-note">Система: ${esc(ageText(O(semanticMemory.age_axis).system_age_minutes))} | Режим: ${esc(ageText(O(semanticMemory.age_axis).regime_age_minutes))} | Продукт: ${esc(ageText(O(semanticMemory.age_axis).product_age_minutes))}</div>
        </div>
        <div class="metric-card" title="Интеграция продуктового состояния TikTok training-ground в системный semantic слой.">
          <div class="metric-title">Интеграция состояния продукта</div>
          <div class="metric-value">${esc(semanticProduct.runtime_process_state || productProcessState || "UNKNOWN")}</div>
          <div class="metric-note">Граница prompt: ${esc(O(semanticProduct.prompt_lineage_honesty).trusted_boundary || "UNKNOWN")} | Восстановление: ${esc(shortText(semanticProduct.runtime_recovery_signal || "none", 38))}</div>
        </div>
        <div class="metric-card" title="Sovereignty/security posture: local-only, external exposure, visibility restrictions и recovery doctrine.">
          <div class="metric-title">Безопасность и суверенность</div>
          <div class="metric-value">${esc(semanticSecurity.sovereignty_posture || "UNKNOWN")}</div>
          <div class="metric-note">Внешняя экспозиция: ${esc(semanticSecurity.external_exposure_state || "UNKNOWN")} | Видимость: ${esc(semanticSecurity.visibility_restrictions_posture || "UNKNOWN")} | Восстановление: ${esc(semanticSecurity.recovery_readiness_posture || "UNKNOWN")}</div>
        </div>
        <div class="metric-card" title="Покрытие Full Vision и границы pointer-only/doc-only зон.">
          <div class="metric-title">Покрытие dashboard</div>
          <div class="metric-value">${esc(coverageVerdict)}</div>
          <div class="metric-note">rows=${esc(String(coverageRows.length))} | missing=${esc(String(coverageMissing))} | pointer_only=${esc(String(coveragePointerOnly))}</div>
        </div>
        <div class="metric-card" title="Custodes + dominance: защита от stale/superseded truth mixing.">
          <div class="metric-title">Custodes / dominance</div>
          <div class="metric-value">${esc(custodesVigilance)} | stale_rules=${esc(String(staleDominanceCount))}</div>
          <div class="metric-note">lock=${esc(custodesLockMode)} | dominance_rules=${esc(String(dominanceRules.length))}</div>
        </div>
        <div class="metric-card" title="Doctrine inventory и boundary-контур без pointer-only маскировки.">
          <div class="metric-title">Doctrine inventory</div>
          <div class="metric-value">docs=${esc(String(doctrineInventory.governance_docs_total ?? 0))} | md=${esc(String(doctrineInventory.governance_markdown_total ?? 0))}</div>
          <div class="metric-note">next_step=${esc(shortText(H(doctrineInventory.next_canonical_step_id || "unknown-next-step"), 52))}</div>
        </div>
      </div>
      <div class="vision-card-subtle">Что происходит: семантический слой связывает канон, мозг, память, безопасность и продукт в одну truth-модель.</div>
      <div class="vision-card-subtle">Почему так: dashboard читает готовые surfaces и не придумывает смысл сам.</div>
      <div class="vision-card-subtle">Что под вопросом: все UNKNOWN/GAP/STALE остаются явными и не маскируются.</div>
      <details class="vision-inline-details">
        <summary>Технические границы и пробелы</summary>
        <div class="vision-inline-body">
          known gaps: ${esc(semanticGaps.map((x) => H(x.id || x.status || "gap")).join(", ") || "none")}<br>
          unknown reason breakdown: ${esc(unknownReasonSummary)}<br>
          unknown reason samples: ${esc(unknownReasonRows.join(" || ") || "none")}<br>
          security doctrine missing paths: ${esc(securityMissing.join(", ") || "none")}<br>
          truth class: ${esc(H(liveSemantic.truth_class || semantic.truth_class || "DERIVED_CANONICAL"))}
        </div>
      </details>
    `;
  }

  if (E("visionWorkFocus")) {
    E("visionWorkFocus").innerHTML = `
      <div class="vision-chip-row">
        <div class="vision-chip"><span class="vision-chip-key">Открыто</span><span class="vision-chip-val">${openCtr.length}</span></div>
        <div class="vision-chip"><span class="vision-chip-key">Закрыто</span><span class="vision-chip-val">${closedCtr.length}</span></div>
        <div class="vision-chip"><span class="vision-chip-key">Главный риск</span><span class="vision-chip-val">${esc(topRisk)}</span></div>
      </div>
      ${(openCtr.slice(0, 2).map((c) => `<div class="presence-node"><div class="vision-card-title">${esc(c.id)} [${esc(c.severity || "unknown")}]</div><div class="vision-card-note">${esc(shortText(c.title || "open contradiction", 88))}</div></div>`).join("")) || `<div class="vision-card-subtle">Открытых противоречий нет.</div>`}
    `;
  }

  if (E("visionChanges")) {
    E("visionChanges").innerHTML = `
      <div class="truth-pill-row">
        <span class="truth-pill proven">последний proof: ${esc(latestProofText)}</span>
        <span class="truth-pill warning">последний risk: ${esc(latestRiskText)}</span>
        <span class="truth-pill warning">последний blocker: ${esc(blockerText || "нет")}</span>
      </div>
      <div class="vision-card-subtle">канал: ${esc(liveChannelHuman)} (${esc(liveChannel.status || "starting")}) | ручной F5 не требуется</div>
      ${liveFeed.slice(0, 5).map((x) => `
      <div class="presence-node change-node ${app.liveDelta.hasNewEvent && app.liveDelta.latestEventId === x.event_id ? "new-arrival" : ""}">
        <div class="change-head"><span>${eventRu(x.event_type)}</span><span class="change-time">${esc(shortTime(x.occurred_at_utc))}</span></div>
        <div class="vision-card-note">${esc(shortText(x.summary || "без описания", 95))}</div>
        <details class="vision-inline-details"><summary>источник</summary><div class="vision-inline-body">${pv(x.source_path || "n/a")} | ${esc(x.truth_class || "SOURCE_EXACT")}</div></details>
      </div>
    `).join("") || `<div class="vision-card-subtle">Новых событий пока нет.</div>`}
    `;
  }

  if (E("visionProven")) {
    const proven = [
      "OPTION_B зафиксирован",
      "Gate C подтвержден",
      `Wave 1: ${tik.wave_1_status || "UNKNOWN"}`,
      `Gate D: ${gates.gate_d || "UNKNOWN"}`,
      "localhost owner window живой",
      O(live.contracts).live_event_log_loaded ? "Live feed загружен" : "Live feed ожидается"
    ];
    E("visionProven").innerHTML = `<div class="truth-pill-row">${proven.map((x) => `<span class="truth-pill proven">${esc(x)}</span>`).join("")}</div>`;
  }

  if (E("visionQuestions")) {
    const wavePostStage = O(tik.post_wave1_stage);
    const open = [
      openCtr.length ? `open contradictions: ${openCtr.map((x) => x.id).join(", ")}` : "open contradictions: none",
      `Gate D status: ${gates.gate_d || "UNKNOWN"}`,
      `Wave 1 status: ${tik.wave_1_status || "UNKNOWN"}`,
      `Post-wave stage: ${wavePostStage.status || "UNKNOWN"}`,
      "event bus: NOT YET IMPLEMENTED (честно обозначено)",
      "before/after diff engine: NOT YET IMPLEMENTED",
      "auto preview pipeline: NOT YET IMPLEMENTED"
    ];
    E("visionQuestions").innerHTML = `<div class="truth-pill-row">${open.map((x) => `<span class="truth-pill warning">${esc(shortText(x, 74))}</span>`).join("")}</div>`;
  }

  if (E("visionHistorySeed")) {
    const historyNodes = A(O(state.production_history_seed).nodes);
    const historyFeed = historyNodes
      .slice()
      .sort((a, b) => Date.parse(String(b.occurred_at_utc || "")) - Date.parse(String(a.occurred_at_utc || "")))
      .slice(0, 8);
    E("visionHistorySeed").innerHTML = historyFeed.map((node) => `
      <div class="history-node" title="Подтвержденный исторический узел из production history seed (repo-visible source).">
        <div class="history-node-head">
          <span class="history-node-title">${esc(node.title || node.id || "history_node")}</span>
          <span class="history-node-time">${esc(shortTime(node.occurred_at_utc || node.at || ""))}</span>
        </div>
        <div class="history-node-note">${esc(shortText(node.summary || node.note || "исторический узел", 120))}</div>
        <div class="history-node-source">${pv(node.source_path || "n/a")} | ${esc(node.truth_class || "SOURCE_EXACT")}</div>
      </div>
    `).join("") || `<div class="vision-card-subtle">Production history seed пока не содержит узлов.</div>`;
  }

  if (E("visionMemoryChronology")) {
    const chronology = A(semanticMemory.chronology_nodes).length
      ? A(semanticMemory.chronology_nodes).slice().sort((a, b) => Date.parse(String(b.occurred_at_utc || b.at || "")) - Date.parse(String(a.occurred_at_utc || a.at || ""))).slice(0, 5)
      : historySortedDesc.slice(0, 5);
    const knownState = A(semanticMemory.known_now).length
      ? A(semanticMemory.known_now)
      : [
        `текущий primary bundle: ${activeBundleName}`,
        `режим источника: ${bindingDisclosure.selection_mode || binding.selection_mode || "unknown"}`,
        `статус волны: ${tik.wave_1_status || "UNKNOWN"}`,
        `post-wave этап: ${postWaveStage.status || "UNKNOWN"}`,
        `статус Gate D: ${gates.gate_d || "UNKNOWN"}`,
        `последнее изменение: ${latestEvt.event_type ? eventRu(latestEvt.event_type) : "none"}`
      ];
    const memoryAge = O(semanticMemory.age_axis);
    const memorySystemAge = Number.isFinite(Number(memoryAge.system_age_minutes)) ? Number(memoryAge.system_age_minutes) : systemAgeMinutes;
    const memoryRegimeAge = Number.isFinite(Number(memoryAge.regime_age_minutes)) ? Number(memoryAge.regime_age_minutes) : regimeAgeMinutes;
    const memoryStableAge = Number.isFinite(Number(memoryAge.last_stable_point_age_minutes)) ? Number(memoryAge.last_stable_point_age_minutes) : lastStableAgeMinutes;
    E("visionMemoryChronology").innerHTML = `
      <div class="operation-strip">
        <span class="operation-chip">Возраст системы: ${esc(ageText(memorySystemAge))}</span>
        <span class="operation-chip">Возраст режима: ${esc(ageText(memoryRegimeAge))}</span>
        <span class="operation-chip">Возраст последней стабильной точки: ${esc(ageText(memoryStableAge))}</span>
        <span class="operation-chip">Последний канонический шаг: ${esc(semanticMemory.last_working_canonical_step_id || "UNKNOWN")}</span>
      </div>
      <div class="memory-known-grid">
        <div class="memory-column">
          <div class="owner-stage-label">Закрепленное состояние (сейчас)</div>
          ${knownState.map((x) => `<div class="owner-stage-item">${esc(shortText(x, 98))}</div>`).join("")}
        </div>
        <div class="memory-column">
          <div class="owner-stage-label">Хронология (подтвержденные узлы)</div>
          ${(chronology.map((node) => `
            <div class="history-node">
              <div class="history-node-head">
                <span class="history-node-title">${esc(node.title || node.id || "history_node")}</span>
                <span class="history-node-time">${esc(shortTime(node.occurred_at_utc || node.at || ""))}</span>
              </div>
              <div class="history-node-note">${esc(shortText(node.summary || node.note || "history node", 96))}</div>
              <div class="history-node-source">${pv(node.source_path || "n/a")} | ${esc(node.truth_class || "SOURCE_EXACT")}</div>
            </div>
          `).join("")) || `<div class="vision-card-subtle">Chronology узлы пока не зафиксированы.</div>`}
        </div>
      </div>
      <div class="vision-card-subtle">Что происходит: экран показывает, что уже закреплено и как система пришла в текущую точку.</div>
      <div class="vision-card-subtle">Можно ли верить: каждый исторический узел опирается на source_path и truth_class.</div>
      <details class="vision-inline-details">
        <summary>Технические поля памяти/хронологии</summary>
        <div class="vision-inline-body">
          last_working_canonical_step_id: ${esc(semanticMemory.last_working_canonical_step_id || "UNKNOWN")}<br>
          source mode: ${esc(bindingDisclosure.selection_mode || binding.selection_mode || "unknown")}<br>
          history nodes count: ${esc(String(historySortedDesc.length))}
        </div>
      </details>
    `;
  }

  if (E("visionCheckpoint")) {
    const pct = cp.total > 0 ? Math.round((cp.ready / cp.total) * 100) : 0;
    const pendingCount = cp.total - cp.ready;
    const ownerDecisionOpen = ownerDecisionTriggers.length > 0 || pendingCount > 0;
    const decisionReason = shortText(
      controlLimits.blocking_reason_detail
      || (cpMissing.length ? cpMissing.join(", ") : "решение владельца пока не требуется"),
      140
    );
    E("visionCheckpoint").innerHTML = `
      <div class="decision-banner ${ownerDecisionOpen ? "warning" : "stable"}">
        <div class="decision-banner-title">Фокус решения владельца</div>
        <div class="decision-banner-note">${ownerDecisionOpen ? "Есть незакрытые checkpoint-границы" : "Критичных checkpoint-границ сейчас нет"}</div>
        <div class="decision-banner-text">${esc(decisionReason)}</div>
      </div>
      <div class="operation-strip">
        <span class="operation-chip">Следующий checkpoint: ${esc(shortCheckpoint)}</span>
        <span class="operation-chip">готово: ${cp.ready}/${cp.total}</span>
        <span class="operation-chip">частично: ${cp.partial}</span>
      </div>
      <div class="lane-track checkpoint-beacon"><div class="lane-fill pulse" style="width:${pct}%"></div></div>
      <div class="checkpoint-list">${cp.checks.map((x) => `<div class="checkpoint-item ${x.ready ? "is-ready" : x.partial ? "is-partial" : "is-pending"}"><span class="checkpoint-name">${esc(checkpointRuleRu(x.r))}</span><span class="label-badge ${x.ready ? "proven" : x.partial ? "partial" : "scaffolded"}">${x.ready ? "ГОТОВО" : x.partial ? "ЧАСТИЧНО" : "ОЖИДАЕТСЯ"}</span></div>`).join("")}</div>
      <details class="vision-inline-details">
        <summary>Технические checkpoint-коды</summary>
        <div class="vision-inline-body">
          next_checkpoint_code: ${esc(cp.next)}<br>
          readiness_percent: ${esc(String(pct))}%<br>
          partial_count: ${esc(String(cp.partial))}
        </div>
      </details>
    `;
  }

  if (E("visionGrowthLane")) {
    const p1 = String(ws.status || "").toUpperCase() === "IN_PROGRESS" ? 45 : 10;
    const p2 = (openCtr.length + closedCtr.length) ? Math.round((closedCtr.length / (openCtr.length + closedCtr.length)) * 100) : 0;
    const p3 = cp.total ? Math.round((cp.ready / cp.total) * 100) : 0;
    E("visionGrowthLane").innerHTML =
      lane("Линия выполнения Wave 1", p1, "Волна активна, но далека от финиша.") +
      lane("Линия закрытия contradictions", p2, "Доля закрытых contradictions.") +
      lane("Линия owner checkpoint", p3, "Готовность к следующему checkpoint.");
  }

  if (E("visionOwnerStage")) {
    const explicitHistorySeed = A(O(state.production_history_seed).nodes);
    const historySeed = explicitHistorySeed.length
      ? explicitHistorySeed.map((n) => ({
        id: H(n.id || "history_node"),
        title: H(n.title || "history"),
        summary: shortText(n.summary || n.note || "исторический узел", 98),
        at: shortTime(n.occurred_at_utc || n.at || ""),
        truthClass: H(n.truth_class || "SOURCE_EXACT"),
        sourcePath: H(n.source_path || "n/a")
      }))
      : buildProductionHistorySeedFromFeed(liveFeed);

    const routeNodes = stageOrder.map((n, idx) => {
      const stateKey = idx < activeIdx ? "done" : (idx === activeIdx ? "active" : (idx === activeIdx + 1 ? "next" : "waiting"));
      const pretty = deptRu(n.id, n.label);
      const focusClass = n.id === routeFocusNode ? "stage-focus-live" : "";
      const changedClass = changedNode && n.id === changedNode ? "stage-latest-live" : "";
      const blockerClass = blockerNode && n.id === blockerNode ? "stage-blocker-live" : "";
      return `<div class="stage-node ${pathNodeClass(stateKey)} ${focusClass} ${changedClass} ${blockerClass}">
        <div class="stage-node-code">${n.label}</div>
        <div class="stage-node-name">${pretty}</div>
        <div class="stage-node-note">${stageHint(stateKey)}</div>
      </div>`;
    }).join("");

    const worksetCards = (work.length ? work : [{ work_id: "W1-TR1", status: tr.status || "IN_PROGRESS", title: "active tranche workset" }]).map((w) => `
      <div class="owner-work-card ${pathNodeClass(w.status)}">
        <div class="owner-work-head">
          <span>${esc(w.work_id)}</span>
          <span class="label-badge ${badgeClass(w.status)}">${esc(w.status || "UNKNOWN")}</span>
        </div>
        <div class="owner-work-note">${esc(w.title || "work item")}</div>
      </div>
    `).join("");

    const changedLine = latestChangeText;
    const provenLine = latestProofText;
    const pendingLine = blockerText || latestRiskText;
    const checkpointNeed = cp.checks.filter((x) => !x.ready).map((x) => x.r).join(", ") || "checkpoint criteria ready";
    const historyCards = historySeed.map((node) => `
      <div class="history-node">
        <div class="history-node-head">
          <span class="history-node-title">${esc(node.title)}</span>
          <span class="history-node-time">${esc(node.at || "n/a")}</span>
        </div>
        <div class="history-node-note">${esc(node.summary)}</div>
        <div class="history-node-source">${pv(node.sourcePath)} | ${esc(node.truthClass)}</div>
      </div>
    `).join("");

    E("visionOwnerStage").innerHTML = `
      <div class="owner-stage-wrap">
        <div class="owner-stage-head">
          <div class="owner-stage-title">Живой маршрут проекта: где процесс сейчас</div>
          <div class="owner-stage-sub">Фокус маршрута: ${esc(routeFocusNode)} | Последний измененный узел: ${esc(changedNode || "n/a")} | Транш: ${esc(tr.tranche_id || "TRANCHE_UNKNOWN")}</div>
          <div class="owner-stage-presence-strip">
            <div class="owner-presence-chip"><span>Сейчас</span><strong>${esc(shortText(ws.objective || "must_fix_foundation", 44))}</strong></div>
            <div class="owner-presence-chip"><span>Последнее изменение</span><strong>${esc(shortText(changedLine, 52))}</strong></div>
            <div class="owner-presence-chip"><span>Последний proof</span><strong>${esc(shortText(provenLine, 52))}</strong></div>
            <div class="owner-presence-chip"><span>Главный риск</span><strong>${esc(topRisk)}</strong></div>
            <div class="owner-presence-chip"><span>Блокер</span><strong>${esc(shortText(pendingLine, 52))}</strong></div>
            <div class="owner-presence-chip"><span>Living flow</span><strong>${esc(shortText(flowPosture, 42))} | ${esc(shortText(flowRouteFocus || "route n/a", 36))}</strong></div>
            <div class="owner-presence-chip"><span>Flow marker</span><strong>${esc(shortText(H(flowTransitionMarkers.active_now || flowSummary || "n/a"), 52))}</strong></div>
            <div class="owner-presence-chip checkpoint"><span>Следующий checkpoint</span><strong>${esc(shortCheckpoint)}</strong></div>
          </div>
        </div>
        <div class="owner-stage-route ${app.liveDelta.hasNewEvent ? "route-event-arrived" : ""}">${routeNodes}</div>
        <div class="owner-stage-grid">
          <div class="owner-stage-column">
            <div class="owner-stage-label">Текущая операция</div>
            <div class="owner-stage-item">${esc(ws.objective || "must_fix_foundation")} | ${esc(tr.tranche_id || "TRANCHE_UNKNOWN")} | ${esc(tr.status || "IN_PROGRESS")}</div>
            <div class="owner-stage-label">Активный workset</div>
            ${worksetCards}
          </div>
          <div class="owner-stage-column">
            <div class="owner-stage-label">Фокус риска / contradiction / checkpoint</div>
            <div class="owner-stage-item">Открытых contradictions: ${openCtr.length}, высокий риск: ${risks.high ?? "n/a"}, критический риск: ${risks.critical ?? "n/a"}.</div>
            <div class="owner-stage-item">Готовность checkpoint: ${cp.ready}/${cp.total}; требуется: ${esc(shortText(checkpointNeed, 94))}.</div>
            <div class="owner-stage-item">Постура Gate D: ${esc(gates.gate_d || "UNKNOWN")}.</div>
            <div class="owner-stage-item">Ascent path к Voice of Imperium: status=${esc(ascentStatus)} | boundary=${esc(shortText(ascentBoundary, 76))}.</div>
            <div class="owner-stage-item">Flow routes: ${esc(shortText(flowRouteStates.filter((route) => Number(route.event_count ?? 0) > 0 || ["ACTIVE", "BLOCKED", "PROVEN"].includes(H(route.status).toUpperCase())).map((route) => `${H(route.route_id || "route")}:${H(route.status || "UNKNOWN")}`).join(" | ") || "n/a", 130))}.</div>
            <div class="owner-stage-item">Signal vessels: ${esc(shortText(flowSignalVessels.map((vessel) => `${H(vessel.vessel_id || "vessel")}:${H(vessel.status || "UNKNOWN")}`).join(" | ") || "n/a", 130))}.</div>
            <div class="owner-stage-item">Ascent lane: ${esc(shortText(ascentLane.map((phase) => `${H(phase.phase_id || phase.stage_id || "phase")}:${H(phase.status || "UNKNOWN")}`).join(" | ") || "n/a", 130))}.</div>
            <div class="lane-track checkpoint-beacon"><div class="lane-fill pulse" style="width:${cp.total ? Math.round((cp.ready / cp.total) * 100) : 0}%"></div></div>
          </div>
        </div>
        <div class="owner-stage-history">
          <div class="owner-stage-label">История производственной линии (первые подтвержденные узлы)</div>
          ${historyCards || `<div class="vision-card-subtle">История пока не накоплена.</div>`}
        </div>
        <div class="owner-stage-trace">
          <div class="owner-trace-card">
            <div class="owner-trace-title">Что изменилось только что</div>
            <div class="owner-trace-body">${esc(changedLine)}</div>
          </div>
          <div class="owner-trace-card">
            <div class="owner-trace-title">Что уже доказано</div>
            <div class="owner-trace-body">${esc(provenLine)}</div>
          </div>
          <div class="owner-trace-card">
            <div class="owner-trace-title">Последний риск</div>
            <div class="owner-trace-body">${esc(topRisk)}</div>
          </div>
          <div class="owner-trace-card">
            <div class="owner-trace-title">Что еще под вопросом</div>
            <div class="owner-trace-body">${esc(pendingLine)}</div>
          </div>
        </div>
        <details class="vision-inline-details">
          <summary>Технические коды производственной линии</summary>
          <div class="vision-inline-body">
            active_route_node_id: ${esc(routeFocusNode)}<br>
            latest_changed_node_id: ${esc(changedNode || "n/a")}<br>
            blocker_node_id: ${esc(blockerNode || "n/a")}<br>
            checkpoint_need_codes: ${esc(shortText(checkpointNeed, 120))}
          </div>
        </details>
      </div>
    `;
  }

  if (E("visionInspector")) {
    E("visionInspector").innerHTML =
      `<div class="compact-note inspector-intro">Command-layer truth summary выше; ниже только audit/debug raw layers.</div>` +
      `<details class="inspector-details"><summary>Raw bundle summary (command layer)</summary><pre>${S({ bundle: state.bundle_name, path: state.bundle_path, source_disclosure: state.source_disclosure, bundle_binding: state.bundle_binding, parity: state.parity, adapter: state.adapter })}</pre></details>` +
      `<details class="inspector-details"><summary>Raw canon sync (source layer)</summary><pre>${S(O(state.canon_state_sync))}</pre></details>` +
      `<details class="inspector-details"><summary>Raw live state (observational layer)</summary><pre>${S({ live_factory_state: live.live_factory_state, live_execution_state: live.live_execution_state, canon_projection: live.canon_projection, live_event_log_meta: live.live_event_log_meta })}</pre></details>` +
      `<details class="inspector-details"><summary>Raw agent runtime observability</summary><pre>${S(O(state.tiktok_agent_runtime_observability))}</pre></details>` +
      `<details class="inspector-details"><summary>Raw semantic state surfaces</summary><pre>${S({ state: O(state.system_semantic_state_surfaces), live: O(live.live_semantic_state) })}</pre></details>` +
      `<details class="inspector-details"><summary>Raw system brain state</summary><pre>${S(O(state.system_brain_state))}</pre></details>` +
      `<details class="inspector-details"><summary>Raw prompt lineage state</summary><pre>${S(O(state.prompt_lineage_state))}</pre></details>` +
      `<details class="inspector-details"><summary>Raw evolution/organs/factory channels</summary><pre>${S({ evolution: O(state.imperium_evolution_state), inquisition: O(state.imperium_inquisition_state), custodes: O(state.imperium_custodes_state), mechanicus: O(state.imperium_mechanicus_state), administratum: O(state.imperium_administratum_state), force: O(state.imperium_force_state), palace_archive: O(state.imperium_palace_archive_state), control_gates: O(state.imperium_control_gates_state), factory: O(state.imperium_factory_production_state), live_evolution: O(live.live_evolution_state), live_inquisition: O(live.live_inquisition_state), live_custodes: O(live.live_custodes_state), live_mechanicus: O(live.live_mechanicus_state), live_administratum: O(live.live_administratum_state), live_force: O(live.live_force_state), live_palace_archive: O(live.live_palace_archive_state), live_control_gates: O(live.live_control_gates_state), live_factory: O(live.live_factory_production_state) })}</pre></details>` +
      `<details class="inspector-details"><summary>Raw event-flow/diff-preview/golden-throne surfaces</summary><pre>${S({ event_flow: O(state.imperium_event_flow_state), diff_preview: O(state.imperium_diff_preview_state), golden_throne: O(state.imperium_golden_throne_discoverability), live_event_flow: O(live.live_event_flow_state), live_diff_preview: O(live.live_diff_preview_state), live_golden_throne: O(live.live_golden_throne_discoverability) })}</pre></details>`;
  }
}

function renderAll() {
  if (!app.state || !app.live) return;
  renderCommand(app.state, app.live);
  renderFullVision(app.state, app.live);
}

async function refreshAll() {
  const [state, live] = await Promise.all([J("/api/state"), J("/api/live_state")]);
  app.state = state;
  applyLiveUpdate(live, { mechanism: "bootstrap", status: "connected", note: "initial load" });
  renderAll();
}

function stopLivePolling() {
  if (app.liveTimer) {
    clearInterval(app.liveTimer);
    app.liveTimer = null;
  }
}

function stopLiveWatchdog() {
  if (app.liveWatchdogTimer) {
    clearInterval(app.liveWatchdogTimer);
    app.liveWatchdogTimer = null;
  }
}

function startLiveWatchdog() {
  stopLiveWatchdog();
  app.liveWatchdogTimer = setInterval(async () => {
    if (app.liveChannel.mechanism !== "sse") return;
    if (app.liveChannel.status !== "connected") return;
    const now = Date.now();
    const silenceMs = now - Number(app.lastLiveTickAtEpochMs || 0);
    if (silenceMs < 9000) return;
    try {
      const live = await J("/api/live_state");
      applyLiveUpdate(live, {
        mechanism: "sse",
        status: "connected",
        note: "sse watchdog refresh"
      });
      if (silenceMs > 24000) {
        startLivePolling("sse_stale_watchdog_fallback");
      }
    } catch (err) {
      app.liveChannel = {
        ...app.liveChannel,
        mechanism: "sse",
        status: "degraded",
        note: `watchdog error: ${err.message}`
      };
      startLivePolling("sse_watchdog_error");
    }
  }, 4500);
}

function handleLiveTickEvent(event, sourceTag = "sse") {
  try {
    const tick = JSON.parse(event.data || "{}");
    mergeStateExcerpt(tick.state_excerpt);
    app.lastLiveTickAtEpochMs = Date.now();
    applyLiveUpdate(tick.live, {
      mechanism: "sse",
      status: "connected",
      note: `live EventSource active (${sourceTag})`
    });
    if (app.liveDelta.hasNewEvent || (Date.now() - Number(app.lastStateSyncAtEpochMs || 0) > 6500)) {
      void syncStateSnapshot("sse_live_tick");
    }
  } catch (err) {
    app.liveChannel = {
      ...app.liveChannel,
      mechanism: "sse",
      status: "degraded",
      note: `sse parse error: ${err.message}`
    };
  }
}

function startLivePolling(reason = "polling_fallback") {
  stopLivePolling();
  stopLiveWatchdog();
  app.liveChannel = {
    ...app.liveChannel,
    mechanism: "polling",
    status: "active",
    note: `incremental polling (${reason})`
  };
  app.liveTimer = setInterval(async () => {
    try {
      const live = await J("/api/live_state");
      applyLiveUpdate(live, {
        mechanism: "polling",
        status: "active",
        note: "incremental polling active"
      });
      if (app.liveDelta.hasNewEvent || (Date.now() - Number(app.lastStateSyncAtEpochMs || 0) > 6500)) {
        void syncStateSnapshot("polling_live_tick");
      }
    } catch (err) {
      app.liveChannel = {
        ...app.liveChannel,
        mechanism: "polling",
        status: "degraded",
        note: `polling error: ${err.message}`
      };
    }
  }, 2200);
}

function startStateRefresh() {
  if (app.stateTimer) clearInterval(app.stateTimer);
  app.stateTimer = setInterval(async () => {
    try {
      const state = await J("/api/state");
      app.state = state;
      app.lastStateSyncAtEpochMs = Date.now();
      renderAll();
    } catch (err) {
      if (E("bundleSummary")) E("bundleSummary").textContent = `State refresh error: ${err.message}`;
    }
  }, 6000);
}

function startLiveChannel() {
  if (app.eventSource) {
    try {
      app.eventSource.close();
    } catch (_err) {
      // no-op
    }
    app.eventSource = null;
  }
  if (typeof EventSource === "undefined") {
    startLivePolling("eventsource_unavailable");
    return;
  }

  const stream = new EventSource("/api/live_stream?interval_ms=1600");
  app.eventSource = stream;
  app.liveChannel = {
    ...app.liveChannel,
    mechanism: "sse",
    status: "connecting",
    note: "opening EventSource channel"
  };

  stream.onopen = () => {
    stopLivePolling();
    app.lastLiveTickAtEpochMs = Date.now();
    app.liveChannel = {
      ...app.liveChannel,
      mechanism: "sse",
      status: "connected",
      note: "live EventSource connected"
    };
    startLiveWatchdog();
    if (app.state && app.live) renderAll();
  };

  stream.addEventListener("live_tick", (event) => {
    handleLiveTickEvent(event, "custom:live_tick");
  });

  stream.onmessage = (event) => {
    handleLiveTickEvent(event, "default:message");
  };

  stream.onerror = () => {
    stopLiveWatchdog();
    app.liveChannel = {
      ...app.liveChannel,
      mechanism: "sse",
      status: "degraded",
      note: "sse disconnected; fallback polling enabled"
    };
    try {
      stream.close();
    } catch (_err) {
      // no-op
    }
    app.eventSource = null;
    startLivePolling("sse_error");
  };
}

async function boot() {
  initMode();
  try {
    await refreshAll();
    startStateRefresh();
    startLiveChannel();
  } catch (err) {
    if (E("bundleSummary")) E("bundleSummary").textContent = `Error: ${err.message}`;
  }
}

boot();
