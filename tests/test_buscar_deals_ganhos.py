"""Testes: paginação de deals ganhos no Pipedrive."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from core.automacao_contrato import buscar_deals_ganhos


@patch("core.automacao_contrato.requests.get")
def test_buscar_deals_ganhos_pagina_ate_acabar_cursor(mock_get):
    page1 = MagicMock()
    page1.status_code = 200
    page1.json.return_value = {
        "data": [{"id": 1, "won_time": "2026-05-29T12:00:00Z"}],
        "additional_data": {"next_cursor": "cursor-2"},
    }
    page2 = MagicMock()
    page2.status_code = 200
    page2.json.return_value = {
        "data": [{"id": 1052, "won_time": "2026-05-29T20:21:56Z"}],
        "additional_data": {},
    }
    mock_get.side_effect = [page1, page2]

    deals = buscar_deals_ganhos()

    assert len(deals) == 2
    assert deals[0]["id"] == 1
    assert deals[1]["id"] == 1052
    assert mock_get.call_count == 2
    assert mock_get.call_args_list[1].kwargs["params"]["cursor"] == "cursor-2"
