"""Contrato API ↔ fixture formulario v1 (Fase 3)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from portal.composition import reset_container
from portal.main import create_app

FIXTURE = (
    Path(__file__).resolve().parent / "fixtures" / "formulario_v1" / "form_payload_v1_g1.json"
)


@pytest.fixture
def client():
    reset_container()
    yield TestClient(create_app())
    reset_container()


def test_fixture_g1_aceito_pelo_backend(client):
    payload = json.loads(FIXTURE.read_text(encoding="utf-8"))
    body = {
        "payload": payload,
        "schema_version": "v1",
        "owner_user_id": 24587114,
        "owner_name": "Consultor Teste",
        "deal_title": "Biview",
    }
    put = client.put("/forms/746/draft", json=body)
    assert put.status_code == 200
    data = put.json()
    assert data["deal_id"] == 746
    assert data["payload"]["cliente"]["contratante"] == payload["cliente"]["contratante"]
    assert data["payload"]["servicos"]["sole_web"] == payload["servicos"]["sole_web"]

    get = client.get("/forms/746")
    assert get.status_code == 200
    assert get.json()["payload"]["hub"]["observacoes_detalhes"] == payload["hub"]["observacoes_detalhes"]
