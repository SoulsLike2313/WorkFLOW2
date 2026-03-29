from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from playwright.sync_api import sync_playwright


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def repo_root_from_script() -> Path:
    return Path(__file__).resolve().parents[3]


def rel_path(path: Path, repo_root: Path) -> str:
    try:
        return str(path.resolve().relative_to(repo_root.resolve())).replace("\\", "/")
    except ValueError:
        return str(path.resolve())


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate owner window live updates without manual F5.")
    parser.add_argument("--url", default="http://127.0.0.1:8777/?mode=fullvision", help="Owner window URL.")
    parser.add_argument(
        "--edge-path",
        default=r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        help="Edge executable path for Playwright launch.",
    )
    parser.add_argument(
        "--output-dir",
        default="runtime/factory_observation/no_f5_probe",
        help="Output directory for screenshots and report.",
    )
    parser.add_argument(
        "--event-source-path",
        default="docs/review_artifacts/TIKTOK_WAVE1_DASHBOARD_LIVE_FIX_INTEGRATION_REPORT_V1.md",
        help="Source path used for emitted probe event.",
    )
    return parser


def emit_probe_event(repo_root: Path, marker: str, source_path: str) -> None:
    cmd = [
        sys.executable,
        str(repo_root / "shared_systems" / "factory_observation_window_v1" / "app" / "local_live_event_writer.py"),
        "--event-type",
        "verification_changed",
        "--severity",
        "info",
        "--summary",
        f"{marker}: in-place live update probe event (no manual refresh).",
        "--source-path",
        source_path,
        "--truth-class",
        "DERIVED_CANONICAL",
    ]
    subprocess.run(cmd, cwd=repo_root, check=True, capture_output=True, text=True)


def main() -> int:
    args = build_parser().parse_args()
    repo_root = repo_root_from_script()
    output_dir = (repo_root / args.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    marker = f"NO_F5_PROBE_{run_id}"
    before_path = output_dir / f"no_f5_before_{run_id}.png"
    after_path = output_dir / f"no_f5_after_{run_id}.png"
    report_path = output_dir / f"no_f5_probe_report_{run_id}.json"

    started = time.time()
    result: dict[str, object] = {
        "run_id": run_id,
        "started_at_utc": utc_now_iso(),
        "url": args.url,
        "marker": marker,
        "status": "FAIL",
        "live_update_observed_without_reload": False,
        "before_screenshot": rel_path(before_path, repo_root),
        "after_screenshot": rel_path(after_path, repo_root),
    }

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            executable_path=args.edge_path,
            args=["--disable-gpu", "--disable-dev-shm-usage"],
        )
        context = browser.new_context(viewport={"width": 1700, "height": 2100})
        page = context.new_page()

        page.goto(args.url, wait_until="domcontentloaded", timeout=60_000)
        page.wait_for_selector("#visionChanges", timeout=30_000)
        page.wait_for_selector("#visionOwnerStage", timeout=30_000)
        page.screenshot(path=str(before_path), full_page=True)

        # Ensure we're fully loaded before emitting the event.
        page.wait_for_timeout(1500)
        emit_probe_event(repo_root=repo_root, marker=marker, source_path=args.event_source_path)

        page.wait_for_function(
            """(probeMarker) => {
                const node = document.querySelector("#visionChanges");
                if (!node) return false;
                return (node.innerText || "").includes(probeMarker);
            }""",
            arg=marker,
            timeout=45_000,
        )
        page.wait_for_timeout(1200)
        page.screenshot(path=str(after_path), full_page=True)

        nav_type = page.evaluate(
            """() => {
                const entries = performance.getEntriesByType("navigation");
                if (!entries || !entries.length) return "unknown";
                return entries[0].type || "unknown";
            }"""
        )
        browser.close()

    finished = time.time()
    result["finished_at_utc"] = utc_now_iso()
    result["duration_seconds"] = round(finished - started, 3)
    result["status"] = "PASS"
    result["live_update_observed_without_reload"] = True
    result["navigation_type"] = nav_type
    report_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    print(rel_path(report_path, repo_root))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
