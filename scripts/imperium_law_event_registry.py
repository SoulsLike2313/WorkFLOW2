#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = REPO_ROOT / "runtime" / "administratum" / "IMPERIUM_LAW_EVENT_REGISTRY_V1.json"
STATUS_PATH = REPO_ROOT / "runtime" / "administratum" / "IMPERIUM_LAW_CARRY_FORWARD_STATUS_V1.json"
NOTE_PATH = REPO_ROOT / "runtime" / "administratum" / "IMPERIUM_LAW_INJECTION_NOTE_V1.md"


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def normalize_rel(path: Path) -> str:
    return str(path.resolve().relative_to(REPO_ROOT.resolve())).replace("\\", "/")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def load_registry() -> dict[str, Any]:
    if REGISTRY_PATH.exists():
        payload = load_json(REGISTRY_PATH)
    else:
        payload = {}
    events = payload.get("events", [])
    if not isinstance(events, list):
        events = []
    return {
        "schema_version": "imperium_law_event_registry.v1",
        "generated_at_utc": payload.get("generated_at_utc", now_iso()),
        "events": events,
    }


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.rstrip() + "\n", encoding="utf-8")


def update_status_and_note(registry: dict[str, Any]) -> dict[str, Any]:
    events = list(registry.get("events", []) or [])
    pending = [item for item in events if not bool(item.get("codified", False))]
    codified = [item for item in events if bool(item.get("codified", False))]
    status = {
        "schema_version": "imperium_law_carry_forward_status.v1",
        "generated_at_utc": now_iso(),
        "registry_path": normalize_rel(REGISTRY_PATH),
        "total_events": len(events),
        "pending_events": len(pending),
        "codified_events": len(codified),
        "pending_event_ids": [str(item.get("event_id", "")) for item in pending if str(item.get("event_id", "")).strip()],
        "last_event_id": str(events[-1].get("event_id", "")) if events else "",
        "last_event_at_utc": str(events[-1].get("created_at_utc", "")) if events else "",
    }
    write_json(STATUS_PATH, status)

    lines = [
        "# IMPERIUM Law Injection Note",
        "",
        f"- generated_at_utc: `{status['generated_at_utc']}`",
        f"- registry: `{normalize_rel(REGISTRY_PATH)}`",
        f"- pending_events: `{status['pending_events']}`",
        "",
        "Use this block under next relevant master prompt:",
        "",
        "injected laws:",
    ]
    if pending:
        for item in pending:
            event_id = str(item.get("event_id", "")).strip() or "event_without_id"
            phrase = str(item.get("owner_phrase", "")).strip() or "owner law event"
            layer = str(item.get("target_layer", "shared")).strip() or "shared"
            lines.append(f"- [{event_id}] ({layer}) {phrase}")
    else:
        lines.append("- none")
    lines.extend(
        [
            "",
            "After codification, mark event as codified with evidence path.",
        ]
    )
    write_text(NOTE_PATH, "\n".join(lines))
    return status


def event_id_from_registry(events: list[dict[str, Any]]) -> str:
    seq = len(events) + 1
    return f"law_event_{seq:04d}"


def cmd_add(args: argparse.Namespace) -> int:
    registry = load_registry()
    events = list(registry.get("events", []) or [])
    event_id = args.event_id.strip() or event_id_from_registry(events)
    event = {
        "event_id": event_id,
        "created_at_utc": now_iso(),
        "source": args.source.strip() or "owner",
        "owner_phrase": args.owner_phrase.strip(),
        "target_layer": args.target_layer.strip() or "shared",
        "target_surface": args.target_surface.strip(),
        "next_prompt_injection_required": True,
        "codified": False,
        "codified_at_utc": "",
        "codified_path": "",
        "notes": args.notes.strip(),
    }
    events.append(event)
    registry["generated_at_utc"] = now_iso()
    registry["events"] = events
    write_json(REGISTRY_PATH, registry)
    status = update_status_and_note(registry)
    print(
        json.dumps(
            {
                "status": "ok",
                "action": "add",
                "event_id": event_id,
                "registry_path": normalize_rel(REGISTRY_PATH),
                "pending_events": status["pending_events"],
                "injection_note_path": normalize_rel(NOTE_PATH),
            },
            ensure_ascii=False,
        )
    )
    return 0


def cmd_codify(args: argparse.Namespace) -> int:
    registry = load_registry()
    events = list(registry.get("events", []) or [])
    target = args.event_id.strip()
    if not target:
        raise SystemExit("--event-id is required for codify")
    found = False
    for item in events:
        if str(item.get("event_id", "")).strip() != target:
            continue
        item["codified"] = True
        item["codified_at_utc"] = now_iso()
        item["codified_path"] = args.codified_path.strip()
        found = True
        break
    if not found:
        raise SystemExit(f"event not found: {target}")
    registry["generated_at_utc"] = now_iso()
    registry["events"] = events
    write_json(REGISTRY_PATH, registry)
    status = update_status_and_note(registry)
    print(
        json.dumps(
            {
                "status": "ok",
                "action": "codify",
                "event_id": target,
                "pending_events": status["pending_events"],
                "registry_path": normalize_rel(REGISTRY_PATH),
            },
            ensure_ascii=False,
        )
    )
    return 0


def cmd_status(_: argparse.Namespace) -> int:
    registry = load_registry()
    write_json(REGISTRY_PATH, registry)
    status = update_status_and_note(registry)
    print(
        json.dumps(
            {
                "status": "ok",
                "action": "status",
                "registry_path": normalize_rel(REGISTRY_PATH),
                "status_path": normalize_rel(STATUS_PATH),
                "injection_note_path": normalize_rel(NOTE_PATH),
                "pending_events": status["pending_events"],
                "total_events": status["total_events"],
            },
            ensure_ascii=False,
        )
    )
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="IMPERIUM law-event carry-forward registry.")
    sub = parser.add_subparsers(dest="command", required=True)

    add_cmd = sub.add_parser("add", help="Register new owner law event.")
    add_cmd.add_argument("--event-id", default="", help="Optional event id override.")
    add_cmd.add_argument("--source", default="owner")
    add_cmd.add_argument("--owner-phrase", required=True)
    add_cmd.add_argument("--target-layer", default="shared")
    add_cmd.add_argument("--target-surface", default="")
    add_cmd.add_argument("--notes", default="")
    add_cmd.set_defaults(func=cmd_add)

    codify_cmd = sub.add_parser("codify", help="Mark event as codified.")
    codify_cmd.add_argument("--event-id", required=True)
    codify_cmd.add_argument("--codified-path", required=True)
    codify_cmd.set_defaults(func=cmd_codify)

    status_cmd = sub.add_parser("status", help="Refresh status and injection note.")
    status_cmd.set_defaults(func=cmd_status)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
