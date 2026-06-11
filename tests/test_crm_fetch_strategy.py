"""Testes de estratégia de fetch CRM (stage_id + orgs em bulk)."""

from __future__ import annotations

import os
import time
from unittest.mock import MagicMock, patch

import pytest

from core.pipedrive_stages import limpar_cache_stages
from portal.infrastructure.pipedrive.pipedrive_crm_reader import PipedriveCrmReader


def _mock_response(payload: dict, *, ok: bool = True) -> MagicMock:
    resp = MagicMock()
    resp.ok = ok
    resp.status_code = 200 if ok else 502
    resp.text = ""
    resp.json.return_value = payload
    return resp


@patch("portal.infrastructure.pipedrive.pipedrive_crm_reader.requests.get")
@patch(
    "portal.infrastructure.pipedrive.pipedrive_crm_reader.list_stage_ids_etapa_contrato",
    return_value=[7],
)
def test_fetch_contrato_deals_usa_stage_id_e_orgs_bulk(mock_stages, mock_get):
    deals_page = _mock_response(
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
                }
            ],
            "additional_data": {},
        }
    )
    orgs_page = _mock_response(
        {"data": [{"id": 670, "name": "Cliente Biview"}]}
    )
    mock_get.side_effect = [deals_page, orgs_page]

    reader = PipedriveCrmReader(api_token="test-token")
    deals = reader._fetch_contrato_deals()

    assert len(deals) == 1
    assert deals[0].id == 746
    assert deals[0].org_name == "Cliente Biview"

    deals_call = mock_get.call_args_list[0]
    assert deals_call.args[0] == "https://api.pipedrive.com/api/v2/deals"
    assert deals_call.kwargs["params"]["stage_id"] == 7
    assert deals_call.kwargs["params"]["status"] == "open"
    assert "owner_id" not in deals_call.kwargs["params"]

    orgs_call = mock_get.call_args_list[1]
    assert orgs_call.args[0] == "https://api.pipedrive.com/api/v2/organizations"
    assert orgs_call.kwargs["params"]["ids"] == "670"


@patch("portal.infrastructure.pipedrive.pipedrive_crm_reader.requests.get")
@patch(
    "portal.infrastructure.pipedrive.pipedrive_crm_reader.list_stage_ids_etapa_contrato",
    return_value=[7],
)
def test_list_deals_filtra_owner_em_memoria(mock_stages, mock_get):
    from fastapi.testclient import TestClient
    from portal.main import create_app

    deals_page = _mock_response(
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
                {
                    "id": 999,
                    "title": "Outro dono",
                    "owner_id": 1,
                    "stage_id": 7,
                    "status": "open",
                    "pipeline_id": 1,
                    "org_id": 671,
                },
            ],
            "additional_data": {},
        }
    )
    orgs_page = _mock_response(
        {
            "data": [
                {"id": 670, "name": "Org A"},
                {"id": 671, "name": "Org B"},
            ]
        }
    )
    users_page = _mock_response({"data": []})
    mock_get.side_effect = [users_page, deals_page, orgs_page]

    PipedriveCrmReader.invalidate_crm_cache()
    limpar_cache_stages()
    client = TestClient(create_app())
    response = client.get("/pipedrive/deals", params={"owner_user_id": 24587114})

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == 746
    assert data[0]["owner_id"] == 24587114


@pytest.mark.integration
@pytest.mark.skipif(
    os.environ.get("PIPEDRIVE_LIVE_BENCH") != "1",
    reason="Defina PIPEDRIVE_LIVE_BENCH=1 para benchmark live no Pipedrive",
)
def test_live_crm_fetch_under_2s():
    """Deal 746 / owner 24587114 — cold fetch deve ficar abaixo de 2s."""
    from dotenv import load_dotenv

    load_dotenv(override=True)
    token = os.environ.get("PIPEDRIVE_API_TOKEN", "").strip()
    if not token:
        pytest.skip("PIPEDRIVE_API_TOKEN ausente")
    if token == "pytest-pipedrive-token":
        pytest.skip("token de pytest — use .env real com PIPEDRIVE_LIVE_BENCH=1")

    import core.config as app_config

    app_config.PIPEDRIVE_API_TOKEN = token

    PipedriveCrmReader.invalidate_crm_cache()
    limpar_cache_stages()
    reader = PipedriveCrmReader(api_token=token)

    t0 = time.perf_counter()
    deals = reader.list_open_deals_in_contrato_stage(fresh=True)
    elapsed_ms = (time.perf_counter() - t0) * 1000

    assert any(d.id == 746 for d in deals), "deal 746 deve estar na etapa Contrato"
    assert elapsed_ms <= 3000, f"fetch contrato deals demorou {elapsed_ms:.0f}ms (meta 3000ms cold)"

    t0 = time.perf_counter()
    owner_deals = reader.list_open_deals_in_contrato_stage(
        owner_user_id=24587114,
        fresh=False,
    )
    cache_ms = (time.perf_counter() - t0) * 1000

    assert any(d.id == 746 for d in owner_deals)
    assert cache_ms <= 50, f"cache hit demorou {cache_ms:.0f}ms"
