#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


DEFAULT_EVENT_LOG_PATH = "runtime/factory_observation/live_events.jsonl"


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def repo_root_from_script() -> Path:
    return Path(__file__).resolve().parents[3]


def resolve_path(repo_root: Path, path_value: str) -> Path:
    p = Path(path_value).expanduser()
    if p.is_absolute():
        return p
    return (repo_root / p).resolve()


def normalize_rel(path: Path, repo_root: Path) -> str:
    try:
        return str(path.relative_to(repo_root)).replace("\\", "/")
    except ValueError:
        return str(path)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Append one local live observation event to JSONL log.")
    parser.add_argument("--event-type", required=True, help="Event type (example: wave_started).")
    parser.add_argument("--summary", required=True, help="Short human-readable summary.")
    parser.add_argument("--severity", default="info", choices=["info", "warning", "critical"], help="Event severity.")
    parser.add_argument("--source-path", default="", help="Repo-relative source path.")
    parser.add_argument("--truth-class", default="SOURCE_EXACT", help="Truth class for this event.")
    parser.add_argument("--product-id", default="tiktok_agent_platform", help="Product id.")
    parser.add_argument("--event-id", default="", help="Optional explicit event id.")
    parser.add_argument("--log-path", default=DEFAULT_EVENT_LOG_PATH, help="JSONL file path.")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    repo_root = repo_root_from_script()
    log_path = resolve_path(repo_root, args.log_path)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    event_id = args.event_id.strip() or f"{args.event_type}_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')}"
    payload = {
        "event_id": event_id,
        "event_type": args.event_type.strip(),
        "occurred_at_utc": utc_now_iso(),
        "severity": args.severity.strip(),
        "summary": args.summary.strip(),
        "source_path": args.source_path.strip(),
        "product_id": args.product_id.strip(),
        "truth_class": args.truth_class.strip() or "SOURCE_EXACT",
        "producer": "local_live_event_writer",
    }

    with log_path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(payload, ensure_ascii=False) + "\n")

    print(
        json.dumps(
            {
                "status": "ok",
                "event_id": event_id,
                "log_path": normalize_rel(log_path, repo_root),
                "event_type": payload["event_type"],
                "severity": payload["severity"],
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
