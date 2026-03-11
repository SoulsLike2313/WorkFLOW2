from __future__ import annotations

import json
from pathlib import Path

from app.core.models import ExportResult
from app.storage.repositories import RepositoryHub

from .diff_report import build_diff_report
from .manifest import build_export_manifest


class Exporter:
    def __init__(self, repo: RepositoryHub):
        self.repo = repo

    def export(self, project_id: int, output_dir: Path) -> ExportResult:
        output_dir.mkdir(parents=True, exist_ok=True)
        patch_dir = output_dir / "patch"
        patch_dir.mkdir(parents=True, exist_ok=True)

        translations = self.repo.list_translations(project_id)
        voice_attempts = self.repo.list_voice_attempts(project_id)

        grouped: dict[str, list[dict]] = {}
        for row in translations:
            grouped.setdefault(row["file_path"], []).append(
                {
                    "line_id": row["line_id"],
                    "speaker_id": row.get("speaker_id"),
                    "source_text": row["source_text"],
                    "translated_text": row["translated_text"],
                    "source_lang": row["source_lang"],
                    "quality_score": row["quality_score"],
                    "backend": row["backend"],
                }
            )

        for rel_path, lines in grouped.items():
            out_name = rel_path.replace("/", "__").replace(".", "_")
            patch_path = patch_dir / f"{out_name}.ru_patch.json"
            patch_path.write_text(json.dumps(lines, ensure_ascii=False, indent=2), encoding="utf-8")

        manifest = build_export_manifest(
            project_id=project_id,
            translated_entries=len(translations),
            voiced_entries=len(voice_attempts),
            output_dir=str(output_dir),
        )
        manifest_path = output_dir / "export_manifest.json"
        manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

        report = build_diff_report(translated=translations, voice_attempts=voice_attempts)
        diff_report_path = output_dir / "diff_report.md"
        diff_report_path.write_text(report, encoding="utf-8")

        return ExportResult(
            output_dir=output_dir,
            manifest_path=manifest_path,
            diff_report_path=diff_report_path,
            translated_entries=len(translations),
            voiced_entries=len(voice_attempts),
        )
