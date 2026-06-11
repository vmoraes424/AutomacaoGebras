"""Fase 7 — smoke pós-deploy (health, listagem, deal de teste)."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from portal.composition import reset_container
from portal.domain.crm.entities import CrmDeal, CrmUser
from portal.infrastructure.pipedrive.pipedrive_crm_reader import PipedriveCrmReader
from portal.main import create_app


@pytest.fixture
def client():
    reset_container()
    yield TestClient(create_app())
    reset_container()


def test_smoke_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "portal"
    assert data["status"] == "ok"
    assert "formulario_web_enabled" in data


def test_smoke_list_users(client):
    users = [CrmUser(id=1, name="Alice", email="a@gebras.com.br")]
    deals = [CrmDeal(id=746, title="Deal", owner_id=1)]
    with (
        patch(
            "portal.infrastructure.pipedrive.pipedrive_crm_reader.PipedriveCrmReader.list_users",
            return_value=users,
        ),
        patch(
            "portal.infrastructure.pipedrive.pipedrive_crm_reader.PipedriveCrmReader.list_open_deals_in_contrato_stage",
            return_value=deals,
        ),
    ):
        response = client.get("/pipedrive/users")
    assert response.status_code == 200
    assert response.json()[0]["name"] == "Alice"


@patch("portal.infrastructure.pipedrive.pipedrive_crm_reader.requests.get")
@patch(
    "portal.infrastructure.pipedrive.pipedrive_crm_reader.list_stage_ids_etapa_contrato",
    return_value=[7],
)
def test_smoke_list_deals(mock_stages, mock_get, client):
    page = MagicMock()
    page.ok = True
    page.text = ""
    page.json.side_effect = [
        {
            "data": [
                {
                    "id": 746,
                    "title": "Smoke deal",
                    "owner_id": 1,
                    "stage_id": 7,
                    "status": "open",
                    "pipeline_id": 1,
                    "org_id": 670,
                }
            ],
            "additional_data": {},
        },
        {"data": [{"id": 670, "name": "Org"}]},
    ]
    mock_get.return_value = page

    PipedriveCrmReader.invalidate_crm_cache()
    response = client.get("/pipedrive/deals", params={"owner_user_id": 1})
    assert response.status_code == 200
    deals = response.json()
    assert len(deals) == 1
    assert deals[0]["operational_label"] == "pendente"


@patch("portal.application.formulario.deal_eligibility.deal_elegivel_formulario_contrato", return_value=True)
@patch("portal.application.formulario.deal_eligibility.fetch_deal_for_form")
@patch("core.form_pipe_sync.fetch_deal_for_form")
def test_smoke_form_deal_teste(mock_fetch, mock_elig_fetch, _elegivel, client):
    deal = {
        "id": 746,
        "title": "Smoke",
        "status": "open",
        "custom_fields": {},
    }
    mock_fetch.return_value = deal
    mock_elig_fetch.return_value = deal
    response = client.get("/forms/746")
    assert response.status_code == 200
    assert response.json()["deal_id"] == 746
    assert response.json()["status"] == "draft"
