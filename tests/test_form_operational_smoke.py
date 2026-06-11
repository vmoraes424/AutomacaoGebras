"""Fase 6/7 — smoke: portal fora do ar nao bloqueia worker (flag off)."""

from __future__ import annotations

from unittest.mock import patch

from core.automacao_config import AutomacaoConfig
from core.automacao_contrato import processar_deals_pendentes


@patch(
    "core.automacao_contrato.get_automacao_config",
    return_value=AutomacaoConfig(formulario_web_enabled=False),
)
@patch(
    "core.automacao_contrato.listar_deal_ids_formulario_aguardando_worker",
    return_value=[999001],
)
@patch("core.automacao_contrato.buscar_deal_por_id")
def test_portal_desligado_worker_ignora_fila_form(_cfg, mock_buscar, _listar):
    processar_deals_pendentes()
    mock_buscar.assert_not_called()
