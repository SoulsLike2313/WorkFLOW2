#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
INBOX_CONTRACT_PATH = REPO_ROOT / "workspace_config" / "integration_inbox_contract.json"
HANDOFF_SCHEMA_PATH = REPO_ROOT / "workspace_config" / "handoff_package_schema.json"
TASK_SCHEMA_PATH = REPO_ROOT / "workspace_config" / "block_task_schema.json"
TASK_REGISTRY = REPO_ROOT / "tasks" / "registry"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def find_task(task_id: str) -> dict[str, Any] | None:
    for path in sorted(TASK_REGISTRY.glob("*.json")):
        try:
            data = load_json(path)
        except Exception:
            continue
        if data.get("task_id") == task_id:
            return data
    return None


def validate_handoff_schema(payload: dict[str, Any], schema: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    for field in schema.get("required_fields", []):
        if field not in payload:
            errors.append(f"missing required field: {field}")
    mode_values = schema.get("mode_values", [])
    if mode_values and payload.get("mode") not in mode_values:
        errors.append("mode not allowed by handoff schema")
    return errors


def path_in_scope(path: str, prefixes: list[str]) -> bool:
    normalized = path.replace("\\", "/")
    for prefix in prefixes:
        p = prefix.replace("\\", "/")
        if normalized == p or normalized.startswith(p.rstrip("/") + "/") or normalized.startswith(p):
            return True
    return False


def review_package(package_dir: Path, handoff_schema: dict[str, Any]) -> dict[str, Any]:
    handoff_path = package_dir / "handoff_package.json"
    result: dict[str, Any] = {
        "package": package_dir.name,
        "package_path": str(package_dir.relative_to(REPO_ROOT)).replace("\\", "/"),
        "reviewed_at": utc_now(),
        "decision": "QUARANTINE",
        "reasons": [],
    }

    if not handoff_path.exists():
        result["reasons"].append("handoff_package.json missing")
        return result

    try:
        payload = load_json(handoff_path)
    except Exception as exc:
        result["reasons"].append(f"handoff_package.json invalid JSON: {exc}")
        return result

    schema_errors = validate_handoff_schema(payload, handoff_schema)
    if schema_errors:
        result["reasons"].extend(schema_errors)
        result["decision"] = "QUARANTINE"
        return result

    task_id = str(payload.get("task_id", ""))
    task = find_task(task_id)
    if task is None:
        result["reasons"].append(f"task_id not found in registry: {task_id}")
        result["decision"] = "REJECT"
        return result

    changed_files = [str(x).replace("\\", "/") for x in payload.get("changed_files", [])]
    allowed_paths = [str(x) for x in task.get("allowed_paths", [])]
    forbidden_paths = [str(x) for x in task.get("forbidden_paths", [])]

    outside_allowed = [p for p in changed_files if not path_in_scope(p, allowed_paths)]
    touched_forbidden = [p for p in changed_files if path_in_scope(p, forbidden_paths)]

    if touched_forbidden:
        result["decision"] = "REJECT"
        result["reasons"].append("forbidden scope touched")
        result["touched_forbidden"] = touched_forbidden
        return result

    if outside_allowed:
        result["decision"] = "REJECT"
        result["reasons"].append("changed files outside allowed scope")
        result["outside_allowed"] = outside_allowed
        return result

    result["decision"] = "ACCEPT_CANDIDATE"
    result["reasons"].append("schema and scope checks passed")
    return result


def write_review_artifacts(review_queue: Path, review: dict[str, Any]) -> tuple[Path, Path]:
    review_dir = review_queue / review["package"]
    review_dir.mkdir(parents=True, exist_ok=True)
    json_path = review_dir / "review_result.json"
    md_path = review_dir / "review_result.md"
    json_path.write_text(json.dumps(review, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    md_lines = [
        "# Integration Review Result",
        "",
        f"- package: `{review['package']}`",
        f"- decision: `{review['decision']}`",
        f"- reviewed_at: `{review['reviewed_at']}`",
        "",
        "## Reasons",
    ]
    md_lines.extend([f"- {x}" for x in review.get("reasons", [])] or ["- none"])
    md_path.write_text("\n".join(md_lines) + "\n", encoding="utf-8")
    return json_path, md_path


def route_package(package_dir: Path, decision: str, contract_paths: dict[str, str]) -> str:
    mapping = {
        "ACCEPT_CANDIDATE": REPO_ROOT / contract_paths["accepted"],
        "REJECT": REPO_ROOT / contract_paths["rejected"],
        "QUARANTINE": REPO_ROOT / contract_paths["quarantine"],
    }
    target_root = mapping.get(decision)
    if not target_root:
        return ""
    target_root.mkdir(parents=True, exist_ok=True)
    target_path = target_root / package_dir.name
    if target_path.exists():
        shutil.rmtree(target_path)
    shutil.move(str(package_dir), str(target_path))
    return str(target_path.relative_to(REPO_ROOT)).replace("\\", "/")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Review integration inbox packages and classify decisions.")
    parser.add_argument("--route", action="store_true", help="Move packages from inbox to accepted/rejected/quarantine by decision.")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    inbox_contract = load_json(INBOX_CONTRACT_PATH)
    handoff_schema = load_json(HANDOFF_SCHEMA_PATH)
    _task_schema = load_json(TASK_SCHEMA_PATH)

    paths = inbox_contract.get("paths", {})
    inbox = REPO_ROOT / paths.get("inbox", "integration/inbox")
    review_queue = REPO_ROOT / paths.get("review_queue", "integration/review_queue")
    review_queue.mkdir(parents=True, exist_ok=True)
    inbox.mkdir(parents=True, exist_ok=True)

    package_dirs = [p for p in sorted(inbox.iterdir()) if p.is_dir()]
    reviews: list[dict[str, Any]] = []
    routed: list[dict[str, str]] = []

    for package_dir in package_dirs:
        review = review_package(package_dir, handoff_schema)
        json_path, md_path = write_review_artifacts(review_queue, review)
        review["review_result_json"] = str(json_path.relative_to(REPO_ROOT)).replace("\\", "/")
        review["review_result_md"] = str(md_path.relative_to(REPO_ROOT)).replace("\\", "/")
        if args.route:
            routed_to = route_package(package_dir, review["decision"], paths)
            if routed_to:
                routed.append({"package": package_dir.name, "decision": review["decision"], "routed_to": routed_to})
        reviews.append(review)

    summary = {
        "run_id": f"inbox-review-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}",
        "reviewed_at": utc_now(),
        "inbox_path": str(inbox.relative_to(REPO_ROOT)).replace("\\", "/"),
        "review_count": len(reviews),
        "decisions": {
            "ACCEPT_CANDIDATE": sum(1 for r in reviews if r["decision"] == "ACCEPT_CANDIDATE"),
            "REJECT": sum(1 for r in reviews if r["decision"] == "REJECT"),
            "QUARANTINE": sum(1 for r in reviews if r["decision"] == "QUARANTINE"),
        },
        "routed": routed,
        "reviews": reviews,
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

