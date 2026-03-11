from __future__ import annotations

import json
from dataclasses import asdict
from datetime import datetime, timezone
from typing import Any

from app.assets.preview_models import ArchiveReportRecord, AssetIndexRecord, AssetPreviewRecord
from app.core.enums import QaSeverity, TranslationStatus
from app.core.models import (
    ExtractionRecord,
    Project,
    QaFinding,
    ScannedFile,
    TranslationDecision,
    VoiceAttempt,
)

from .db import Database


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class RepositoryHub:
    def __init__(self, db: Database):
        self.db = db

    def ensure_project(self, name: str, game_path: str) -> Project:
        row = self.db.query_one(
            "SELECT id, name, game_path FROM projects WHERE name=? AND game_path=?",
            (name, game_path),
        )
        if row:
            return Project(id=int(row["id"]), name=row["name"], game_path=row["game_path"])
        project_id = self.db.execute(
            "INSERT INTO projects(name, game_path, created_at, updated_at) VALUES(?,?,?,?)",
            (name, game_path, _now_iso(), _now_iso()),
        )
        return Project(id=project_id, name=name, game_path=game_path)

    def list_projects(self) -> list[Project]:
        rows = self.db.query("SELECT id, name, game_path FROM projects ORDER BY id DESC")
        return [Project(id=int(r["id"]), name=r["name"], game_path=r["game_path"]) for r in rows]

    def clear_project_runtime(self, project_id: int) -> None:
        tables = [
            "scanned_files",
            "asset_previews",
            "archive_reports",
            "asset_index",
            "translations",
            "translation_backend_runs",
            "backend_diagnostics",
            "language_reports",
            "quality_snapshots",
            "project_reports",
            "language_detections",
            "voice_links",
            "voice_attempt_history",
            "voice_sample_bank",
            "speaker_groups",
            "voice_attempts",
            "qa_findings",
            "correction_history",
            "adaptation_events",
            "extracted_entries",
            "export_jobs",
        ]
        with self.db.transaction() as cur:
            for table in tables:
                cur.execute(f"DELETE FROM {table} WHERE project_id=?", (project_id,))

    def add_scanned_files(self, files: list[ScannedFile]) -> None:
        payload = [
            (
                item.project_id,
                item.file_path,
                item.file_type,
                item.file_ext,
                item.size_bytes,
                item.sha1,
                item.manifest_group,
                _now_iso(),
            )
            for item in files
        ]
        self.db.executemany(
            """
            INSERT INTO scanned_files(
              project_id, file_path, file_type, file_ext, size_bytes, sha1, manifest_group, created_at
            ) VALUES(?,?,?,?,?,?,?,?)
            """,
            payload,
        )

    def upsert_scanned_file(self, scanned_file: ScannedFile) -> None:
        with self.db.transaction() as cur:
            cur.execute(
                "DELETE FROM scanned_files WHERE project_id=? AND file_path=?",
                (scanned_file.project_id, scanned_file.file_path),
            )
            cur.execute(
                """
                INSERT INTO scanned_files(
                  project_id, file_path, file_type, file_ext, size_bytes, sha1, manifest_group, created_at
                ) VALUES(?,?,?,?,?,?,?,?)
                """,
                (
                    scanned_file.project_id,
                    scanned_file.file_path,
                    scanned_file.file_type,
                    scanned_file.file_ext,
                    scanned_file.size_bytes,
                    scanned_file.sha1,
                    scanned_file.manifest_group,
                    _now_iso(),
                ),
            )

    def list_scanned_files(self, project_id: int) -> list[dict[str, Any]]:
        rows = self.db.query(
            """
            SELECT file_path, file_type, file_ext, size_bytes, sha1, manifest_group, created_at
            FROM scanned_files
            WHERE project_id=?
            ORDER BY file_path
            """,
            (project_id,),
        )
        return [dict(r) for r in rows]

    def add_extracted_entries(self, entries: list[ExtractionRecord]) -> int:
        count = 0
        with self.db.transaction() as cur:
            for item in entries:
                cur.execute(
                    """
                    INSERT OR REPLACE INTO extracted_entries(
                      project_id, line_id, file_path, speaker_id, source_text, context_type,
                      tags_json, placeholders_json, voice_link, metadata_json, created_at
                    ) VALUES(?,?,?,?,?,?,?,?,?,?,?)
                    """,
                    (
                        item.project_id,
                        item.line_id,
                        item.file_path,
                        item.speaker_id,
                        item.source_text,
                        item.context_type,
                        json.dumps(item.tags, ensure_ascii=False),
                        json.dumps(item.placeholders, ensure_ascii=False),
                        item.voice_link,
                        json.dumps(item.metadata, ensure_ascii=False),
                        _now_iso(),
                    ),
                )
                count += 1

            cur.execute(
                """
                INSERT OR REPLACE INTO voice_links(entry_id, project_id, speaker_id, source_voice_path, text_voice_key, created_at)
                SELECT id, project_id, speaker_id, voice_link, line_id, ?
                FROM extracted_entries
                WHERE project_id=? AND voice_link IS NOT NULL AND TRIM(voice_link) <> ''
                """,
                (_now_iso(), entries[0].project_id if entries else -1),
            )
        return count

    def list_entries(
        self,
        project_id: int,
        *,
        language: str | None = None,
        search: str | None = None,
        limit: int = 2000,
    ) -> list[dict[str, Any]]:
        query = """
            SELECT
              e.id,
              e.line_id,
              e.file_path,
              e.speaker_id,
              e.source_text,
              e.context_type,
              e.tags_json,
              e.placeholders_json,
              e.voice_link,
              l.detected_lang,
              l.confidence AS language_confidence,
              t.translated_text,
              t.translation_status,
              t.quality_score,
              t.glossary_hits_json,
              t.tm_hits_json,
              t.backend,
              t.fallback_backend,
              t.context_used,
              t.latency_ms,
              t.uncertainty,
              CASE WHEN e.voice_link IS NULL OR TRIM(e.voice_link)='' THEN 0 ELSE 1 END AS has_voice_link,
              COALESCE(v.status, 'pending') AS voice_status
            FROM extracted_entries e
            LEFT JOIN language_detections l ON l.entry_id = e.id
            LEFT JOIN translations t ON t.entry_id = e.id
            LEFT JOIN (
              SELECT entry_id, status, MAX(updated_at) AS updated_at
              FROM voice_attempts
              GROUP BY entry_id
            ) v ON v.entry_id = e.id
            WHERE e.project_id = ?
        """
        params: list[Any] = [project_id]
        if language:
            query += " AND l.detected_lang = ?"
            params.append(language)
        if search:
            query += " AND (e.source_text LIKE ? OR e.line_id LIKE ? OR e.file_path LIKE ?)"
            pattern = f"%{search}%"
            params.extend([pattern, pattern, pattern])
        query += " ORDER BY e.id LIMIT ?"
        params.append(limit)
        rows = self.db.query(query, tuple(params))
        parsed: list[dict[str, Any]] = []
        for row in rows:
            item = dict(row)
            for key in ("tags_json", "placeholders_json", "glossary_hits_json", "tm_hits_json"):
                if item.get(key):
                    try:
                        item[key] = json.loads(item[key])
                    except json.JSONDecodeError:
                        item[key] = []
                else:
                    item[key] = []
            item["context_used"] = bool(item.get("context_used"))
            parsed.append(item)
        return parsed

    def get_entry(self, entry_id: int) -> dict[str, Any] | None:
        row = self.db.query_one(
            """
            SELECT
              e.*,
              l.detected_lang,
              l.confidence,
              t.translated_text,
              t.translation_status,
              t.backend,
              t.fallback_backend,
              t.context_used
            FROM extracted_entries e
            LEFT JOIN language_detections l ON l.entry_id = e.id
            LEFT JOIN translations t ON t.entry_id = e.id
            WHERE e.id=?
            """,
            (entry_id,),
        )
        return dict(row) if row else None

    def clear_entries_for_file(self, project_id: int, file_path: str) -> None:
        self.db.execute(
            "DELETE FROM extracted_entries WHERE project_id=? AND file_path=?",
            (project_id, file_path),
        )

    def get_neighbor_texts(self, project_id: int, entry_id: int, window: int = 1) -> list[str]:
        entry = self.get_entry(entry_id)
        if not entry:
            return []
        file_path = str(entry.get("file_path") or "")
        start_id = max(1, entry_id - window)
        end_id = entry_id + window
        rows = self.db.query(
            """
            SELECT id, source_text
            FROM extracted_entries
            WHERE project_id=? AND file_path=? AND id BETWEEN ? AND ? AND id<>?
            ORDER BY id
            """,
            (project_id, file_path, start_id, end_id, entry_id),
        )
        return [str(row["source_text"]) for row in rows]

    def upsert_language_detection(
        self, entry_id: int, project_id: int, detected_lang: str, confidence: float, heuristics: dict[str, Any]
    ) -> None:
        self.db.execute(
            """
            INSERT INTO language_detections(entry_id, project_id, detected_lang, confidence, heuristics_json, created_at)
            VALUES(?,?,?,?,?,?)
            ON CONFLICT(entry_id) DO UPDATE SET
              detected_lang=excluded.detected_lang,
              confidence=excluded.confidence,
              heuristics_json=excluded.heuristics_json
            """,
            (entry_id, project_id, detected_lang, confidence, json.dumps(heuristics, ensure_ascii=False), _now_iso()),
        )

    def upsert_translation(self, project_id: int, decision: TranslationDecision) -> None:
        self.db.execute(
            """
            INSERT INTO translations(
              entry_id, project_id, source_lang, translated_text, translation_status,
              glossary_hits_json, tm_hits_json, quality_score, latency_ms, backend, fallback_backend, context_used,
              uncertainty, decision_log_json,
              created_at, updated_at
            ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            ON CONFLICT(entry_id) DO UPDATE SET
              source_lang=excluded.source_lang,
              translated_text=excluded.translated_text,
              translation_status=excluded.translation_status,
              glossary_hits_json=excluded.glossary_hits_json,
              tm_hits_json=excluded.tm_hits_json,
              quality_score=excluded.quality_score,
              latency_ms=excluded.latency_ms,
              backend=excluded.backend,
              fallback_backend=excluded.fallback_backend,
              context_used=excluded.context_used,
              uncertainty=excluded.uncertainty,
              decision_log_json=excluded.decision_log_json,
              updated_at=excluded.updated_at
            """,
            (
                decision.entry_id,
                project_id,
                decision.source_lang,
                decision.translated_text,
                decision.status.value,
                json.dumps(decision.glossary_hits, ensure_ascii=False),
                json.dumps(decision.tm_hits, ensure_ascii=False),
                decision.quality_score,
                decision.latency_ms,
                decision.backend,
                decision.fallback_backend,
                int(decision.context_used),
                decision.uncertainty,
                json.dumps(decision.decision_log, ensure_ascii=False),
                _now_iso(),
                _now_iso(),
            ),
        )

    def list_translations(self, project_id: int) -> list[dict[str, Any]]:
        rows = self.db.query(
            """
            SELECT t.*, e.line_id, e.file_path, e.source_text, e.speaker_id
            FROM translations t
            JOIN extracted_entries e ON e.id=t.entry_id
            WHERE t.project_id=?
            ORDER BY e.id
            """,
            (project_id,),
        )
        out: list[dict[str, Any]] = []
        for row in rows:
            item = dict(row)
            for key in ("glossary_hits_json", "tm_hits_json", "decision_log_json"):
                try:
                    item[key] = json.loads(item[key] or "[]")
                except json.JSONDecodeError:
                    item[key] = []
            item["context_used"] = bool(item.get("context_used"))
            out.append(item)
        return out

    def upsert_glossary_term(
        self,
        project_id: int,
        source_term: str,
        target_term: str,
        source_lang: str,
        *,
        case_sensitive: bool = False,
        priority: int = 100,
    ) -> None:
        self.db.execute(
            """
            INSERT INTO glossary_terms(
              project_id, source_term, target_term, source_lang, case_sensitive, priority, created_at, updated_at
            ) VALUES(?,?,?,?,?,?,?,?)
            ON CONFLICT(project_id, source_term, source_lang) DO UPDATE SET
              target_term=excluded.target_term,
              case_sensitive=excluded.case_sensitive,
              priority=excluded.priority,
              updated_at=excluded.updated_at
            """,
            (
                project_id,
                source_term,
                target_term,
                source_lang,
                int(case_sensitive),
                priority,
                _now_iso(),
                _now_iso(),
            ),
        )

    def list_glossary_terms(self, project_id: int) -> list[dict[str, Any]]:
        rows = self.db.query(
            """
            SELECT id, source_term, target_term, source_lang, case_sensitive, priority, updated_at
            FROM glossary_terms
            WHERE project_id=?
            ORDER BY priority ASC, source_term ASC
            """,
            (project_id,),
        )
        return [dict(r) for r in rows]

    def add_translation_memory(
        self, project_id: int, source_text: str, target_text: str, source_lang: str, quality_score: float
    ) -> None:
        existing = self.db.query_one(
            """
            SELECT id, use_count FROM translation_memory
            WHERE project_id=? AND source_text=? AND source_lang=?
            ORDER BY id DESC LIMIT 1
            """,
            (project_id, source_text, source_lang),
        )
        if existing:
            self.db.execute(
                """
                UPDATE translation_memory
                SET target_text=?, quality_score=?, use_count=?, last_used_at=?, updated_at=?
                WHERE id=?
                """,
                (
                    target_text,
                    quality_score,
                    int(existing["use_count"]) + 1,
                    _now_iso(),
                    _now_iso(),
                    int(existing["id"]),
                ),
            )
            return
        self.db.execute(
            """
            INSERT INTO translation_memory(
              project_id, source_text, target_text, source_lang, quality_score, use_count, last_used_at, created_at, updated_at
            ) VALUES(?,?,?,?,?,?,?,?,?)
            """,
            (project_id, source_text, target_text, source_lang, quality_score, 1, _now_iso(), _now_iso(), _now_iso()),
        )

    def list_translation_memory(self, project_id: int, source_lang: str | None = None) -> list[dict[str, Any]]:
        query = """
            SELECT id, source_text, target_text, source_lang, quality_score, use_count, last_used_at
            FROM translation_memory
            WHERE project_id=?
        """
        params: list[Any] = [project_id]
        if source_lang:
            query += " AND source_lang=?"
            params.append(source_lang)
        query += " ORDER BY quality_score DESC, use_count DESC"
        rows = self.db.query(query, tuple(params))
        return [dict(r) for r in rows]

    def mark_tm_used(self, tm_id: int) -> None:
        self.db.execute(
            """
            UPDATE translation_memory
            SET use_count=use_count+1, last_used_at=?, updated_at=?
            WHERE id=?
            """,
            (_now_iso(), _now_iso(), tm_id),
        )

    def add_correction_history(
        self, project_id: int, entry_id: int, before_text: str, after_text: str, user_note: str | None
    ) -> None:
        self.db.execute(
            """
            INSERT INTO correction_history(entry_id, project_id, before_text, after_text, user_note, created_at)
            VALUES(?,?,?,?,?,?)
            """,
            (entry_id, project_id, before_text, after_text, user_note, _now_iso()),
        )

    def list_corrections(self, project_id: int, limit: int = 200) -> list[dict[str, Any]]:
        rows = self.db.query(
            """
            SELECT c.id, c.entry_id, c.before_text, c.after_text, c.user_note, c.created_at, e.line_id, e.source_text
            FROM correction_history c
            JOIN extracted_entries e ON e.id=c.entry_id
            WHERE c.project_id=?
            ORDER BY c.id DESC
            LIMIT ?
            """,
            (project_id, limit),
        )
        return [dict(r) for r in rows]

    def add_adaptation_event(
        self, project_id: int, event_type: str, event_scope: str, event_ref: str, details: dict[str, Any]
    ) -> None:
        self.db.execute(
            """
            INSERT INTO adaptation_events(project_id, event_type, event_scope, event_ref, details_json, created_at)
            VALUES(?,?,?,?,?,?)
            """,
            (project_id, event_type, event_scope, event_ref, json.dumps(details, ensure_ascii=False), _now_iso()),
        )

    def list_adaptation_events(self, project_id: int, limit: int = 200) -> list[dict[str, Any]]:
        rows = self.db.query(
            """
            SELECT id, event_type, event_scope, event_ref, details_json, created_at
            FROM adaptation_events
            WHERE project_id=?
            ORDER BY id DESC
            LIMIT ?
            """,
            (project_id, limit),
        )
        out: list[dict[str, Any]] = []
        for row in rows:
            item = dict(row)
            try:
                item["details_json"] = json.loads(item["details_json"] or "{}")
            except json.JSONDecodeError:
                item["details_json"] = {}
            out.append(item)
        return out

    def list_learning_improvements(self, project_id: int, limit: int = 200) -> list[dict[str, Any]]:
        rows = self.db.query(
            """
            SELECT
              e.id AS entry_id,
              e.line_id,
              e.source_text,
              t.translated_text,
              t.backend,
              t.translation_status,
              t.tm_hits_json,
              t.glossary_hits_json,
              t.quality_score,
              t.updated_at
            FROM translations t
            JOIN extracted_entries e ON e.id=t.entry_id
            WHERE t.project_id=?
              AND (
                t.backend='translation_memory'
                OR t.tm_hits_json <> '[]'
                OR t.glossary_hits_json <> '[]'
                OR t.translation_status='corrected'
              )
            ORDER BY t.updated_at DESC
            LIMIT ?
            """,
            (project_id, limit),
        )
        out: list[dict[str, Any]] = []
        for row in rows:
            item = dict(row)
            try:
                item["tm_hits_json"] = json.loads(item["tm_hits_json"] or "[]")
            except json.JSONDecodeError:
                item["tm_hits_json"] = []
            try:
                item["glossary_hits_json"] = json.loads(item["glossary_hits_json"] or "[]")
            except json.JSONDecodeError:
                item["glossary_hits_json"] = []
            out.append(item)
        return out

    def upsert_voice_profile(self, project_id: int, speaker_id: str, profile: dict[str, Any]) -> None:
        self.db.execute(
            """
            INSERT INTO voice_profiles(project_id, speaker_id, profile_json, updated_at)
            VALUES(?,?,?,?)
            ON CONFLICT(project_id, speaker_id) DO UPDATE SET
              profile_json=excluded.profile_json,
              updated_at=excluded.updated_at
            """,
            (project_id, speaker_id, json.dumps(profile, ensure_ascii=False), _now_iso()),
        )

    def list_voice_profiles(self, project_id: int) -> dict[str, dict[str, Any]]:
        rows = self.db.query(
            "SELECT speaker_id, profile_json FROM voice_profiles WHERE project_id=?",
            (project_id,),
        )
        out: dict[str, dict[str, Any]] = {}
        for row in rows:
            try:
                out[row["speaker_id"]] = json.loads(row["profile_json"] or "{}")
            except json.JSONDecodeError:
                out[row["speaker_id"]] = {}
        return out

    def replace_speaker_groups(self, project_id: int, groups: list[dict[str, Any]]) -> None:
        with self.db.transaction() as cur:
            cur.execute("DELETE FROM speaker_groups WHERE project_id=?", (project_id,))
            for item in groups:
                cur.execute(
                    """
                    INSERT INTO speaker_groups(
                      project_id, speaker_id, group_label, line_count, linked_count, broken_links,
                      scene_count, avg_confidence, metadata_json, updated_at
                    ) VALUES(?,?,?,?,?,?,?,?,?,?)
                    """,
                    (
                        project_id,
                        str(item.get("speaker_id") or "unknown"),
                        str(item.get("group_label") or "speaker:unknown"),
                        int(item.get("line_count") or 0),
                        int(item.get("linked_count") or 0),
                        int(item.get("broken_links") or 0),
                        int(item.get("scene_count") or 0),
                        float(item.get("avg_confidence") or 0.0),
                        json.dumps(
                            {
                                "scene_ids": item.get("scene_ids", []),
                                "linking_strategy": item.get("linking_strategy", "speaker_id+metadata+scene"),
                            },
                            ensure_ascii=False,
                        ),
                        _now_iso(),
                    ),
                )

    def list_speaker_groups(self, project_id: int, limit: int = 200) -> list[dict[str, Any]]:
        rows = self.db.query(
            """
            SELECT id, speaker_id, group_label, line_count, linked_count, broken_links, scene_count,
                   avg_confidence, metadata_json, updated_at
            FROM speaker_groups
            WHERE project_id=?
            ORDER BY line_count DESC, speaker_id ASC
            LIMIT ?
            """,
            (project_id, limit),
        )
        out: list[dict[str, Any]] = []
        for row in rows:
            item = dict(row)
            try:
                item["metadata_json"] = json.loads(item.get("metadata_json") or "{}")
            except json.JSONDecodeError:
                item["metadata_json"] = {}
            out.append(item)
        return out

    def replace_voice_sample_bank(self, project_id: int, samples: list[dict[str, Any]]) -> None:
        with self.db.transaction() as cur:
            cur.execute("DELETE FROM voice_sample_bank WHERE project_id=?", (project_id,))
            for item in samples:
                cur.execute(
                    """
                    INSERT INTO voice_sample_bank(
                      project_id, speaker_id, line_id, scene_id, source_file, source_duration_ms, metadata_json, created_at
                    ) VALUES(?,?,?,?,?,?,?,?)
                    """,
                    (
                        project_id,
                        str(item.get("speaker_id") or "unknown"),
                        str(item.get("line_id") or ""),
                        str(item.get("scene_id") or ""),
                        str(item.get("source_file") or ""),
                        int(item.get("source_duration_ms") or 0),
                        json.dumps(item.get("metadata_json", {}), ensure_ascii=False),
                        _now_iso(),
                    ),
                )

    def list_voice_sample_bank(
        self, project_id: int, *, speaker_id: str | None = None, limit: int = 2000
    ) -> list[dict[str, Any]]:
        query = """
            SELECT id, speaker_id, line_id, scene_id, source_file, source_duration_ms, metadata_json, created_at
            FROM voice_sample_bank
            WHERE project_id=?
        """
        params: list[Any] = [project_id]
        if speaker_id:
            query += " AND speaker_id=?"
            params.append(speaker_id)
        query += " ORDER BY id DESC LIMIT ?"
        params.append(limit)
        rows = self.db.query(query, tuple(params))
        out: list[dict[str, Any]] = []
        for row in rows:
            item = dict(row)
            try:
                item["metadata_json"] = json.loads(item.get("metadata_json") or "{}")
            except json.JSONDecodeError:
                item["metadata_json"] = {}
            out.append(item)
        return out

    def add_voice_attempt(self, project_id: int, attempt: VoiceAttempt) -> None:
        self.db.execute(
            """
            INSERT INTO voice_attempts(
              entry_id, project_id, speaker_id, source_voice_path, output_voice_path, status,
              quality_score, duration_source_ms, duration_output_ms, metadata_json, created_at, updated_at
            ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)
            """,
            (
                attempt.entry_id,
                project_id,
                attempt.speaker_id,
                attempt.source_voice_path,
                attempt.output_voice_path,
                attempt.status.value,
                attempt.quality_score,
                attempt.duration_source_ms,
                attempt.duration_output_ms,
                json.dumps(attempt.metadata, ensure_ascii=False),
                _now_iso(),
                _now_iso(),
            ),
        )

    def list_voice_attempts(self, project_id: int, limit: int = 2000) -> list[dict[str, Any]]:
        rows = self.db.query(
            """
            SELECT v.*, e.line_id, e.source_text, t.translated_text
            FROM voice_attempts v
            JOIN extracted_entries e ON e.id=v.entry_id
            LEFT JOIN translations t ON t.entry_id=e.id
            WHERE v.project_id=?
            ORDER BY v.id DESC
            LIMIT ?
            """,
            (project_id, limit),
        )
        out: list[dict[str, Any]] = []
        for row in rows:
            item = dict(row)
            try:
                item["metadata_json"] = json.loads(item["metadata_json"] or "{}")
            except json.JSONDecodeError:
                item["metadata_json"] = {}
            out.append(item)
        return out

    def add_voice_attempt_history(
        self,
        *,
        project_id: int,
        entry_id: int | None,
        speaker_id: str,
        source_file: str,
        source_duration_ms: int,
        generated_file: str,
        synthesis_mode: str,
        alignment_ratio: float,
        quality_score: float,
        confidence_score: float,
        metadata_json: dict[str, Any],
    ) -> None:
        self.db.execute(
            """
            INSERT INTO voice_attempt_history(
              project_id, entry_id, speaker_id, source_file, source_duration_ms, generated_file, synthesis_mode,
              alignment_ratio, quality_score, confidence_score, metadata_json, created_at
            ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)
            """,
            (
                project_id,
                entry_id,
                speaker_id,
                source_file,
                source_duration_ms,
                generated_file,
                synthesis_mode,
                alignment_ratio,
                quality_score,
                confidence_score,
                json.dumps(metadata_json, ensure_ascii=False),
                _now_iso(),
            ),
        )

    def list_voice_attempt_history(
        self,
        *,
        project_id: int,
        speaker_id: str | None = None,
        limit: int = 500,
    ) -> list[dict[str, Any]]:
        query = """
            SELECT id, entry_id, speaker_id, source_file, source_duration_ms, generated_file, synthesis_mode,
                   alignment_ratio, quality_score, confidence_score, metadata_json, created_at
            FROM voice_attempt_history
            WHERE project_id=?
        """
        params: list[Any] = [project_id]
        if speaker_id:
            query += " AND speaker_id=?"
            params.append(speaker_id)
        query += " ORDER BY id DESC LIMIT ?"
        params.append(limit)
        rows = self.db.query(query, tuple(params))
        out: list[dict[str, Any]] = []
        for row in rows:
            item = dict(row)
            try:
                item["metadata_json"] = json.loads(item.get("metadata_json") or "{}")
            except json.JSONDecodeError:
                item["metadata_json"] = {}
            out.append(item)
        return out

    def replace_qa_findings(self, project_id: int, findings: list[QaFinding]) -> None:
        with self.db.transaction() as cur:
            cur.execute("DELETE FROM qa_findings WHERE project_id=?", (project_id,))
            for finding in findings:
                cur.execute(
                    """
                    INSERT INTO qa_findings(project_id, entry_id, check_name, severity, message, details_json, created_at)
                    VALUES(?,?,?,?,?,?,?)
                    """,
                    (
                        project_id,
                        finding.entry_id,
                        finding.check_name,
                        finding.severity.value,
                        finding.message,
                        json.dumps(finding.details, ensure_ascii=False),
                        _now_iso(),
                    ),
                )

    def list_qa_findings(self, project_id: int, limit: int = 2000) -> list[dict[str, Any]]:
        rows = self.db.query(
            """
            SELECT id, entry_id, check_name, severity, message, details_json, created_at
            FROM qa_findings
            WHERE project_id=?
            ORDER BY id DESC
            LIMIT ?
            """,
            (project_id, limit),
        )
        out: list[dict[str, Any]] = []
        for row in rows:
            item = dict(row)
            try:
                item["details_json"] = json.loads(item["details_json"] or "{}")
            except json.JSONDecodeError:
                item["details_json"] = {}
            out.append(item)
        return out

    def create_export_job(self, project_id: int, output_dir: str) -> int:
        return self.db.execute(
            """
            INSERT INTO export_jobs(project_id, output_dir, status, created_at, updated_at)
            VALUES(?,?,?,?,?)
            """,
            (project_id, output_dir, "running", _now_iso(), _now_iso()),
        )

    def finish_export_job(self, job_id: int, status: str, manifest_path: str, diff_report_path: str) -> None:
        self.db.execute(
            """
            UPDATE export_jobs
            SET status=?, manifest_path=?, diff_report_path=?, updated_at=?
            WHERE id=?
            """,
            (status, manifest_path, diff_report_path, _now_iso(), job_id),
        )

    def list_export_jobs(self, project_id: int, limit: int = 100) -> list[dict[str, Any]]:
        rows = self.db.query(
            """
            SELECT id, output_dir, status, manifest_path, diff_report_path, created_at, updated_at
            FROM export_jobs
            WHERE project_id=?
            ORDER BY id DESC
            LIMIT ?
            """,
            (project_id, limit),
        )
        return [dict(r) for r in rows]

    def add_translation_backend_run(
        self,
        *,
        project_id: int,
        entry_id: int | None,
        requested_backend: str,
        backend_name: str,
        fallback_backend: str | None,
        latency_ms: int,
        context_used: bool,
        fallback_used: bool,
    ) -> None:
        self.db.execute(
            """
            INSERT INTO translation_backend_runs(
              project_id, entry_id, requested_backend, backend_name, fallback_backend,
              latency_ms, context_used, fallback_used, created_at
            ) VALUES(?,?,?,?,?,?,?,?,?)
            """,
            (
                project_id,
                entry_id,
                requested_backend,
                backend_name,
                fallback_backend,
                latency_ms,
                int(context_used),
                int(fallback_used),
                _now_iso(),
            ),
        )

    def list_translation_backend_runs(self, project_id: int, limit: int = 300) -> list[dict[str, Any]]:
        rows = self.db.query(
            """
            SELECT id, entry_id, requested_backend, backend_name, fallback_backend,
                   latency_ms, context_used, fallback_used, created_at
            FROM translation_backend_runs
            WHERE project_id=?
            ORDER BY id DESC
            LIMIT ?
            """,
            (project_id, limit),
        )
        out: list[dict[str, Any]] = []
        for row in rows:
            item = dict(row)
            item["context_used"] = bool(item.get("context_used"))
            item["fallback_used"] = bool(item.get("fallback_used"))
            out.append(item)
        return out

    def upsert_language_report(
        self,
        *,
        project_id: int,
        report_name: str,
        lines_total: int,
        uncertain_count: int,
        uncertain_rate: float,
        payload: dict[str, Any],
    ) -> None:
        self.db.execute(
            """
            INSERT INTO language_reports(
              project_id, report_name, lines_total, uncertain_count, uncertain_rate, payload_json, created_at, updated_at
            ) VALUES(?,?,?,?,?,?,?,?)
            ON CONFLICT(project_id, report_name) DO UPDATE SET
              lines_total=excluded.lines_total,
              uncertain_count=excluded.uncertain_count,
              uncertain_rate=excluded.uncertain_rate,
              payload_json=excluded.payload_json,
              updated_at=excluded.updated_at
            """,
            (
                project_id,
                report_name,
                lines_total,
                uncertain_count,
                uncertain_rate,
                json.dumps(payload, ensure_ascii=False),
                _now_iso(),
                _now_iso(),
            ),
        )

    def list_language_reports(self, project_id: int, limit: int = 100) -> list[dict[str, Any]]:
        rows = self.db.query(
            """
            SELECT id, report_name, lines_total, uncertain_count, uncertain_rate, payload_json, created_at, updated_at
            FROM language_reports
            WHERE project_id=?
            ORDER BY updated_at DESC
            LIMIT ?
            """,
            (project_id, limit),
        )
        out: list[dict[str, Any]] = []
        for row in rows:
            item = dict(row)
            try:
                item["payload_json"] = json.loads(item.get("payload_json") or "{}")
            except json.JSONDecodeError:
                item["payload_json"] = {}
            out.append(item)
        return out

    def replace_backend_diagnostics(self, project_id: int, rows: list[dict[str, Any]]) -> None:
        with self.db.transaction() as cur:
            cur.execute("DELETE FROM backend_diagnostics WHERE project_id=?", (project_id,))
            for item in rows:
                cur.execute(
                    """
                    INSERT INTO backend_diagnostics(
                      project_id, backend_name, runs_count, avg_latency_ms, p95_latency_ms,
                      fallback_count, context_used_rate, payload_json, created_at
                    ) VALUES(?,?,?,?,?,?,?,?,?)
                    """,
                    (
                        project_id,
                        str(item.get("backend_name") or "unknown"),
                        int(item.get("runs_count") or 0),
                        float(item.get("avg_latency_ms") or 0.0),
                        float(item.get("p95_latency_ms") or 0.0),
                        int(item.get("fallback_count") or 0),
                        float(item.get("context_used_rate") or 0.0),
                        json.dumps(item, ensure_ascii=False),
                        _now_iso(),
                    ),
                )

    def list_backend_diagnostics(self, project_id: int, limit: int = 100) -> list[dict[str, Any]]:
        rows = self.db.query(
            """
            SELECT id, backend_name, runs_count, avg_latency_ms, p95_latency_ms, fallback_count,
                   context_used_rate, payload_json, created_at
            FROM backend_diagnostics
            WHERE project_id=?
            ORDER BY runs_count DESC, backend_name ASC
            LIMIT ?
            """,
            (project_id, limit),
        )
        out: list[dict[str, Any]] = []
        for row in rows:
            item = dict(row)
            try:
                item["payload_json"] = json.loads(item.get("payload_json") or "{}")
            except json.JSONDecodeError:
                item["payload_json"] = {}
            out.append(item)
        return out

    def add_project_report(self, *, project_id: int, report_type: str, payload: dict[str, Any]) -> None:
        self.db.execute(
            """
            INSERT INTO project_reports(project_id, report_type, payload_json, created_at)
            VALUES(?,?,?,?)
            """,
            (project_id, report_type, json.dumps(payload, ensure_ascii=False), _now_iso()),
        )

    def list_project_reports(self, project_id: int, report_type: str | None = None, limit: int = 100) -> list[dict[str, Any]]:
        query = """
            SELECT id, report_type, payload_json, created_at
            FROM project_reports
            WHERE project_id=?
        """
        params: list[Any] = [project_id]
        if report_type:
            query += " AND report_type=?"
            params.append(report_type)
        query += " ORDER BY id DESC LIMIT ?"
        params.append(limit)
        rows = self.db.query(query, tuple(params))
        out: list[dict[str, Any]] = []
        for row in rows:
            item = dict(row)
            try:
                item["payload_json"] = json.loads(item.get("payload_json") or "{}")
            except json.JSONDecodeError:
                item["payload_json"] = {}
            out.append(item)
        return out

    def add_quality_snapshot(self, *, project_id: int, snapshot_type: str, payload: dict[str, Any]) -> None:
        self.db.execute(
            """
            INSERT INTO quality_snapshots(project_id, snapshot_type, payload_json, created_at)
            VALUES(?,?,?,?)
            """,
            (project_id, snapshot_type, json.dumps(payload, ensure_ascii=False), _now_iso()),
        )

    def list_quality_snapshots(self, project_id: int, snapshot_type: str | None = None, limit: int = 100) -> list[dict[str, Any]]:
        query = """
            SELECT id, snapshot_type, payload_json, created_at
            FROM quality_snapshots
            WHERE project_id=?
        """
        params: list[Any] = [project_id]
        if snapshot_type:
            query += " AND snapshot_type=?"
            params.append(snapshot_type)
        query += " ORDER BY id DESC LIMIT ?"
        params.append(limit)
        rows = self.db.query(query, tuple(params))
        out: list[dict[str, Any]] = []
        for row in rows:
            item = dict(row)
            try:
                item["payload_json"] = json.loads(item.get("payload_json") or "{}")
            except json.JSONDecodeError:
                item["payload_json"] = {}
            out.append(item)
        return out

    def create_companion_session(
        self,
        *,
        project_id: int,
        session_id: str,
        executable_path: str,
        watched_path: str,
        process_status: str,
        process_pid: int | None,
    ) -> None:
        self.db.execute(
            """
            INSERT INTO companion_sessions(
              project_id, session_id, executable_path, watched_path, process_pid, process_status, started_at, ended_at
            ) VALUES(?,?,?,?,?,?,?,NULL)
            """,
            (project_id, session_id, executable_path, watched_path, process_pid, process_status, _now_iso()),
        )

    def update_companion_session(
        self,
        *,
        session_id: str,
        process_status: str,
        process_pid: int | None = None,
        ended: bool = False,
    ) -> None:
        if ended:
            self.db.execute(
                """
                UPDATE companion_sessions
                SET process_status=?, process_pid=?, ended_at=?
                WHERE session_id=?
                """,
                (process_status, process_pid, _now_iso(), session_id),
            )
            return
        self.db.execute(
            """
            UPDATE companion_sessions
            SET process_status=?, process_pid=COALESCE(?, process_pid)
            WHERE session_id=?
            """,
            (process_status, process_pid, session_id),
        )

    def get_companion_session(self, session_id: str) -> dict[str, Any] | None:
        row = self.db.query_one(
            """
            SELECT id, project_id, session_id, executable_path, watched_path, process_pid, process_status, started_at, ended_at
            FROM companion_sessions
            WHERE session_id=?
            """,
            (session_id,),
        )
        return dict(row) if row else None

    def list_companion_sessions(self, project_id: int, limit: int = 100) -> list[dict[str, Any]]:
        rows = self.db.query(
            """
            SELECT id, project_id, session_id, executable_path, watched_path, process_pid, process_status, started_at, ended_at
            FROM companion_sessions
            WHERE project_id=?
            ORDER BY id DESC
            LIMIT ?
            """,
            (project_id, limit),
        )
        return [dict(row) for row in rows]

    def add_watched_file_event(
        self,
        *,
        project_id: int,
        session_id: str,
        watched_path: str,
        event_type: str,
        file_path: str,
    ) -> None:
        self.db.execute(
            """
            INSERT INTO watched_file_events(project_id, session_id, watched_path, event_type, file_path, created_at)
            VALUES(?,?,?,?,?,?)
            """,
            (project_id, session_id, watched_path, event_type, file_path, _now_iso()),
        )

    def list_watched_file_events(
        self, project_id: int, session_id: str | None = None, limit: int = 300
    ) -> list[dict[str, Any]]:
        query = """
            SELECT id, project_id, session_id, watched_path, event_type, file_path, created_at
            FROM watched_file_events
            WHERE project_id=?
        """
        params: list[Any] = [project_id]
        if session_id:
            query += " AND session_id=?"
            params.append(session_id)
        query += " ORDER BY id DESC LIMIT ?"
        params.append(limit)
        rows = self.db.query(query, tuple(params))
        return [dict(row) for row in rows]

    def clear_asset_research(self, project_id: int) -> None:
        with self.db.transaction() as cur:
            cur.execute("DELETE FROM asset_previews WHERE project_id=?", (project_id,))
            cur.execute("DELETE FROM archive_reports WHERE project_id=?", (project_id,))
            cur.execute("DELETE FROM asset_index WHERE project_id=?", (project_id,))

    def upsert_asset_index(self, item: AssetIndexRecord) -> None:
        self.db.execute(
            """
            INSERT INTO asset_index(
              project_id, file_path, asset_type, preview_type, preview_status,
              metadata_json, suspected_container, relevance_score, updated_at
            ) VALUES(?,?,?,?,?,?,?,?,?)
            ON CONFLICT(project_id, file_path) DO UPDATE SET
              asset_type=excluded.asset_type,
              preview_type=excluded.preview_type,
              preview_status=excluded.preview_status,
              metadata_json=excluded.metadata_json,
              suspected_container=excluded.suspected_container,
              relevance_score=excluded.relevance_score,
              updated_at=excluded.updated_at
            """,
            (
                item.project_id,
                item.file_path,
                item.asset_type,
                item.preview_type,
                item.preview_status,
                json.dumps(item.metadata, ensure_ascii=False),
                int(item.suspected_container),
                float(item.relevance_score),
                _now_iso(),
            ),
        )

    def upsert_asset_preview(self, item: AssetPreviewRecord) -> None:
        self.db.execute(
            """
            INSERT INTO asset_previews(
              project_id, file_path, preview_type, preview_status, preview_path, metadata_json, updated_at
            ) VALUES(?,?,?,?,?,?,?)
            ON CONFLICT(project_id, file_path, preview_type) DO UPDATE SET
              preview_status=excluded.preview_status,
              preview_path=excluded.preview_path,
              metadata_json=excluded.metadata_json,
              updated_at=excluded.updated_at
            """,
            (
                item.project_id,
                item.file_path,
                item.preview_type,
                item.preview_status,
                item.preview_path,
                json.dumps(item.metadata, ensure_ascii=False),
                _now_iso(),
            ),
        )

    def upsert_archive_report(self, item: ArchiveReportRecord) -> None:
        self.db.execute(
            """
            INSERT INTO archive_reports(
              project_id, file_path, suspected_container, confidence, reason, metadata_json, updated_at
            ) VALUES(?,?,?,?,?,?,?)
            ON CONFLICT(project_id, file_path) DO UPDATE SET
              suspected_container=excluded.suspected_container,
              confidence=excluded.confidence,
              reason=excluded.reason,
              metadata_json=excluded.metadata_json,
              updated_at=excluded.updated_at
            """,
            (
                item.project_id,
                item.file_path,
                int(item.suspected_container),
                float(item.confidence),
                item.reason,
                json.dumps(item.metadata, ensure_ascii=False),
                _now_iso(),
            ),
        )

    def list_asset_index(self, project_id: int, limit: int = 3000) -> list[dict[str, Any]]:
        rows = self.db.query(
            """
            SELECT id, project_id, file_path, asset_type, preview_type, preview_status,
                   metadata_json, suspected_container, relevance_score, updated_at
            FROM asset_index
            WHERE project_id=?
            ORDER BY relevance_score DESC, file_path ASC
            LIMIT ?
            """,
            (project_id, limit),
        )
        out: list[dict[str, Any]] = []
        for row in rows:
            item = dict(row)
            try:
                item["metadata_json"] = json.loads(item.get("metadata_json") or "{}")
            except json.JSONDecodeError:
                item["metadata_json"] = {}
            item["suspected_container"] = bool(item.get("suspected_container"))
            out.append(item)
        return out

    def get_asset_index(self, project_id: int, file_path: str) -> dict[str, Any] | None:
        row = self.db.query_one(
            """
            SELECT id, project_id, file_path, asset_type, preview_type, preview_status,
                   metadata_json, suspected_container, relevance_score, updated_at
            FROM asset_index
            WHERE project_id=? AND file_path=?
            """,
            (project_id, file_path),
        )
        if not row:
            return None
        item = dict(row)
        try:
            item["metadata_json"] = json.loads(item.get("metadata_json") or "{}")
        except json.JSONDecodeError:
            item["metadata_json"] = {}
        item["suspected_container"] = bool(item.get("suspected_container"))
        return item

    def get_asset_preview(self, project_id: int, file_path: str) -> dict[str, Any] | None:
        row = self.db.query_one(
            """
            SELECT id, project_id, file_path, preview_type, preview_status, preview_path, metadata_json, updated_at
            FROM asset_previews
            WHERE project_id=? AND file_path=?
            ORDER BY id DESC
            LIMIT 1
            """,
            (project_id, file_path),
        )
        if not row:
            return None
        item = dict(row)
        try:
            item["metadata_json"] = json.loads(item.get("metadata_json") or "{}")
        except json.JSONDecodeError:
            item["metadata_json"] = {}
        return item

    def list_archive_reports(
        self,
        project_id: int,
        *,
        suspected_only: bool = False,
        limit: int = 1000,
    ) -> list[dict[str, Any]]:
        query = """
            SELECT id, project_id, file_path, suspected_container, confidence, reason, metadata_json, updated_at
            FROM archive_reports
            WHERE project_id=?
        """
        params: list[Any] = [project_id]
        if suspected_only:
            query += " AND suspected_container=1"
        query += " ORDER BY suspected_container DESC, confidence DESC, file_path ASC LIMIT ?"
        params.append(limit)
        rows = self.db.query(query, tuple(params))
        out: list[dict[str, Any]] = []
        for row in rows:
            item = dict(row)
            try:
                item["metadata_json"] = json.loads(item.get("metadata_json") or "{}")
            except json.JSONDecodeError:
                item["metadata_json"] = {}
            item["suspected_container"] = bool(item.get("suspected_container"))
            out.append(item)
        return out

    def get_archive_report(self, project_id: int, file_path: str) -> dict[str, Any] | None:
        row = self.db.query_one(
            """
            SELECT id, project_id, file_path, suspected_container, confidence, reason, metadata_json, updated_at
            FROM archive_reports
            WHERE project_id=? AND file_path=?
            """,
            (project_id, file_path),
        )
        if not row:
            return None
        item = dict(row)
        try:
            item["metadata_json"] = json.loads(item.get("metadata_json") or "{}")
        except json.JSONDecodeError:
            item["metadata_json"] = {}
        item["suspected_container"] = bool(item.get("suspected_container"))
        return item

    def set_setting(self, key: str, value: dict[str, Any]) -> None:
        self.db.execute(
            """
            INSERT INTO app_settings(key, value_json, updated_at)
            VALUES(?,?,?)
            ON CONFLICT(key) DO UPDATE SET
              value_json=excluded.value_json,
              updated_at=excluded.updated_at
            """,
            (key, json.dumps(value, ensure_ascii=False), _now_iso()),
        )

    def get_setting(self, key: str) -> dict[str, Any] | None:
        row = self.db.query_one("SELECT value_json FROM app_settings WHERE key=?", (key,))
        if not row:
            return None
        try:
            return json.loads(row["value_json"])
        except json.JSONDecodeError:
            return None

    def apply_correction(
        self,
        project_id: int,
        entry_id: int,
        corrected_text: str,
        *,
        user_note: str | None = None,
        source_lang: str = "unknown",
    ) -> None:
        row = self.db.query_one(
            "SELECT translated_text FROM translations WHERE entry_id=?",
            (entry_id,),
        )
        before = row["translated_text"] if row else ""
        self.add_correction_history(project_id, entry_id, before, corrected_text, user_note)
        decision = TranslationDecision(
            entry_id=entry_id,
            source_lang=source_lang,
            translated_text=corrected_text,
            status=TranslationStatus.CORRECTED,
            glossary_hits=[],
            tm_hits=[],
            quality_score=0.98,
            latency_ms=0,
            backend="user_correction",
            uncertainty=0.01,
            decision_log=["manual correction applied"],
        )
        self.upsert_translation(project_id, decision)
        entry_row = self.db.query_one(
            "SELECT source_text FROM extracted_entries WHERE id=?",
            (entry_id,),
        )
        source_text = entry_row["source_text"] if entry_row else ""
        if source_text:
            self.add_translation_memory(project_id, source_text, corrected_text, source_lang, quality_score=0.98)
        self.add_adaptation_event(
            project_id,
            event_type="user_correction",
            event_scope="translation",
            event_ref=str(entry_id),
            details={
                "before": before,
                "after": corrected_text,
                "user_note": user_note or "",
            },
        )
