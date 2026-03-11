from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from .config import load_config
from .update import PatchBundle, UpdateService


def _write_json(path: Path | None, payload: dict[str, Any]) -> None:
    if path is None:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _print_json(payload: dict[str, Any]) -> None:
    print(json.dumps(payload, ensure_ascii=False, indent=2))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Shortform local update/patch CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    check = sub.add_parser("check", help="Validate update manifest for local compatibility")
    check.add_argument("--manifest", required=True, help="Path to manifest JSON file")
    check.add_argument("--json-out", help="Optional path for JSON output")

    apply = sub.add_parser("apply", help="Apply local patch bundle")
    apply.add_argument("--bundle", required=True, help="Path to patch bundle (zip/file)")
    apply.add_argument("--target-version", required=True, help="Target version label")
    apply.add_argument("--json-out", help="Optional path for JSON output")

    verify = sub.add_parser("post-verify", help="Run post-update readiness verification")
    verify.add_argument("--json-out", help="Optional path for JSON output")

    args = parser.parse_args(argv)

    config = load_config()
    service = UpdateService(config)

    if args.command == "check":
        result = service.check_for_update(Path(args.manifest))
        _print_json(result)
        _write_json(Path(args.json_out) if args.json_out else None, result)
        return 0 if bool(result.get("is_compatible")) else 1

    if args.command == "apply":
        bundle = PatchBundle(bundle_path=Path(args.bundle), target_version=args.target_version)
        result = service.apply_local_patch(bundle).model_dump(mode="json")
        _print_json(result)
        _write_json(Path(args.json_out) if args.json_out else None, result)
        return 0 if str(result.get("status")) == "applied" else 1

    if args.command == "post-verify":
        result = service.post_update_verification()
        _print_json(result)
        _write_json(Path(args.json_out) if args.json_out else None, result)
        return 0 if str(result.get("status")) == "PASS" else 1

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
