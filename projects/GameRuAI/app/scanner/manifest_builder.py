from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Any


def build_manifest(root: Path, files: list[dict[str, Any]]) -> dict[str, Any]:
    by_type = Counter(item["file_type"] for item in files)
    by_ext = Counter(item["file_ext"] for item in files)
    groups = Counter(item["manifest_group"] for item in files)
    return {
        "root": str(root),
        "files_total": len(files),
        "by_type": dict(sorted(by_type.items())),
        "by_extension": dict(sorted(by_ext.items())),
        "by_group": dict(sorted(groups.items())),
        "files": files,
    }
