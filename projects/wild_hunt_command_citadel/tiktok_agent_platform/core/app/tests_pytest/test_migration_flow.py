from __future__ import annotations

from app.workspace.persistence import LATEST_SCHEMA_VERSION, SQLiteWorkspacePersistence


def test_workspace_persistence_migration(tmp_path):
    db = tmp_path / "workspace_state.db"
    persistence = SQLiteWorkspacePersistence(db)
    version = persistence.get_schema_version()
    assert version == LATEST_SCHEMA_VERSION
    persistence.migrate()
    assert persistence.get_schema_version() == LATEST_SCHEMA_VERSION

