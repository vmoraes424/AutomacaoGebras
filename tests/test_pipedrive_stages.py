"""Testes: etapas do funil Pipedrive (Contrato dispara; ganho pós-assinatura)."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from core import pipedrive_stages as stages
from core.gebras_defaults import (
    PIPEDRIVE_STAGE_CONTRATO_NOME,
    PIPEDRIVE_STAGE_NEGOCIACAO_NOME,
)


@pytest.fixture(autouse=True)
def _limpar_cache():
    stages.limpar_cache_stages()
    yield
    stages.limpar_cache_stages()


def test_normalizar_nome_etapa_ignora_acentos_e_maiusculas():
    assert stages._normalizar_nome_etapa("Negociação") == stages._normalizar_nome_etapa(
        "NEGOCIACAO"
    )


@patch("core.pipedrive_stages.requests.get")
def test_deal_ja_em_negociacao_nao_move(mock_get: MagicMock):
    mock_get.return_value = MagicMock(
        ok=True,
        status_code=200,
        json=lambda: {
            "data": [
                {"id": 5, "name": "Proposta"},
                {"id": 6, "name": "Negociação"},
                {"id": 7, "name": "Contrato"},
            ]
        },
    )
    deal = {"id": 100, "pipeline_id": 1, "stage_id": 6}
    assert stages.deal_esta_em_negociacao(deal) is True
    with patch("core.pipedrive_stages.requests.patch") as mock_patch:
        assert stages.garantir_deal_em_etapa_negociacao(deal) is False
        mock_patch.assert_not_called()


@patch("core.pipedrive_stages.requests.get")
@patch("core.pipedrive_stages.requests.patch")
def test_deal_fora_de_negociacao_move_para_etapa(
    mock_patch: MagicMock, mock_get: MagicMock
):
    mock_get.return_value = MagicMock(
        ok=True,
        status_code=200,
        json=lambda: {
            "data": [
                {"id": 5, "name": "Proposta"},
                {"id": 6, "name": "Negociação"},
                {"id": 7, "name": "Contrato"},
            ]
        },
    )
    mock_patch.return_value = MagicMock(ok=True, status_code=200)
    deal = {"id": 200, "pipeline_id": 1, "stage_id": 7}
    assert stages.garantir_deal_em_etapa_negociacao(deal) is True
    mock_patch.assert_called_once()
    call = mock_patch.call_args
    assert call[0][0].endswith("/deals/200")
    assert call[1]["json"] == {"stage_id": 6}
    assert deal["stage_id"] == 6


@patch("core.pipedrive_stages.requests.get")
def test_etapa_negociacao_ausente_no_pipeline_levanta_erro(mock_get: MagicMock):
    mock_get.return_value = MagicMock(
        ok=True,
        status_code=200,
        json=lambda: {"data": [{"id": 1, "name": "Proposta"}]},
    )
    deal = {"id": 300, "pipeline_id": 99, "stage_id": 1}
    with pytest.raises(RuntimeError, match=PIPEDRIVE_STAGE_NEGOCIACAO_NOME):
        stages.garantir_deal_em_etapa_negociacao(deal)


@patch("core.pipedrive_stages.requests.get")
@patch("core.pipedrive_stages.requests.patch")
def test_deal_move_para_etapa_contrato_apos_assinatura(
    mock_patch: MagicMock, mock_get: MagicMock
):
    mock_get.return_value = MagicMock(
        ok=True,
        status_code=200,
        json=lambda: {
            "data": [
                {"id": 5, "name": "Proposta"},
                {"id": 6, "name": "Negociação"},
                {"id": 7, "name": "Contrato"},
            ]
        },
    )
    mock_patch.return_value = MagicMock(ok=True, status_code=200)
    deal = {"id": 400, "pipeline_id": 1, "stage_id": 6}
    assert stages.garantir_deal_em_etapa_contrato(deal) is True
    mock_patch.assert_called_once()
    call = mock_patch.call_args
    assert call[0][0].endswith("/deals/400")
    assert call[1]["json"] == {"stage_id": 7}
    assert deal["stage_id"] == 7


@patch("core.pipedrive_stages.requests.get")
def test_deal_ja_em_contrato_nao_move(mock_get: MagicMock):
    mock_get.return_value = MagicMock(
        ok=True,
        status_code=200,
        json=lambda: {
            "data": [
                {"id": 6, "name": "Negociação"},
                {"id": 7, "name": "Contrato"},
            ]
        },
    )
    deal = {"id": 500, "pipeline_id": 1, "stage_id": 7}
    with patch("core.pipedrive_stages.requests.patch") as mock_patch:
        assert stages.garantir_deal_em_etapa_contrato(deal) is False
        mock_patch.assert_not_called()


@patch("core.pipedrive_stages.requests.get")
def test_etapa_contrato_ausente_no_pipeline_levanta_erro(mock_get: MagicMock):
    mock_get.return_value = MagicMock(
        ok=True,
        status_code=200,
        json=lambda: {"data": [{"id": 1, "name": "Proposta"}]},
    )
    deal = {"id": 600, "pipeline_id": 99, "stage_id": 1}
    with pytest.raises(RuntimeError, match=PIPEDRIVE_STAGE_CONTRATO_NOME):
        stages.garantir_deal_em_etapa_contrato(deal)


@patch("core.pipedrive_stages.requests.get")
def test_deal_esta_em_etapa_contrato(mock_get: MagicMock):
    mock_get.return_value = MagicMock(
        ok=True,
        status_code=200,
        json=lambda: {
            "data": [
                {"id": 6, "name": "Negociação"},
                {"id": 7, "name": "Contrato"},
            ]
        },
    )
    assert stages.deal_esta_em_etapa_contrato(
        {"id": 1, "pipeline_id": 1, "stage_id": 7}
    )
    assert not stages.deal_esta_em_etapa_contrato(
        {"id": 2, "pipeline_id": 1, "stage_id": 6}
    )


@patch("core.pipedrive_stages.requests.patch")
def test_marcar_deal_como_ganho(mock_patch: MagicMock):
    mock_patch.return_value = MagicMock(
        ok=True,
        status_code=200,
        json=lambda: {"data": {"id": 800, "status": "won"}},
    )
    stages.marcar_deal_como_ganho("800")
    mock_patch.assert_called_once()
    assert mock_patch.call_args.kwargs["json"] == {"status": "won"}
