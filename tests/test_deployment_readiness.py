import os
import importlib
import os

from fastapi.testclient import TestClient


def get_test_client():
    # Import lazily so env vars are considered at call time
    from mcp_server import server  # noqa
    return TestClient(server.http_app)


def test_health_endpoint_production(monkeypatch):
    monkeypatch.setenv("ENVIRONMENT", "production")
    monkeypatch.setenv("PORT", "3030")
    client = get_test_client()
    r = client.get("/health")
    assert r.status_code == 200
    data = r.json()
    for key in ["status", "service", "version", "environment", "port"]:
        assert key in data
    assert data["port"] == "3030"
    assert data["environment"] == "production"


def test_root_endpoint_includes_protocols(monkeypatch):
    monkeypatch.setenv("ENVIRONMENT", "production")
    monkeypatch.setenv("PORT", "3030")
    client = get_test_client()
    r = client.get("/")
    assert r.status_code == 200
    data = r.json()
    assert "protocols" in data
    assert "mcp_websocket" in data["protocols"]
    assert data["status"] == "running"


def test_websocket_connect(monkeypatch):
    monkeypatch.setenv("ENVIRONMENT", "production")
    monkeypatch.setenv("PORT", "3030")
    client = get_test_client()
    with client.websocket_connect("/mcp") as ws:
        # Just ensure connection opens and can close cleanly
        ws.close()


def test_api_key_auth_run_code(monkeypatch):
    monkeypatch.setenv("ENVIRONMENT", "production")
    monkeypatch.setenv("PORT", "3030")
    stable_key = "mcp_admin_static_test_key"
    monkeypatch.setenv("API_KEY", stable_key)
    # Reload auth to pick up stable key
    from mcp_server.utils import auth
    importlib.reload(auth)
    from mcp_server.utils.auth import api_key_manager

    assert stable_key in api_key_manager.api_keys
    client = get_test_client()
    r = client.post(
        "/run_code",
        headers={"Authorization": f"Bearer {stable_key}"},
        json={"code": "print('hi')"},
    )
    assert r.status_code == 200
    data = r.json()
    assert "stdout" in data and "hi" in data["stdout"]


def test_api_key_auth_required(monkeypatch):
    monkeypatch.setenv("ENVIRONMENT", "production")
    monkeypatch.setenv("PORT", "3030")
    client = get_test_client()
    r = client.post("/run_code", json={"code": "print('x')"})
    # HTTPBearer returns 403 when missing credentials
    assert r.status_code in (401, 403)
