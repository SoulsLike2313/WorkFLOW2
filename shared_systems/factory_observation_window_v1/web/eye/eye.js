(function () {
  const zoneOrbit = document.getElementById("zoneOrbit");
  const brainStatus = document.getElementById("brainStatus");
  const syncBadge = document.getElementById("syncBadge");
  const globalStatus = document.getElementById("globalStatus");
  const zoneHeader = document.getElementById("zoneHeader");
  const zoneContent = document.getElementById("zoneContent");
  const worldShell = document.getElementById("worldShell");
  const diveState = document.getElementById("diveState");
  const backBtn = document.getElementById("backToWorldBtn");
  const refreshBtn = document.getElementById("refreshBtn");

  const layerButtons = [...document.querySelectorAll(".layer-btn")];

  const state = {
    payload: null,
    live: null,
    selectedZone: null,
    sublayer: "owner",
    dive: "world",
  };

  const ZONES = [
    {
      id: "emperor_core",
      name: "Emperor Core",
      role: "Суверенный anchor, верхний источник воли.",
      dataRole: "Authority + throne discoverability.",
      navRole: "Главный вход в карту и обратный маршрут.",
      sourcePath: "docs/governance/GOLDEN_THRONE_AUTHORITY_ANCHOR_V1.json",
      extract: (s) => s?.imperium_golden_throne_discoverability || s?.system_brain_state?.throne_authority || {},
      angle: 270,
      radius: 200,
    },
    {
      id: "imperium_pyramid",
      name: "Imperium Pyramid",
      role: "Иерархия силы и целостность контуров.",
      dataRole: "Truth spine + governance acceptance.",
      navRole: "Переход к структурным слоям.",
      sourcePath: "runtime/administratum/IMPERIUM_TRUTH_SPINE_V1.json",
      extract: (s) => s?.imperium_truth_spine_state || {},
      angle: 330,
      radius: 280,
    },
    {
      id: "administratum",
      name: "Administratum",
      role: "Контракты, реестры, укладка сущностей.",
      dataRole: "Registry/control contract surfaces.",
      navRole: "Погружение в адресный и policy слой.",
      sourcePath: "shared_systems/factory_observation_window_v1/adapters/IMPERIUM_ADMINISTRATUM_STATE_SURFACE_V1.json",
      extract: (s) => s?.imperium_administratum_state || s?.imperium_parallel_channels?.administratum || {},
      angle: 20,
      radius: 280,
    },
    {
      id: "servitor_codex",
      name: "Servitor / Codex Chamber",
      role: "Исполнительный контур и рабочая сборка.",
      dataRole: "Code bank + live operation telemetry.",
      navRole: "Фокус на исполнение и change-feed.",
      sourcePath: "shared_systems/factory_observation_window_v1/adapters/IMPERIUM_CODE_BANK_STATE_SURFACE_V1.json",
      extract: (s) => s?.imperium_code_bank_state || {},
      angle: 90,
      radius: 280,
    },
    {
      id: "custodes",
      name: "Custodes Protection Layer",
      role: "Охрана границ и устойчивость канона.",
      dataRole: "Custodes state + gate watch.",
      navRole: "Переход в защитные меры.",
      sourcePath: "shared_systems/factory_observation_window_v1/adapters/IMPERIUM_ADEPTUS_CUSTODES_STATE_SURFACE_V1.json",
      extract: (s) => s?.imperium_custodes_state || s?.imperium_parallel_channels?.custodes || {},
      angle: 160,
      radius: 280,
    },
    {
      id: "inquisition",
      name: "Inquisition Audit Layer",
      role: "Drift/heresy контроль и эскалация.",
      dataRole: "Inquisition state surface.",
      navRole: "Погружение в риски и противоречия.",
      sourcePath: "shared_systems/factory_observation_window_v1/adapters/IMPERIUM_INQUISITION_STATE_SURFACE_V1.json",
      extract: (s) => s?.imperium_inquisition_state || s?.imperium_parallel_channels?.inquisition || {},
      angle: 220,
      radius: 280,
    },
    {
      id: "brain_layer",
      name: "Brain Layer",
      role: "Когнитивное ядро и route-маршрутизация.",
      dataRole: "system_brain_state + brain layers.",
      navRole: "Переход в матрёшку сознания.",
      sourcePath: "runtime/administratum/IMPERIUM_TRUTH_SPINE_V1.json",
      extract: (s) => ({ ...safeObj(s?.system_brain_state), layers: s?.imperium_brain_v2_layers || {} }),
      angle: 280,
      radius: 130,
    },
  ];

  function safeObj(x) {
    return x && typeof x === "object" ? x : {};
  }

  function toArray(x) {
    return Array.isArray(x) ? x : [];
  }

  function esc(str) {
    return String(str ?? "").replace(/[&<>"']/g, (m) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", "\"": "&quot;", "'": "&#39;" }[m]));
  }

  async function fetchJson(url) {
    const res = await fetch(url);
    if (!res.ok) {
      throw new Error(`${url} -> ${res.status}`);
    }
    return res.json();
  }

  function statusFromPayload(payload) {
    const p = safeObj(payload);
    const candidates = [
      p.status,
      p.verdict,
      p.overall_status,
      p.readiness,
      p.claim,
      p.gate_summary,
      p.truth_status,
    ];
    for (const item of candidates) {
      const val = String(item || "").trim();
      if (val) return val.toUpperCase();
    }
    return "UNKNOWN";
  }

  function truthBinding(payload, sourcePath) {
    const hasPayload = Object.keys(safeObj(payload)).length > 0;
    return hasPayload && sourcePath ? "TRUTH_BOUND" : "DISPLAY_ONLY";
  }

  function statusTone(status) {
    if (status.includes("PASS") || status.includes("TRUSTED") || status.includes("ADMISSIBLE") || status.includes("CLEAN")) return "ok";
    if (status.includes("FAIL") || status.includes("REJECT") || status.includes("BLOCK")) return "fail";
    return "";
  }

  function summaryRows() {
    const s = safeObj(state.payload);
    const live = safeObj(state.live);
    const summary = safeObj(s.summary || {});
    return [
      { label: "SYNC", value: String(summary.sync_verdict || "UNKNOWN").toUpperCase() },
      { label: "TRUST", value: String(summary.trust_verdict || "UNKNOWN").toUpperCase() },
      { label: "ADMISSION", value: String(summary.admission_verdict || "UNKNOWN").toUpperCase() },
      { label: "GATE RUNTIME", value: String(summary.gate_runtime_verdict || "UNKNOWN").toUpperCase() },
      { label: "LAW LOCK", value: String(summary.law_lock_verdict || "UNKNOWN").toUpperCase() },
      { label: "LIVE FEED", value: String((live.live_change_feed || []).length ? "ACTIVE" : "UNKNOWN") },
    ];
  }

  function renderGlobalStatus() {
    const rows = summaryRows();
    globalStatus.innerHTML = `<div class="status-grid">${rows
      .map((r) => `<div class="status-chip ${statusTone(r.value)}"><strong>${esc(r.label)}</strong><br>${esc(r.value)}</div>`)
      .join("")}</div>`;
    const syncValue = rows.find((x) => x.label === "SYNC")?.value || "UNKNOWN";
    syncBadge.textContent = `sync: ${syncValue}`;
  }

  function zoneView(zone) {
    const payload = zone.extract(state.payload);
    const status = statusFromPayload(payload);
    const binding = truthBinding(payload, zone.sourcePath);
    return { zone, payload, status, binding };
  }

  function renderZoneOrbit() {
    const cx = 50;
    const cy = 50;
    zoneOrbit.innerHTML = ZONES.map((zone) => {
      const rad = (zone.angle * Math.PI) / 180;
      const x = cx + (zone.radius / 7.6) * Math.cos(rad);
      const y = cy + (zone.radius / 7.6) * Math.sin(rad);
      const data = zoneView(zone);
      const active = state.selectedZone === zone.id ? "active" : "";
      return `
        <button
          class="zone-node ${active}"
          style="left:${x}%;top:${y}%;"
          data-zone-id="${esc(zone.id)}"
          type="button"
        >
          <div class="zone-name">${esc(zone.name)}</div>
          <div class="zone-meta">
            <span>${esc(data.status)}</span>
            <span class="${data.binding === "TRUTH_BOUND" ? "truth-bound" : "display-only"}">${esc(data.binding)}</span>
          </div>
        </button>
      `;
    }).join("");

    for (const node of zoneOrbit.querySelectorAll(".zone-node")) {
      node.addEventListener("click", () => {
        state.selectedZone = node.dataset.zoneId || null;
        state.dive = "zone";
        worldShell.classList.add("dive-active");
        backBtn.disabled = false;
        diveState.textContent = `Слой: ZONE / ${state.selectedZone || "UNKNOWN"}`;
        renderZoneOrbit();
        renderZonePanel();
      });
    }
  }

  function renderZonePanel() {
    if (!state.selectedZone) {
      zoneHeader.textContent = "Выберите зону на карте.";
      zoneContent.textContent = "Нет выбранной зоны.";
      return;
    }
    const zone = ZONES.find((z) => z.id === state.selectedZone);
    if (!zone) return;
    const { payload, status, binding } = zoneView(zone);
    const technical = JSON.stringify(payload, null, 2);
    const ownerLayer = `
      <p><strong>${esc(zone.name)}</strong></p>
      <p>Visual role: ${esc(zone.role)}</p>
      <p>Navigation role: ${esc(zone.navRole)}</p>
      <p>Truth role: ${esc(binding)} / status=${esc(status)}</p>
    `;
    const proofLayer = `
      <p><strong>Источник:</strong> ${esc(zone.sourcePath)}</p>
      <p><strong>Data role:</strong> ${esc(zone.dataRole)}</p>
      <p><strong>Binding policy:</strong> display-only shell, no authority-write.</p>
      <p><strong>Synthetic truth:</strong> forbidden.</p>
    `;
    const technicalLayer = `<pre>${esc(technical || "{}")}</pre>`;

    zoneHeader.innerHTML = `${esc(zone.name)} <span class="${binding === "TRUTH_BOUND" ? "truth-bound" : "display-only"}">${esc(binding)}</span>`;
    if (state.sublayer === "owner") zoneContent.innerHTML = ownerLayer;
    if (state.sublayer === "proof") zoneContent.innerHTML = proofLayer;
    if (state.sublayer === "technical") zoneContent.innerHTML = technicalLayer;
  }

  function renderBrain() {
    const payload = safeObj(state.payload);
    const status = statusFromPayload(payload.imperium_truth_spine_state || payload.system_brain_state || {});
    brainStatus.textContent = status;
  }

  function render() {
    renderGlobalStatus();
    renderBrain();
    renderZoneOrbit();
    renderZonePanel();
  }

  async function refresh() {
    const [fullState, liveState] = await Promise.all([fetchJson("/api/state"), fetchJson("/api/live_state")]);
    state.payload = fullState;
    state.live = liveState;
    render();
  }

  layerButtons.forEach((btn) => {
    btn.addEventListener("click", () => {
      state.sublayer = btn.dataset.layer || "owner";
      layerButtons.forEach((b) => b.classList.toggle("active", b === btn));
      renderZonePanel();
    });
  });

  backBtn.addEventListener("click", () => {
    state.dive = "world";
    state.selectedZone = null;
    worldShell.classList.remove("dive-active");
    diveState.textContent = "Слой: WORLD OVERVIEW";
    backBtn.disabled = true;
    render();
  });

  refreshBtn.addEventListener("click", () => {
    refresh().catch((err) => {
      zoneHeader.textContent = "Ошибка обновления";
      zoneContent.textContent = err.message;
    });
  });

  refresh().catch((err) => {
    syncBadge.textContent = "sync: ERROR";
    zoneHeader.textContent = "Ошибка запуска";
    zoneContent.textContent = err.message;
  });
  setInterval(() => {
    refresh().catch(() => {});
  }, 4000);
})();
