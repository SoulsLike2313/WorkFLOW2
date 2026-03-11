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
