from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import sync_playwright


COMMAND_ZONES = [
    ("bundle_summary", "#bundleSummary"),
    ("factory_overview", "#factoryOverview"),
    ("semantic_state", "#systemSemanticState"),
    ("wave_control", "#wave1ControlSurfaces"),
    ("live_change_feed", "#liveChangeFeed"),
    ("queue_monitor", "#queueMonitor"),
]

FULL_VISION_ZONES = [
    ("signal_band", "#visionSignalBand"),
    ("matryoshka_core", "#visionMatryoshkaCore"),
    ("sector_immersion", "#visionSectorImmersion"),
    ("imperial_overview", "#visionImperialOverview"),
    ("owner_stage", "#visionOwnerStage"),
    ("brain_core", "#visionBrainCore"),
    ("evolution_channel", "#visionEvolutionChannel"),
    ("inquisition_core", "#visionInquisitionCore"),
    ("custodes_core", "#visionCustodesCore"),
    ("mechanicus_core", "#visionMechanicusCore"),
    ("administratum_core", "#visionAdministratumCore"),
    ("force_doctrine", "#visionForceDoctrine"),
    ("control_gates", "#visionControlGates"),
    ("palace_archive", "#visionPalaceArchive"),
    ("event_flow_spine", "#visionEventFlowSpine"),
    ("diff_preview", "#visionDiffPreview"),
    ("golden_throne", "#visionGoldenThrone"),
    ("factory_assembly", "#visionFactoryAssembly"),
    ("product_live", "#visionProductLive"),
    ("prompt_state", "#visionPromptState"),
    ("memory_chronology", "#visionMemoryChronology"),
    ("checkpoint", "#visionCheckpoint"),
]


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def with_mode(url: str, mode: str) -> str:
    parsed = urlparse(url)
    query = dict(parse_qsl(parsed.query, keep_blank_values=True))
    query["mode"] = mode
    return urlunparse(
        (
            parsed.scheme,
            parsed.netloc,
            parsed.path or "/",
            parsed.params,
            urlencode(query, doseq=True),
            parsed.fragment,
        )
    )


def wait_for_mode_ready(page: Any, mode: str) -> None:
    page.wait_for_function("target => document.body?.dataset?.mode === target", arg=mode, timeout=15000)
    if mode == "command":
        page.wait_for_function(
            """
            () => {
              const bundle = document.getElementById('bundleSummary');
              if (!bundle) return false;
              const text = (bundle.textContent || '').trim().toLowerCase();
              return text.length > 20 && !text.includes('loading...');
            }
            """,
            timeout=25000,
        )
    else:
        page.wait_for_function(
            """
            () => {
              const root = document.getElementById('visionImperialOverview');
              return !!root && ((root.innerText || '').trim().length > 10);
            }
            """,
            timeout=25000,
        )


def capture_mode(
    page: Any,
    base_url: str,
    mode: str,
    zones: list[tuple[str, str]],
    out_dir: Path,
) -> dict[str, Any]:
    mode_url = with_mode(base_url, mode)
    page.goto(mode_url, wait_until="domcontentloaded", timeout=60000)
    wait_for_mode_ready(page, mode)
    page.wait_for_timeout(1200)

    fullpage_file = out_dir / f"{mode}_fullpage.png"
    page.screenshot(path=str(fullpage_file), full_page=True)

    zone_results: list[dict[str, Any]] = []
    for zone_id, selector in zones:
        zone_file = out_dir / f"{mode}_zone_{zone_id}.png"
        entry = {
            "zone_id": zone_id,
            "selector": selector,
            "status": "MISSING",
            "screenshot_path": None,
        }
        try:
            locator = page.locator(selector).first
            if locator.count() > 0 and locator.is_visible(timeout=3000):
                locator.scroll_into_view_if_needed(timeout=4000)
                locator.screenshot(path=str(zone_file))
                entry["status"] = "CAPTURED"
                entry["screenshot_path"] = str(zone_file)
            else:
                entry["status"] = "NOT_VISIBLE"
        except PlaywrightError as exc:
            entry["status"] = "CAPTURE_FAILED"
            entry["error"] = str(exc)
        zone_results.append(entry)

    html_file = out_dir / f"{mode}_page.html"
    html_file.write_text(page.content(), encoding="utf-8")

    state_dump = page.evaluate(
        """
        async ({ mode }) => {
          const getJson = async (url) => {
            try {
              const r = await fetch(url);
              if (!r.ok) return { ok: false, status: r.status, payload: null };
              return { ok: true, status: r.status, payload: await r.json() };
            } catch (err) {
              return { ok: false, status: 0, error: String(err), payload: null };
            }
          };
          const [stateRes, liveRes] = await Promise.all([getJson('/api/state'), getJson('/api/live_state')]);
          return {
            captured_at_utc: new Date().toISOString(),
            requested_mode: mode,
            dom_mode: document.body?.dataset?.mode || null,
            mode_status_text: document.getElementById('modeStatusText')?.innerText || null,
            state_response: stateRes,
            live_state_response: liveRes
          };
        }
        """,
        {"mode": mode},
    )
    state_file = out_dir / f"{mode}_state_dump.json"
    state_file.write_text(json.dumps(state_dump, ensure_ascii=False, indent=2), encoding="utf-8")

    return {
        "mode": mode,
        "url": mode_url,
        "fullpage_screenshot": str(fullpage_file),
        "html_dump": str(html_file),
        "json_dump": str(state_file),
        "zones": zone_results,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Local visual audit loop for Imperial Dashboard using Playwright (COMMAND/FULL VISION)."
    )
    parser.add_argument("--url", default="http://127.0.0.1:8777/", help="Local dashboard URL")
    parser.add_argument("--out-dir", default="", help="Output directory for captures and dumps")
    parser.add_argument("--headful", action="store_true", help="Run browser in headful mode")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[1]
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out_dir = (
        Path(args.out_dir).resolve()
        if args.out_dir
        else repo_root / "docs" / "review_artifacts" / "visual_evidence" / f"imperial_dashboard_visual_audit_loop_{run_id}"
    )
    out_dir.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=not args.headful)
        context = browser.new_context(viewport={"width": 1920, "height": 1080})
        page = context.new_page()

        command_result = capture_mode(page, args.url, "command", COMMAND_ZONES, out_dir)
        fullvision_result = capture_mode(page, args.url, "fullvision", FULL_VISION_ZONES, out_dir)

        context.close()
        browser.close()

    meta = {
        "capture_method": "localhost_playwright_capture_loop",
        "generated_at_utc": utc_now_iso(),
        "run_id": run_id,
        "dashboard_url": args.url,
        "modes": [command_result, fullvision_result],
        "notes": [
            "no_fake_data",
            "paired_html_json_state_dumps",
            "full_page_and_major_zone_screenshots",
        ],
    }
    (out_dir / "capture_meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")

    print(json.dumps({"status": "ok", "out_dir": str(out_dir), "run_id": run_id}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
