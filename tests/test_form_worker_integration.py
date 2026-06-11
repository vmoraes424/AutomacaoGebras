"""Integracao worker + fila deal_forms (formulario web)."""

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
    "status": "open",
    "stage_id": 7,
    "pipeline_id": 1,
    "update_time": "2026-06-10T12:00:00.000Z",
}


def _form_g1() -> dict:
    return json.loads((FIXTURES / "form_payload_v1_g1.json").read_text(encoding="utf-8"))


def _worker_patches(*, deal_ids=None):
    """Mocks minimos para um ciclo de processar_deals_pendentes."""
    ts = datetime(2026, 6, 10, 12, 0, tzinfo=timezone.utc)
    ids = deal_ids if deal_ids is not None else [999001]
    return (
        patch("core.automacao_contrato.limpar_templates_orfaos_runtime"),
        patch(
            "core.automacao_contrato.listar_deal_ids_formulario_aguardando_worker",
            return_value=ids,
        ),
        patch(
            "core.automacao_contrato.buscar_deal_por_id",
            return_value=DEAL if ids else None,
        ),
        patch(
            "core.automacao_contrato.carregar_deals_processados",
            return_value=(set(), set()),
        ),
        patch("core.automacao_contrato.buscar_por_deal_id", return_value=None),
        patch("core.automacao_contrato._parse_deal_timestamp_utc", return_value=ts),
        patch("core.automacao_contrato.atualizar_deal_form_status"),
        patch(
            "core.automacao_contrato.deal_elegivel_formulario_contrato",
            return_value=True,
        ),
    )


@patch("core.automacao_contrato.fill_contract", return_value="/tmp/x.docx")
@patch("core.automacao_contrato.criar_pedido_plune", return_value={"pedidos": []})
def test_sem_form_na_fila_nao_processa(mock_plune, _fill):
    patches = _worker_patches(deal_ids=[])
    for p in patches:
        p.start()
    try:
        processar_deals_pendentes()
    finally:
        for p in patches:
            p.stop()
    mock_plune.assert_not_called()


@patch("core.automacao_contrato.fill_contract", return_value="/tmp/x.docx")
@patch("core.automacao_contrato.criar_pedido_plune", return_value={"pedidos": []})
@patch("core.form_deal_adapter.load_deal_form_from_db", return_value=None)
def test_form_ausente_no_adaptador_nao_chama_plune(_load, mock_plune, _fill):
    patches = _worker_patches()
    for p in patches:
        p.start()
    try:
        processar_deals_pendentes()
    finally:
        for p in patches:
            p.stop()
    mock_plune.assert_not_called()


@patch("core.automacao_contrato.FORMULARIO_WEB_ENABLED", True)
def test_form_validated_usa_merge_e_processa():
    from contextlib import ExitStack

    with ExitStack() as stack:
        for p in _worker_patches():
            stack.enter_context(p)
        stack.enter_context(
            patch(
                "core.form_deal_adapter.load_deal_form_from_db",
                return_value=DealFormSnapshot(999001, "validated", "v1", _form_g1()),
            )
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
        stack.enter_context(patch("core.automacao_contrato.DEV_PULAR_CLICKSIGN", True))
        stack.enter_context(
            patch("core.automacao_contrato._registrar_deal_processado_worker")
        )
        stack.enter_context(patch("core.automacao_contrato.enviar_aviso_comercial_etapa1"))
        processar_deals_pendentes()

    mock_plune.assert_called_once()
    assert str(mock_plune.call_args[0][0]) == "999001"


@patch("core.automacao_contrato.FORMULARIO_WEB_ENABLED", False)
@patch(
    "core.automacao_contrato.listar_deal_ids_formulario_aguardando_worker",
    return_value=[999001],
)
@patch("core.automacao_contrato.buscar_deal_por_id")
def test_flag_off_worker_nao_consume_fila_form(mock_buscar, _listar):
    processar_deals_pendentes()
    mock_buscar.assert_not_called()


@patch("core.automacao_contrato.criar_pedido_plune", return_value={"pedidos": []})
def test_deal_ja_processado_nao_reprocessa(mock_plune):
    patches = list(_worker_patches())
    patches[3] = patch(
        "core.automacao_contrato.carregar_deals_processados",
        return_value=({"999001"}, set()),
    )
    for p in patches:
        p.start()
    try:
        processar_deals_pendentes()
    finally:
        for p in patches:
            p.stop()
    mock_plune.assert_not_called()
