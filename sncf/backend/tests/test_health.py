from __future__ import annotations

import json

from fastapi.testclient import TestClient

from app.config import Settings
from app.main import create_app


def test_health_ok(client: TestClient) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["data_loaded"] is True
    assert body["llm_enabled"] is False


def test_health_never_leaks_secrets(tmp_path) -> None:
    secret = "super-secret-token"
    settings = Settings(
        enable_docs=False,
        allowed_hosts=("testserver",),
        llm_api_key=secret,
    )
    with TestClient(create_app(settings)) as test_client:
        body = test_client.get("/health").text
        assert secret not in body
        assert "llm_api_key" not in body


def test_missing_dataset_degrades_gracefully(tmp_path) -> None:
    settings = Settings(
        enable_docs=False,
        allowed_hosts=("testserver",),
        data_dir=tmp_path,
    )
    with TestClient(create_app(settings)) as test_client:
        health = test_client.get("/health")
        assert health.status_code == 503
        assert health.json()["status"] == "degraded"

        search = test_client.post("/api/search", json={"origin": "Toulouse"})
        assert search.status_code == 503


def test_unknown_data_source_degrades(tmp_path) -> None:
    settings = Settings(
        enable_docs=False,
        allowed_hosts=("testserver",),
        data_source="not-a-real-source",
        data_dir=tmp_path,
    )
    with TestClient(create_app(settings)) as test_client:
        assert test_client.get("/health").status_code == 503


def test_docs_disabled_when_configured(settings) -> None:
    with TestClient(create_app(settings)) as test_client:
        assert test_client.get("/docs").status_code == 404
        assert test_client.get("/openapi.json").status_code == 404


def test_security_headers_present(client: TestClient) -> None:
    response = client.get("/health")
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["X-Frame-Options"] == "DENY"
    assert response.headers["Referrer-Policy"] == "no-referrer"
    assert response.json()["status"] == "ok"


def test_oversized_request_rejected(client: TestClient) -> None:
    payload = json.dumps({"origin": "Toulouse", "extra": "x" * 70000})
    response = client.post(
        "/api/search",
        content=payload,
        headers={"Content-Type": "application/json"},
    )
    assert response.status_code == 413
