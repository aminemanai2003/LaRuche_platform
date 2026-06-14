"""Auth endpoint tests — no Keycloak needed (dev bypass active)."""

from __future__ import annotations

from fastapi.testclient import TestClient
from orchestrator.main import app

client = TestClient(app)


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_auth_verify_no_keycloak():
    # Without KEYCLOAK_URL, dev bypass returns 200 + user headers
    r = client.get("/auth/verify")
    assert r.status_code == 200
    assert r.headers.get("x-user-id") == "dev-user"


def test_me_no_keycloak():
    r = client.get("/api/me")
    assert r.status_code == 200
    body = r.json()
    assert body["email"] == "dev@local"
    assert "advisor" in body["roles"]
