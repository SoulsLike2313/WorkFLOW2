from __future__ import annotations

from app.config import load_config
from app.update import UpdateService


def test_post_update_verification_flow():
    service = UpdateService(load_config())
    result = service.post_update_verification()
    assert result["status"] in {"PASS", "PASS_WITH_WARNINGS", "FAIL"}
    assert "readiness" in result

