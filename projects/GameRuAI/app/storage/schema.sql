PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS projects (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  game_path TEXT NOT NULL,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE(name, game_path)
);

CREATE TABLE IF NOT EXISTS scanned_files (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
  file_path TEXT NOT NULL,
  file_type TEXT NOT NULL,
  file_ext TEXT NOT NULL,
  size_bytes INTEGER NOT NULL,
  sha1 TEXT NOT NULL,
  manifest_group TEXT NOT NULL,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_scanned_files_project ON scanned_files(project_id);

CREATE TABLE IF NOT EXISTS extracted_entries (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
  line_id TEXT NOT NULL,
  file_path TEXT NOT NULL,
  speaker_id TEXT,
  source_text TEXT NOT NULL,
  context_type TEXT NOT NULL,
  tags_json TEXT NOT NULL DEFAULT '[]',
  placeholders_json TEXT NOT NULL DEFAULT '[]',
  voice_link TEXT,
  metadata_json TEXT NOT NULL DEFAULT '{}',
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE(project_id, line_id, file_path)
);
CREATE INDEX IF NOT EXISTS idx_extracted_project ON extracted_entries(project_id);
CREATE INDEX IF NOT EXISTS idx_extracted_line ON extracted_entries(line_id);

CREATE TABLE IF NOT EXISTS translations (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  entry_id INTEGER NOT NULL REFERENCES extracted_entries(id) ON DELETE CASCADE,
  project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
  source_lang TEXT NOT NULL,
  translated_text TEXT NOT NULL,
  translation_status TEXT NOT NULL,
  glossary_hits_json TEXT NOT NULL DEFAULT '[]',
  tm_hits_json TEXT NOT NULL DEFAULT '[]',
  quality_score REAL NOT NULL DEFAULT 0,
  latency_ms INTEGER NOT NULL DEFAULT 0,
  backend TEXT NOT NULL,
  fallback_backend TEXT,
  context_used INTEGER NOT NULL DEFAULT 0,
  uncertainty REAL NOT NULL DEFAULT 0,
  decision_log_json TEXT NOT NULL DEFAULT '[]',
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE(entry_id)
);
CREATE INDEX IF NOT EXISTS idx_translations_project ON translations(project_id);

CREATE TABLE IF NOT EXISTS glossary_terms (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
  source_term TEXT NOT NULL,
  target_term TEXT NOT NULL,
  source_lang TEXT NOT NULL,
  case_sensitive INTEGER NOT NULL DEFAULT 0,
  priority INTEGER NOT NULL DEFAULT 100,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE(project_id, source_term, source_lang)
);
CREATE INDEX IF NOT EXISTS idx_glossary_project ON glossary_terms(project_id);

CREATE TABLE IF NOT EXISTS translation_memory (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
  source_text TEXT NOT NULL,
  target_text TEXT NOT NULL,
  source_lang TEXT NOT NULL,
  quality_score REAL NOT NULL DEFAULT 0,
  use_count INTEGER NOT NULL DEFAULT 0,
  last_used_at TEXT,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_tm_project_lang ON translation_memory(project_id, source_lang);

CREATE TABLE IF NOT EXISTS language_detections (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  entry_id INTEGER NOT NULL REFERENCES extracted_entries(id) ON DELETE CASCADE,
  project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
  detected_lang TEXT NOT NULL,
  confidence REAL NOT NULL,
  heuristics_json TEXT NOT NULL DEFAULT '{}',
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE(entry_id)
);
CREATE INDEX IF NOT EXISTS idx_lang_project ON language_detections(project_id);

CREATE TABLE IF NOT EXISTS voice_links (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  entry_id INTEGER NOT NULL REFERENCES extracted_entries(id) ON DELETE CASCADE,
  project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
  speaker_id TEXT,
  source_voice_path TEXT NOT NULL,
  text_voice_key TEXT,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE(entry_id)
);
CREATE INDEX IF NOT EXISTS idx_voice_links_project ON voice_links(project_id);

CREATE TABLE IF NOT EXISTS voice_profiles (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
  speaker_id TEXT NOT NULL,
  profile_json TEXT NOT NULL,
  updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE(project_id, speaker_id)
);
CREATE INDEX IF NOT EXISTS idx_voice_profiles_project ON voice_profiles(project_id);

CREATE TABLE IF NOT EXISTS speaker_groups (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
  speaker_id TEXT NOT NULL,
  group_label TEXT NOT NULL,
  line_count INTEGER NOT NULL DEFAULT 0,
  linked_count INTEGER NOT NULL DEFAULT 0,
  broken_links INTEGER NOT NULL DEFAULT 0,
  scene_count INTEGER NOT NULL DEFAULT 0,
  avg_confidence REAL NOT NULL DEFAULT 0,
  metadata_json TEXT NOT NULL DEFAULT '{}',
  updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE(project_id, speaker_id)
);
CREATE INDEX IF NOT EXISTS idx_speaker_groups_project ON speaker_groups(project_id);

CREATE TABLE IF NOT EXISTS voice_sample_bank (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
  speaker_id TEXT NOT NULL,
  line_id TEXT,
  scene_id TEXT,
  source_file TEXT NOT NULL,
  source_duration_ms INTEGER NOT NULL DEFAULT 0,
  metadata_json TEXT NOT NULL DEFAULT '{}',
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_voice_sample_bank_project ON voice_sample_bank(project_id);
CREATE INDEX IF NOT EXISTS idx_voice_sample_bank_speaker ON voice_sample_bank(project_id, speaker_id);

CREATE TABLE IF NOT EXISTS voice_attempts (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  entry_id INTEGER NOT NULL REFERENCES extracted_entries(id) ON DELETE CASCADE,
  project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
  speaker_id TEXT NOT NULL,
  source_voice_path TEXT NOT NULL,
  output_voice_path TEXT NOT NULL,
  status TEXT NOT NULL,
  quality_score REAL NOT NULL DEFAULT 0,
  duration_source_ms INTEGER NOT NULL DEFAULT 0,
  duration_output_ms INTEGER NOT NULL DEFAULT 0,
  metadata_json TEXT NOT NULL DEFAULT '{}',
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_voice_attempts_project ON voice_attempts(project_id);
CREATE INDEX IF NOT EXISTS idx_voice_attempts_entry ON voice_attempts(entry_id);

CREATE TABLE IF NOT EXISTS voice_attempt_history (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
  entry_id INTEGER REFERENCES extracted_entries(id) ON DELETE SET NULL,
  speaker_id TEXT NOT NULL,
  source_file TEXT NOT NULL,
  source_duration_ms INTEGER NOT NULL DEFAULT 0,
  generated_file TEXT NOT NULL,
  synthesis_mode TEXT NOT NULL,
  alignment_ratio REAL NOT NULL DEFAULT 0,
  quality_score REAL NOT NULL DEFAULT 0,
  confidence_score REAL NOT NULL DEFAULT 0,
  metadata_json TEXT NOT NULL DEFAULT '{}',
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_voice_attempt_history_project ON voice_attempt_history(project_id);
CREATE INDEX IF NOT EXISTS idx_voice_attempt_history_speaker ON voice_attempt_history(project_id, speaker_id);

CREATE TABLE IF NOT EXISTS correction_history (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  entry_id INTEGER NOT NULL REFERENCES extracted_entries(id) ON DELETE CASCADE,
  project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
  before_text TEXT NOT NULL,
  after_text TEXT NOT NULL,
  user_note TEXT,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_correction_project ON correction_history(project_id);

CREATE TABLE IF NOT EXISTS adaptation_events (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
  event_type TEXT NOT NULL,
  event_scope TEXT,
  event_ref TEXT,
  details_json TEXT NOT NULL DEFAULT '{}',
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_adaptation_project ON adaptation_events(project_id);

CREATE TABLE IF NOT EXISTS qa_findings (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
  entry_id INTEGER REFERENCES extracted_entries(id) ON DELETE SET NULL,
  check_name TEXT NOT NULL,
  severity TEXT NOT NULL,
  message TEXT NOT NULL,
  details_json TEXT NOT NULL DEFAULT '{}',
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_qa_project ON qa_findings(project_id);

CREATE TABLE IF NOT EXISTS export_jobs (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
  output_dir TEXT NOT NULL,
  status TEXT NOT NULL,
  manifest_path TEXT,
  diff_report_path TEXT,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_export_jobs_project ON export_jobs(project_id);

CREATE TABLE IF NOT EXISTS app_settings (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  key TEXT NOT NULL UNIQUE,
  value_json TEXT NOT NULL,
  updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS companion_sessions (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
  session_id TEXT NOT NULL UNIQUE,
  executable_path TEXT NOT NULL,
  watched_path TEXT NOT NULL,
  process_pid INTEGER,
  process_status TEXT NOT NULL,
  started_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  ended_at TEXT
);
CREATE INDEX IF NOT EXISTS idx_companion_sessions_project ON companion_sessions(project_id);

CREATE TABLE IF NOT EXISTS watched_file_events (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
  session_id TEXT NOT NULL,
  watched_path TEXT NOT NULL,
  event_type TEXT NOT NULL,
  file_path TEXT NOT NULL,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_watched_events_project ON watched_file_events(project_id);
CREATE INDEX IF NOT EXISTS idx_watched_events_session ON watched_file_events(session_id);

CREATE TABLE IF NOT EXISTS translation_backend_runs (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
  entry_id INTEGER REFERENCES extracted_entries(id) ON DELETE SET NULL,
  requested_backend TEXT NOT NULL,
  backend_name TEXT NOT NULL,
  fallback_backend TEXT,
  latency_ms INTEGER NOT NULL DEFAULT 0,
  context_used INTEGER NOT NULL DEFAULT 0,
  fallback_used INTEGER NOT NULL DEFAULT 0,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_backend_runs_project ON translation_backend_runs(project_id);
CREATE INDEX IF NOT EXISTS idx_backend_runs_entry ON translation_backend_runs(entry_id);

CREATE TABLE IF NOT EXISTS language_reports (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
  report_name TEXT NOT NULL,
  lines_total INTEGER NOT NULL DEFAULT 0,
  uncertain_count INTEGER NOT NULL DEFAULT 0,
  uncertain_rate REAL NOT NULL DEFAULT 0,
  payload_json TEXT NOT NULL DEFAULT '{}',
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE(project_id, report_name)
);
CREATE INDEX IF NOT EXISTS idx_language_reports_project ON language_reports(project_id);

CREATE TABLE IF NOT EXISTS project_reports (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
  report_type TEXT NOT NULL,
  payload_json TEXT NOT NULL DEFAULT '{}',
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_project_reports_project ON project_reports(project_id);

CREATE TABLE IF NOT EXISTS backend_diagnostics (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
  backend_name TEXT NOT NULL,
  runs_count INTEGER NOT NULL DEFAULT 0,
  avg_latency_ms REAL NOT NULL DEFAULT 0,
  p95_latency_ms REAL NOT NULL DEFAULT 0,
  fallback_count INTEGER NOT NULL DEFAULT 0,
  context_used_rate REAL NOT NULL DEFAULT 0,
  payload_json TEXT NOT NULL DEFAULT '{}',
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_backend_diagnostics_project ON backend_diagnostics(project_id);

CREATE TABLE IF NOT EXISTS quality_snapshots (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
  snapshot_type TEXT NOT NULL,
  payload_json TEXT NOT NULL DEFAULT '{}',
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_quality_snapshots_project ON quality_snapshots(project_id);

CREATE TABLE IF NOT EXISTS asset_index (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
  file_path TEXT NOT NULL,
  asset_type TEXT NOT NULL,
  preview_type TEXT NOT NULL,
  preview_status TEXT NOT NULL,
  metadata_json TEXT NOT NULL DEFAULT '{}',
  suspected_container INTEGER NOT NULL DEFAULT 0,
  relevance_score REAL NOT NULL DEFAULT 0,
  updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE(project_id, file_path)
);
CREATE INDEX IF NOT EXISTS idx_asset_index_project ON asset_index(project_id);
CREATE INDEX IF NOT EXISTS idx_asset_index_type ON asset_index(asset_type);

CREATE TABLE IF NOT EXISTS asset_previews (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
  file_path TEXT NOT NULL,
  preview_type TEXT NOT NULL,
  preview_status TEXT NOT NULL,
  preview_path TEXT,
  metadata_json TEXT NOT NULL DEFAULT '{}',
  updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE(project_id, file_path, preview_type)
);
CREATE INDEX IF NOT EXISTS idx_asset_previews_project ON asset_previews(project_id);

CREATE TABLE IF NOT EXISTS archive_reports (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
  file_path TEXT NOT NULL,
  suspected_container INTEGER NOT NULL DEFAULT 0,
  confidence REAL NOT NULL DEFAULT 0,
  reason TEXT NOT NULL,
  metadata_json TEXT NOT NULL DEFAULT '{}',
  updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE(project_id, file_path)
);
CREATE INDEX IF NOT EXISTS idx_archive_reports_project ON archive_reports(project_id);

CREATE TABLE IF NOT EXISTS asset_manifest (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
  file_path TEXT NOT NULL,
  media_type TEXT NOT NULL,
  content_role TEXT NOT NULL,
  extension TEXT NOT NULL,
  size_bytes INTEGER NOT NULL DEFAULT 0,
  relevance_score REAL NOT NULL DEFAULT 0,
  suspected_container INTEGER NOT NULL DEFAULT 0,
  status TEXT NOT NULL DEFAULT 'indexed',
  confidence REAL NOT NULL DEFAULT 0,
  provenance TEXT NOT NULL DEFAULT 'asset_intelligence_core',
  version_tag TEXT NOT NULL DEFAULT 'v1',
  metadata_json TEXT NOT NULL DEFAULT '{}',
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE(project_id, file_path)
);
CREATE INDEX IF NOT EXISTS idx_asset_manifest_project ON asset_manifest(project_id);
CREATE INDEX IF NOT EXISTS idx_asset_manifest_media ON asset_manifest(media_type);

CREATE TABLE IF NOT EXISTS content_units (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
  entry_id INTEGER REFERENCES extracted_entries(id) ON DELETE SET NULL,
  line_id TEXT NOT NULL,
  file_path TEXT NOT NULL,
  content_type TEXT NOT NULL,
  source_lang TEXT NOT NULL DEFAULT 'unknown',
  confidence REAL NOT NULL DEFAULT 0,
  scene_id TEXT,
  speaker_id TEXT,
  status TEXT NOT NULL DEFAULT 'analyzed',
  provenance TEXT NOT NULL DEFAULT 'content_understanding_core',
  metadata_json TEXT NOT NULL DEFAULT '{}',
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_content_units_project ON content_units(project_id);
CREATE INDEX IF NOT EXISTS idx_content_units_line ON content_units(project_id, line_id);

CREATE TABLE IF NOT EXISTS scene_groups (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
  scene_id TEXT NOT NULL,
  line_count INTEGER NOT NULL DEFAULT 0,
  speaker_count INTEGER NOT NULL DEFAULT 0,
  status TEXT NOT NULL DEFAULT 'ready',
  confidence REAL NOT NULL DEFAULT 0,
  provenance TEXT NOT NULL DEFAULT 'scene_model',
  metadata_json TEXT NOT NULL DEFAULT '{}',
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE(project_id, scene_id)
);
CREATE INDEX IF NOT EXISTS idx_scene_groups_project ON scene_groups(project_id);

CREATE TABLE IF NOT EXISTS transcript_segments (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
  entry_id INTEGER REFERENCES extracted_entries(id) ON DELETE SET NULL,
  line_id TEXT NOT NULL,
  segment_id INTEGER NOT NULL DEFAULT 0,
  start_ms INTEGER NOT NULL DEFAULT 0,
  end_ms INTEGER NOT NULL DEFAULT 0,
  confidence REAL NOT NULL DEFAULT 0,
  provenance TEXT NOT NULL DEFAULT 'audio_analysis',
  metadata_json TEXT NOT NULL DEFAULT '{}',
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_transcript_segments_project ON transcript_segments(project_id);

CREATE TABLE IF NOT EXISTS sync_plans (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
  entry_id INTEGER REFERENCES extracted_entries(id) ON DELETE SET NULL,
  line_id TEXT,
  source_duration_ms INTEGER NOT NULL DEFAULT 0,
  target_duration_ms INTEGER NOT NULL DEFAULT 0,
  delta_ms INTEGER NOT NULL DEFAULT 0,
  recommended_adjustment TEXT NOT NULL,
  confidence REAL NOT NULL DEFAULT 0,
  status TEXT NOT NULL DEFAULT 'planned',
  provenance TEXT NOT NULL DEFAULT 'sync_core',
  payload_json TEXT NOT NULL DEFAULT '{}',
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_sync_plans_project ON sync_plans(project_id);

CREATE TABLE IF NOT EXISTS translation_packages (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
  entry_id INTEGER REFERENCES extracted_entries(id) ON DELETE SET NULL,
  backend_name TEXT NOT NULL,
  fallback_used INTEGER NOT NULL DEFAULT 0,
  confidence REAL NOT NULL DEFAULT 0,
  quality_score REAL NOT NULL DEFAULT 0,
  status TEXT NOT NULL DEFAULT 'generated',
  package_json TEXT NOT NULL DEFAULT '{}',
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_translation_packages_project ON translation_packages(project_id);
CREATE INDEX IF NOT EXISTS idx_translation_packages_entry ON translation_packages(project_id, entry_id);

CREATE TABLE IF NOT EXISTS knowledge_sources (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
  source_key TEXT NOT NULL,
  source_type TEXT NOT NULL,
  version_tag TEXT NOT NULL,
  source_status TEXT NOT NULL,
  health_state TEXT NOT NULL DEFAULT 'ok',
  metadata_json TEXT NOT NULL DEFAULT '{}',
  provenance TEXT NOT NULL DEFAULT 'source_of_truth',
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE(project_id, source_key)
);
CREATE INDEX IF NOT EXISTS idx_knowledge_sources_project ON knowledge_sources(project_id);

CREATE TABLE IF NOT EXISTS external_reference_events (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
  entry_id INTEGER REFERENCES extracted_entries(id) ON DELETE SET NULL,
  provider TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'logged',
  confidence REAL NOT NULL DEFAULT 0,
  payload_json TEXT NOT NULL DEFAULT '{}',
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_external_reference_events_project ON external_reference_events(project_id);

CREATE TABLE IF NOT EXISTS evidence_records (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
  evidence_type TEXT NOT NULL,
  entity_ref TEXT NOT NULL,
  confidence REAL NOT NULL DEFAULT 0,
  status TEXT NOT NULL DEFAULT 'recorded',
  payload_json TEXT NOT NULL DEFAULT '{}',
  provenance TEXT NOT NULL DEFAULT 'evidence_learning_core',
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_evidence_records_project ON evidence_records(project_id);

CREATE TABLE IF NOT EXISTS audio_analysis_results (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
  entry_id INTEGER REFERENCES extracted_entries(id) ON DELETE SET NULL,
  source_file TEXT NOT NULL,
  generated_file TEXT,
  source_duration_ms INTEGER NOT NULL DEFAULT 0,
  generated_duration_ms INTEGER NOT NULL DEFAULT 0,
  delta_ms INTEGER NOT NULL DEFAULT 0,
  quality_score REAL NOT NULL DEFAULT 0,
  confidence REAL NOT NULL DEFAULT 0,
  status TEXT NOT NULL DEFAULT 'analyzed',
  payload_json TEXT NOT NULL DEFAULT '{}',
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_audio_analysis_results_project ON audio_analysis_results(project_id);
