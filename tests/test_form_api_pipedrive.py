"""Testes: endpoints Pipedrive do portal (com mocks)."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from portal.domain.crm.entities import ContratoSnapshot, CrmDeal, CrmUser
from portal.domain.crm.exceptions import CrmReadError
from portal.infrastructure.pipedrive.pipedrive_crm_reader import PipedriveCrmReader
from portal.main import create_app


@pytest.fixture
def client():
    return TestClient(create_app())


def _snapshot(users: list[CrmUser], deals: list[CrmDeal]) -> ContratoSnapshot:
    return ContratoSnapshot(deals=tuple(deals), users=tuple(users))


def test_list_users(client):
    mock_users = [
        CrmUser(id=1, name="Alice", email="alice@gebras.com.br"),
        CrmUser(id=2, name="Bob", email="bob@gebras.com.br"),
    ]
    mock_deals = [CrmDeal(id=746, title="Biview", owner_id=1)]
    with patch.object(
        PipedriveCrmReader,
        "get_contrato_snapshot",
        return_value=_snapshot(mock_users, mock_deals),
    ):
        response = client.get("/pipedrive/users")
    assert response.status_code == 200
    assert response.json() == [
        {
            "id": 1,
            "name": "Alice",
            "email": "alice@gebras.com.br",
            "deals_contrato_count": 1,
        }
    ]


def test_list_users_conta_deals_por_consultor(client):
    mock_users = [
        CrmUser(id=1, name="Alice", email="alice@gebras.com.br"),
        CrmUser(id=2, name="Bob", email="bob@gebras.com.br"),
    ]
    mock_deals = [
        CrmDeal(id=746, title="Biview", owner_id=1),
        CrmDeal(id=747, title="Outro", owner_id=1),
        CrmDeal(id=800, title="Bob deal", owner_id=2),
    ]
    with patch.object(
        PipedriveCrmReader,
        "get_contrato_snapshot",
        return_value=_snapshot(mock_users, mock_deals),
    ):
        response = client.get("/pipedrive/users")
    assert response.status_code == 200
    by_id = {u["id"]: u for u in response.json()}
    assert by_id[1]["deals_contrato_count"] == 2
    assert by_id[2]["deals_contrato_count"] == 1


def test_list_users_sem_deals_contrato_retorna_vazio(client):
    mock_users = [CrmUser(id=1, name="Alice", email="alice@gebras.com.br")]
    with patch.object(
        PipedriveCrmReader,
        "get_contrato_snapshot",
        return_value=_snapshot(mock_users, []),
    ):
        response = client.get("/pipedrive/users")
    assert response.status_code == 200
    assert response.json() == []


def test_list_users_pipedrive_error(client):
    with patch.object(
        PipedriveCrmReader,
        "get_contrato_snapshot",
        side_effect=CrmReadError("falha pipe"),
    ):
        response = client.get("/pipedrive/users")
    assert response.status_code == 502


def test_x_portal_fresh_header_bypasses_backend_cache(client):
    """Sem header reutiliza TTL; X-Portal-Fresh: 1 força nova leitura do Pipe."""
    PipedriveCrmReader.invalidate_crm_cache()

    mock_users = [CrmUser(id=1, name="Alice", email="alice@gebras.com.br")]
    mock_deals = [CrmDeal(id=746, title="Biview", owner_id=1)]
    fetch_count = {"n": 0}

    def fetch_snapshot(_self):
        fetch_count["n"] += 1
        return _snapshot(mock_users, mock_deals)

    with patch.object(PipedriveCrmReader, "_fetch_contrato_snapshot", fetch_snapshot):
        assert client.get("/pipedrive/users").status_code == 200
        assert fetch_count["n"] == 1

        assert client.get("/pipedrive/users").status_code == 200
        assert fetch_count["n"] == 1

        assert (
            client.get("/pipedrive/users", headers={"X-Portal-Fresh": "1"}).status_code == 200
        )
        assert fetch_count["n"] == 2

    PipedriveCrmReader.invalidate_crm_cache()


def test_list_deals_sem_fresh_header_usa_cache(client):
    PipedriveCrmReader.invalidate_crm_cache()

    mock_users = [CrmUser(id=1, name="Alice", email="alice@gebras.com.br")]
    mock_deals = [CrmDeal(id=746, title="Biview", owner_id=1)]
    fetch_count = {"n": 0}

    def fetch_snapshot(_self):
        fetch_count["n"] += 1
        return _snapshot(mock_users, mock_deals)

    with patch.object(PipedriveCrmReader, "_fetch_contrato_snapshot", fetch_snapshot):
        assert client.get("/pipedrive/deals", params={"owner_user_id": 1}).status_code == 200
        assert fetch_count["n"] == 1

        assert client.get("/pipedrive/deals", params={"owner_user_id": 1}).status_code == 200
        assert fetch_count["n"] == 1

        assert (
            client.get(
                "/pipedrive/deals",
                params={"owner_user_id": 1},
                headers={"X-Portal-Fresh": "1"},
            ).status_code
            == 200
        )
        assert fetch_count["n"] == 2

    PipedriveCrmReader.invalidate_crm_cache()


@patch("portal.infrastructure.pipedrive.pipedrive_crm_reader.requests.get")
@patch(
    "portal.infrastructure.pipedrive.pipedrive_crm_reader.list_stage_ids_etapa_contrato",
    return_value=[7],
)
def test_list_deals_filtra_etapa_contrato_e_owner(mock_stages, mock_get, client):
    page = MagicMock()
    page.ok = True
    page.status_code = 200
    page.text = ""
    page.json.side_effect = [
        {"data": []},
        {
            "data": [
                {
                    "id": 746,
                    "title": "Biview",
                    "owner_id": 24587114,
                    "stage_id": 7,
                    "status": "open",
                    "pipeline_id": 1,
                    "org_id": 670,
                },
            ],
            "additional_data": {},
        },
        {"data": [{"id": 670, "name": "Biview Org"}]},
        {"data": []},
    ]
    mock_get.return_value = page

    PipedriveCrmReader.invalidate_crm_cache()
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
    deals_call = mock_get.call_args_list[1]
    assert deals_call.kwargs["params"]["status"] == "open"
    assert deals_call.kwargs["params"]["stage_id"] == 7
    assert "owner_id" not in deals_call.kwargs["params"]


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
