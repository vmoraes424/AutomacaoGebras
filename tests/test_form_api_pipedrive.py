"""Testes: endpoints Pipedrive do portal (com mocks)."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from portal.domain.crm.entities import CrmDeal, CrmUser
from portal.domain.crm.exceptions import CrmReadError
from portal.infrastructure.pipedrive.pipedrive_crm_reader import PipedriveCrmReader
from portal.main import create_app


@pytest.fixture
def client():
    return TestClient(create_app())


def test_list_users(client):
    mock_users = [
        CrmUser(id=1, name="Alice", email="alice@gebras.com.br"),
        CrmUser(id=2, name="Bob", email="bob@gebras.com.br"),
    ]
    mock_deals = [
        CrmDeal(id=746, title="Biview", owner_id=1),
    ]
    with (
        patch.object(PipedriveCrmReader, "list_users", return_value=mock_users),
        patch.object(
            PipedriveCrmReader,
            "list_open_deals_in_contrato_stage",
            return_value=mock_deals,
        ),
    ):
        response = client.get("/pipedrive/users")
    assert response.status_code == 200
    assert response.json() == [mock_users[0].to_dict()]


def test_list_users_sem_deals_contrato_retorna_vazio(client):
    mock_users = [CrmUser(id=1, name="Alice", email="alice@gebras.com.br")]
    with (
        patch.object(PipedriveCrmReader, "list_users", return_value=mock_users),
        patch.object(
            PipedriveCrmReader,
            "list_open_deals_in_contrato_stage",
            return_value=[],
        ),
    ):
        response = client.get("/pipedrive/users")
    assert response.status_code == 200
    assert response.json() == []


def test_list_users_pipedrive_error(client):
    mock_deals = [CrmDeal(id=746, title="Biview", owner_id=1)]
    with (
        patch.object(
            PipedriveCrmReader,
            "list_users",
            side_effect=CrmReadError("falha pipe"),
        ),
        patch.object(
            PipedriveCrmReader,
            "list_open_deals_in_contrato_stage",
            return_value=mock_deals,
        ),
    ):
        response = client.get("/pipedrive/users")
    assert response.status_code == 502


@patch("portal.infrastructure.pipedrive.pipedrive_crm_reader.deal_esta_em_etapa_contrato")
@patch("portal.infrastructure.pipedrive.pipedrive_crm_reader.requests.get")
def test_list_deals_filtra_etapa_contrato_e_owner(mock_get, mock_em_contrato, client):
    mock_em_contrato.side_effect = lambda d: d.get("id") in (746, 999)

    page = MagicMock()
    page.ok = True
    page.status_code = 200
    page.json.return_value = {
        "data": [
            {
                "id": 746,
                "title": "Biview",
                "owner_id": 24587114,
                "stage_id": 7,
                "status": "open",
                "pipeline_id": 1,
            },
            {
                "id": 100,
                "title": "Outro",
                "owner_id": 24587114,
                "stage_id": 5,
                "status": "open",
                "pipeline_id": 1,
            },
        ],
        "additional_data": {},
    }
    mock_get.return_value = page

    response = client.get("/pipedrive/deals", params={"owner_user_id": 24587114})

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == 746
    assert data[0]["owner_id"] == 24587114
    assert data[0]["portal_stage"] == "Contrato"
    assert data[0]["operational_label"] == "pendente"
    assert data[0]["ready_for_form"] is True
    assert data[0]["ready_for_automation"] is False
    assert mock_get.call_args.kwargs["params"]["owner_id"] == 24587114
    assert mock_get.call_args.kwargs["params"]["status"] == "open"


def test_portal_package_has_no_forbidden_imports():
    root = __import__("pathlib").Path(__file__).resolve().parent.parent / "portal"
    forbidden = (
        "plune_pedido",
        "hub_pedido",
        "automacao_contrato",
        "ClicksignClient",
    )
    for path in root.rglob("*.py"):
        text = path.read_text(encoding="utf-8")
        for token in forbidden:
            assert token not in text, f"{token} encontrado em {path}"


def test_domain_and_application_have_no_fastapi_imports():
    root = __import__("pathlib").Path(__file__).resolve().parent.parent / "portal"
    for layer in ("domain", "application"):
        for path in (root / layer).rglob("*.py"):
            text = path.read_text(encoding="utf-8")
            assert "fastapi" not in text, f"fastapi em {path}"
            assert "requests" not in text, f"requests em {path}"
