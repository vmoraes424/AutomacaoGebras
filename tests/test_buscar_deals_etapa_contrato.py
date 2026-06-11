"""Testes: deals abertos na etapa Contrato no Pipedrive."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from core.pipedrive_stages import buscar_deals_etapa_contrato


@patch("core.pipedrive_stages.deal_esta_em_etapa_contrato")
@patch("core.pipedrive_stages.requests.get")
def test_buscar_deals_etapa_contrato_pagina_e_filtra(mock_get, mock_em_contrato):
    mock_em_contrato.side_effect = lambda deal: deal.get("id") in (2, 1052)

    page1 = MagicMock()
    page1.status_code = 200
    page1.json.return_value = {
        "data": [
            {"id": 1, "status": "open", "stage_id": 5},
            {"id": 2, "status": "open", "stage_id": 7},
        ],
        "additional_data": {"next_cursor": "cursor-2"},
    }
    page2 = MagicMock()
    page2.status_code = 200
    page2.json.return_value = {
        "data": [{"id": 1052, "status": "open", "stage_id": 7}],
        "additional_data": {},
    }
    mock_get.side_effect = [page1, page2]

    deals = buscar_deals_etapa_contrato()

    assert len(deals) == 2
    assert deals[0]["id"] == 2
    assert deals[1]["id"] == 1052
    assert mock_get.call_count == 2
    assert mock_get.call_args_list[0].kwargs["params"]["status"] == "open"
    assert mock_get.call_args_list[1].kwargs["params"]["cursor"] == "cursor-2"
