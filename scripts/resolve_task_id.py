#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

from detect_machine_mode import build_mode_payload

REPO_ROOT = Path(__file__).resolve().parents[1]
TASK_REGISTRY = REPO_ROOT / "tasks" / "registry"
TASK_SCHEMA_PATH = REPO_ROOT / "workspace_config" / "block_task_schema.json"


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def find_task(task_id: str) -> tuple[dict[str, Any] | None, Path | None]:
    for path in sorted(TASK_REGISTRY.glob("*.json")):
        try:
            data = load_json(path)
        except Exception:
            continue
        if data.get("task_id") == task_id:
            return data, path
    return None, None


def validate_task_schema(task: dict[str, Any], schema: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = schema.get("required_fields", [])
    for field in required:
        if field not in task:
            errors.append(f"missing required field: {field}")
    regex = schema.get("task_id_regex")
    if regex and not re.match(regex, str(task.get("task_id", ""))):
        errors.append(f"task_id does not match regex {regex}")
    return errors


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Resolve task_id and print block execution contract summary.")
    parser.add_argument("--task-id", required=True)
    parser.add_argument("--intent", choices=["auto", "creator", "helper", "integration"], default="auto")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    schema = load_json(TASK_SCHEMA_PATH)
    mode_payload = build_mode_payload(intent=args.intent)

    task, task_path = find_task(args.task_id)
    if task is None:
        print(
            json.dumps(
                {
                    "task_id": args.task_id,
                    "status": "NOT_FOUND",
                    "registry_root": str(TASK_REGISTRY.relative_to(REPO_ROOT)).replace("\\", "/"),
                    "machine_mode": mode_payload["machine_mode"],
                    "mode_warnings": mode_payload["warnings"],
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 1

    errors = validate_task_schema(task, schema)
    payload = {
        "task_id": task["task_id"],
        "status": "RESOLVED" if not errors else "INVALID",
        "task_file": str(task_path.relative_to(REPO_ROOT)).replace("\\", "/"),
        "title": task.get("title"),
        "target_scope": task.get("target_scope"),
        "allowed_paths": task.get("allowed_paths", []),
        "forbidden_paths": task.get("forbidden_paths", []),
        "required_outputs": task.get("required_outputs", []),
        "required_checks": task.get("required_checks", []),
        "handoff_target": task.get("handoff_target"),
        "non_goals": task.get("non_goals", []),
        "machine_mode": mode_payload["machine_mode"],
        "mode_allowed_operations": mode_payload["operations"]["allowed"],
        "mode_forbidden_operations": mode_payload["operations"]["forbidden"],
        "schema_errors": errors,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())

