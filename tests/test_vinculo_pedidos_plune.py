"""Vínculo implantação ↔ recorrente (PedidoOriginal)."""

from __future__ import annotations

from unittest.mock import patch

from core.plune_pedido import (
    TIPO_PEDIDO_IMPLANTACAO,
    TIPO_PEDIDO_RECORRENTE,
    vincular_pedidos_plune_implantacao_recorrente,
)


@patch("core.plune_pedido._buscar_observacao_pedido_plune", return_value="OBS ATUAL")
@patch("core.plune_pedido._atualizar_campos_pedido_plune")
def test_vincula_ambos_sentidos(mock_update, _mock_busca_obs):
    resultados = [
        {"tipo": TIPO_PEDIDO_IMPLANTACAO, "pedido_id": "6801", "status": "created"},
        {"tipo": TIPO_PEDIDO_RECORRENTE, "pedido_id": "6800", "status": "created"},
    ]
    vincular_pedidos_plune_implantacao_recorrente(resultados, cliente_id="1001")

    assert mock_update.call_count == 4
    mock_update.assert_any_call("6801", "1001", {"PedidoOriginal": "6800"})
    mock_update.assert_any_call("6800", "1001", {"PedidoOriginal": "6801"})
    # também complementa Observacao nos dois pedidos
    mock_update.assert_any_call(
        "6801",
        "1001",
        {
            "Observacao": "OBS ATUAL\n\nPEDIDOS VINCULADOS:\nImplantação: 6801\nRecorrente: 6800"
        },
    )
    mock_update.assert_any_call(
        "6800",
        "1001",
        {
            "Observacao": "OBS ATUAL\n\nPEDIDOS VINCULADOS:\nImplantação: 6801\nRecorrente: 6800"
        },
    )


@patch("core.plune_pedido._atualizar_campos_pedido_plune")
def test_sem_implantacao_nao_atualiza(mock_update):
    resultados = [
        {"tipo": TIPO_PEDIDO_RECORRENTE, "pedido_id": "6800", "status": "created"},
    ]
    vincular_pedidos_plune_implantacao_recorrente(resultados, cliente_id="1001")
    mock_update.assert_not_called()
