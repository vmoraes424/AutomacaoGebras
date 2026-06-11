"""Fase 6/7 — smoke: portal fora do ar nao bloqueia worker (flag off)."""

from __future__ import annotations

from unittest.mock import patch

from core.automacao_contrato import processar_deals_pendentes


@patch("core.automacao_contrato.FORMULARIO_WEB_ENABLED", False)
@patch(
    "core.automacao_contrato.listar_deal_ids_formulario_aguardando_worker",
    return_value=[999001],
)
@patch("core.automacao_contrato.buscar_deal_por_id")
def test_portal_desligado_worker_ignora_fila_form(mock_buscar, _listar):
    processar_deals_pendentes()
    mock_buscar.assert_not_called()
