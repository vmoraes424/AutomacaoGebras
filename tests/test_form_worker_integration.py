"""Integracao worker + FORMULARIO_WEB_ENABLED (Fase 5)."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from core.automacao_contrato import processar_deals_pendentes
from core.form_deal_adapter import DealFormSnapshot

FIXTURES = Path(__file__).resolve().parent / "fixtures" / "formulario_v1"
DEAL = {
    "id": 999001,
    "title": "Golden G1",
    "update_time": "2026-06-10T12:00:00.000Z",
}


def _form_g1() -> dict:
    return json.loads((FIXTURES / "form_payload_v1_g1.json").read_text(encoding="utf-8"))


def _worker_patches():
    """Mocks minimos para um ciclo de processar_deals_pendentes."""
    ts = datetime(2026, 6, 10, 12, 0, tzinfo=timezone.utc)
    return (
        patch("core.automacao_contrato.limpar_templates_orfaos_runtime"),
        patch(
            "core.automacao_contrato.buscar_deals_etapa_contrato",
            return_value=[DEAL],
        ),
        patch(
            "core.automacao_contrato.carregar_deals_processados",
            return_value=(set(), set()),
        ),
        patch("core.automacao_contrato.buscar_por_deal_id", return_value=None),
        patch("core.automacao_contrato._parse_deal_timestamp_utc", return_value=ts),
        patch("core.automacao_contrato.DATA_INICIO_SCRIPT", None),
    )


@patch("core.automacao_contrato.fill_contract", return_value="/tmp/x.docx")
@patch("core.automacao_contrato.criar_pedido_plune", return_value={"pedidos": []})
@patch("core.automacao_contrato.validar_deal_para_automacao")
@patch("core.automacao_contrato.FORMULARIO_WEB_ENABLED", False)
def test_flag_off_valida_deal_legado(mock_validar, mock_plune, _fill):
    patches = _worker_patches()
    for p in patches:
        p.start()
    try:
        processar_deals_pendentes()
    finally:
        for p in patches:
            p.stop()
    mock_validar.assert_called_once()
    mock_plune.assert_called_once()
    deal_arg = mock_validar.call_args[0][0]
    assert deal_arg["id"] == DEAL["id"]


@patch("core.automacao_contrato.fill_contract", return_value="/tmp/x.docx")
@patch("core.automacao_contrato.criar_pedido_plune", return_value={"pedidos": []})
@patch("core.automacao_contrato.validar_deal_para_automacao")
@patch("core.automacao_contrato.FORMULARIO_WEB_ENABLED", True)
@patch("core.form_deal_adapter.load_deal_form_from_db", return_value=None)
def test_flag_on_sem_form_nao_chama_plune_nem_valida(
    _load, mock_validar, mock_plune, _fill
):
    patches = _worker_patches()
    for p in patches:
        p.start()
    try:
        processar_deals_pendentes()
    finally:
        for p in patches:
            p.stop()
    mock_validar.assert_not_called()
    mock_plune.assert_not_called()


def test_flag_on_form_validated_usa_merge_pula_validacao_pipe():
    from contextlib import ExitStack

    with ExitStack() as stack:
        for p in _worker_patches():
            stack.enter_context(p)
        stack.enter_context(patch("core.automacao_contrato.FORMULARIO_WEB_ENABLED", True))
        stack.enter_context(
            patch(
                "core.form_deal_adapter.load_deal_form_from_db",
                return_value=DealFormSnapshot(999001, "validated", "v1", _form_g1()),
            )
        )
        mock_validar = stack.enter_context(
            patch("core.automacao_contrato.validar_deal_para_automacao")
        )
        mock_plune = stack.enter_context(
            patch(
                "core.automacao_contrato.criar_pedido_plune",
                return_value={"pedidos": []},
            )
        )
        stack.enter_context(patch("core.automacao_contrato._fluxo_hub_pre_aprovacao"))
        stack.enter_context(
            patch("core.automacao_contrato.fill_contract", return_value="/tmp/x.docx")
        )
        stack.enter_context(
            patch("core.automacao_contrato.extrair_signatarios", return_value=[])
        )
        stack.enter_context(
            patch("core.automacao_contrato.baixar_docx_contrato_padrao_deal", return_value=None)
        )
        stack.enter_context(
            patch("core.automacao_contrato.notificar_validacao_aprovada", return_value=False)
        )
        stack.enter_context(patch("core.automacao_contrato.DEV_PULAR_CLICKSIGN", True))
        stack.enter_context(patch("core.automacao_contrato.salvar_deal_processado"))
        stack.enter_context(patch("core.automacao_contrato.enviar_aviso_comercial_etapa1"))
        processar_deals_pendentes()

    mock_validar.assert_not_called()
    mock_plune.assert_called_once()
    assert str(mock_plune.call_args[0][0]) == "999001"


@patch("core.automacao_contrato.validar_deal_para_automacao")
@patch("core.automacao_contrato.FORMULARIO_WEB_ENABLED", False)
def test_deal_ja_processado_nao_reprocessa(mock_validar):
    patches = list(_worker_patches())
    patches[2] = patch(
        "core.automacao_contrato.carregar_deals_processados",
        return_value=( {"999001"}, set()),
    )
    for p in patches:
        p.start()
    try:
        processar_deals_pendentes()
    finally:
        for p in patches:
            p.stop()
    mock_validar.assert_not_called()


def test_gate_g4_formulario_web_enabled_lido_do_env(monkeypatch):
    monkeypatch.setenv("FORMULARIO_WEB_ENABLED", "false")
    from core.config import _env_bool

    assert _env_bool("FORMULARIO_WEB_ENABLED", True) is False
