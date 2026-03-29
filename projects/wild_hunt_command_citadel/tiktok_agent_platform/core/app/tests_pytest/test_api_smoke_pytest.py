from __future__ import annotations

import pytest

pytest.importorskip("fastapi", reason="fastapi runtime dependency is required for API smoke tests")
_fastapi_testclient = pytest.importorskip(
    "fastapi.testclient",
    reason="fastapi.testclient runtime dependency is required for API smoke tests",
)
TestClient = _fastapi_testclient.TestClient

from app.api import app


def test_api_smoke_health_and_workspace():
    client = TestClient(app)
    assert client.get("/health").status_code == 200
    assert client.get("/workspace/health").status_code == 200
    assert client.get("/workspace/readiness").status_code == 200
    assert client.get("/workspace/prompt-lineage").status_code == 200
    assert client.get("/workspace/runtime-observability").status_code == 200
    assert client.get("/readiness").status_code == 200
