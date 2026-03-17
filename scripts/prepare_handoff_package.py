#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from detect_machine_mode import build_mode_payload

REPO_ROOT = Path(__file__).resolve().parents[1]
HANDOFF_SCHEMA_PATH = REPO_ROOT / "workspace_config" / "handoff_package_schema.json"
DEFAULT_INBOX = REPO_ROOT / "integration" / "inbox"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def run_git_status_files() -> list[str]:
    proc = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    files: list[str] = []
    for line in proc.stdout.splitlines():
        if len(line) >= 4:
            files.append(line[3:].strip().replace("\\", "/"))
    return sorted(set(x for x in files if x))


def parse_checks(items: list[str]) -> dict[str, str]:
    checks: dict[str, str] = {}
    for item in items:
        if "=" not in item:
            checks[item] = "UNKNOWN"
            continue
        key, value = item.split("=", 1)
        checks[key.strip()] = value.strip()
    return checks


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Prepare helper/integration handoff package into integration inbox.")
    parser.add_argument("--task-id", required=True)
    parser.add_argument("--node-id", required=True)
    parser.add_argument("--mode", choices=["auto", "helper", "integration"], default="auto")
    parser.add_argument("--verdict", choices=["PASS", "PASS_WITH_WARNINGS", "FAIL", "BLOCKED"], default="PASS_WITH_WARNINGS")
    parser.add_argument("--changed-file", dest="changed_files", action="append", default=[])
    parser.add_argument("--check", action="append", default=[], help="check_name=result")
    parser.add_argument("--risk", action="append", default=[])
    parser.add_argument("--blocker", action="append", default=[])
    parser.add_argument("--attachment", action="append", default=[])
    parser.add_argument("--output-dir", default=str(DEFAULT_INBOX))
    parser.add_argument("--package-id", default="")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    schema = load_json(HANDOFF_SCHEMA_PATH)
    mode_payload = build_mode_payload(intent="auto" if args.mode == "auto" else args.mode)

    effective_mode = mode_payload["machine_mode"] if args.mode == "auto" else args.mode
    if effective_mode not in {"helper", "integration"}:
        effective_mode = "integration"

    changed_files = sorted(set(args.changed_files or run_git_status_files()))
    checks = parse_checks(args.check)
    output_root = Path(args.output_dir)
    output_root.mkdir(parents=True, exist_ok=True)

    package_id = args.package_id.strip()
    if not package_id:
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        task_tag = args.task_id.replace("/", "_")
        node_tag = args.node_id.replace("/", "_")
        package_id = f"{timestamp}_{task_tag}_{node_tag}"

    package_dir = output_root / package_id
    attachments_dir = package_dir / "attachments"
    package_dir.mkdir(parents=True, exist_ok=True)
    attachments_dir.mkdir(parents=True, exist_ok=True)

    copied_attachments: list[str] = []
    for raw in args.attachment:
        src = (REPO_ROOT / raw).resolve()
        if not src.exists() or not src.is_file():
            continue
        rel_name = src.name
        dst = attachments_dir / rel_name
        shutil.copy2(src, dst)
        copied_attachments.append(f"attachments/{rel_name}")

    payload: dict[str, Any] = {
        "block_id": package_id,
        "task_id": args.task_id,
        "node_id": args.node_id,
        "mode": effective_mode,
        "changed_files": changed_files,
        "checks": checks,
        "risks": args.risk,
        "blockers": args.blocker,
        "verdict": args.verdict,
        "delivery_timestamp": utc_now(),
        "attachments": copied_attachments,
        "notes": {
            "mode_detection": mode_payload["machine_mode"],
            "mode_warnings": mode_payload["warnings"],
            "schema_version": schema.get("schema_version", "unknown"),
        },
    }

    (package_dir / "handoff_package.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    md_lines = [
        "# Handoff Package Report",
        "",
        f"- block_id: `{payload['block_id']}`",
        f"- task_id: `{payload['task_id']}`",
        f"- node_id: `{payload['node_id']}`",
        f"- mode: `{payload['mode']}`",
        f"- verdict: `{payload['verdict']}`",
        f"- delivery_timestamp: `{payload['delivery_timestamp']}`",
        "",
        "## Changed Files",
    ]
    md_lines.extend([f"- `{x}`" for x in changed_files] or ["- none"])
    md_lines += ["", "## Checks"]
    md_lines.extend([f"- `{k}` = `{v}`" for k, v in checks.items()] or ["- none"])
    md_lines += ["", "## Risks"]
    md_lines.extend([f"- {x}" for x in args.risk] or ["- none"])
    md_lines += ["", "## Blockers"]
    md_lines.extend([f"- {x}" for x in args.blocker] or ["- none"])

    (package_dir / "HANDOFF_REPORT.md").write_text("\n".join(md_lines) + "\n", encoding="utf-8")

    summary = {
        "package_dir": str(package_dir),
        "handoff_json": str(package_dir / "handoff_package.json"),
        "handoff_report": str(package_dir / "HANDOFF_REPORT.md"),
        "mode": effective_mode,
        "changed_files_count": len(changed_files),
        "attachments_count": len(copied_attachments),
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

