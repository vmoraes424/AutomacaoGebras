"""Testes: healthcheck da API do portal."""

from __future__ import annotations

from fastapi.testclient import TestClient

from portal.main import create_app


def test_health_returns_200():
    client = TestClient(create_app())
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
