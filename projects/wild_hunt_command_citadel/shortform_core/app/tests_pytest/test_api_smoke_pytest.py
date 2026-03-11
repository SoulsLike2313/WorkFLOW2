from __future__ import annotations

from fastapi.testclient import TestClient

from app.api import app


def test_api_smoke_health_and_workspace():
    client = TestClient(app)
    assert client.get("/health").status_code == 200
    assert client.get("/workspace/health").status_code == 200
    assert client.get("/workspace/readiness").status_code == 200
    assert client.get("/readiness").status_code == 200

