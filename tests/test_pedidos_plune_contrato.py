"""Testes: números de pedido Plune no contrato Word."""

from __future__ import annotations

from core.plune_pedido import (
    TIPO_PEDIDO_IMPLANTACAO,
    TIPO_PEDIDO_RECORRENTE,
    extrair_numeros_pedidos_plune,
    formatar_linha_pedidos_plune_contrato,
)


def test_extrair_numeros_pedidos():
    result = {
        "pedidos": [
            {"tipo": TIPO_PEDIDO_IMPLANTACAO, "pedido_id": "1001", "status": "created"},
            {"tipo": TIPO_PEDIDO_RECORRENTE, "pedido_id": "1002", "status": "created"},
        ]
    }
    assert extrair_numeros_pedidos_plune(result) == {
        "implantacao": "1001",
        "recorrente": "1002",
    }


def test_formatar_linha_pedidos():
    linha = formatar_linha_pedidos_plune_contrato(
        {"implantacao": "1001", "recorrente": "1002"}
    )
    assert "Implantação: 1001" in linha
    assert "Recorrente: 1002" in linha


def test_formatar_linha_vazia():
    assert formatar_linha_pedidos_plune_contrato({}) == "—"
