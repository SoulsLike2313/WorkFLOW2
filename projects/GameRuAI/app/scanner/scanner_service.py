from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from app.core.models import ScannedFile
from app.storage.repositories import RepositoryHub

from .file_classifier import classify_file
from .manifest_builder import build_manifest


def _sha1(path: Path) -> str:
    hasher = hashlib.sha1()
    with path.open("rb") as fh:
        while True:
            chunk = fh.read(8192)
            if not chunk:
                break
            hasher.update(chunk)
    return hasher.hexdigest()


class ScannerService:
    def __init__(self, repo: RepositoryHub):
        self.repo = repo

    def scan(self, project_id: int, game_root: Path) -> dict[str, Any]:
        files: list[ScannedFile] = []
        for path in sorted(game_root.rglob("*")):
            if not path.is_file():
                continue
            file_type, file_ext = classify_file(path)
            rel = path.relative_to(game_root).as_posix()
            group = rel.split("/", 1)[0] if "/" in rel else "root"
            files.append(
                ScannedFile(
                    project_id=project_id,
                    file_path=rel,
                    file_type=file_type,
                    file_ext=file_ext,
                    size_bytes=path.stat().st_size,
                    sha1=_sha1(path),
                    manifest_group=group,
                )
            )

        self.repo.add_scanned_files(files)
        simple_files = [
            {
                "file_path": item.file_path,
                "file_type": item.file_type,
                "file_ext": item.file_ext,
                "size_bytes": item.size_bytes,
                "sha1": item.sha1,
                "manifest_group": item.manifest_group,
            }
            for item in files
        ]
        manifest = build_manifest(game_root, simple_files)
        return manifest
