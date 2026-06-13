from fastapi.testclient import TestClient
from orchestrator.main import app

client = TestClient(app)


def test_health() -> None:
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["service"] == "orchestrator"
