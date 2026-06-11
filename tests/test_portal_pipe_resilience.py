"""Fase 7 — falha no Pipe não apaga formulários salvos."""

from __future__ import annotations

from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from portal.composition import reset_container
from portal.main import create_app


@pytest.fixture
def client():
    reset_container()
    yield TestClient(create_app())
    reset_container()


@patch("core.form_pipe_sync.fetch_deal_for_form", return_value=None)
def test_get_form_retorna_rascunho_quando_pipe_indisponivel(_fetch, client):
    body = {
        "payload": {"cliente": {"contratante": "Salvo no banco"}},
        "schema_version": "v1",
    }
    put = client.put("/forms/501/draft", json=body)
    assert put.status_code == 200

    get = client.get("/forms/501")
    assert get.status_code == 200
    assert get.json()["payload"]["cliente"]["contratante"] == "Salvo no banco"


@patch("core.form_pipe_sync.fetch_deal_for_form", return_value=None)
def test_get_form_404_sem_rascunho_e_sem_pipe(_fetch, client):
    response = client.get("/forms/999999")
    assert response.status_code == 404
