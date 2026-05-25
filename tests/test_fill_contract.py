"""Testes: contexto do contrato (fill_contract)."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from core.automacao_contrato import fill_contract
from core.plune_pedido import TIPO_PEDIDO_IMPLANTACAO, TIPO_PEDIDO_RECORRENTE
from core.pipedrive_fields import (
    FIELD_GESTAO_ACL,
    FIELD_INDICADORES_QUALIDADE,
    FIELD_QTD_SOLE,
    FIELD_QUALIDADE_ENERGIA,
)


@patch("core.automacao_contrato.buscar_parceiro_plune_por_documento")
@patch("core.automacao_contrato.DocxTemplate")
@patch("core.automacao_contrato.os.path.exists", return_value=True)
def test_sole_consultoria_no_contexto(mock_exists, mock_docx_cls, mock_parceiro):
    deal = {
        "id": 746,
        "title": "Teste",
        "custom_fields": {
            FIELD_QUALIDADE_ENERGIA: 6,
            FIELD_QTD_SOLE: 4,
            FIELD_GESTAO_ACL: 6,
            FIELD_INDICADORES_QUALIDADE: 5,
        },
    }
    mock_parceiro.return_value = None
    doc = MagicMock()
    mock_docx_cls.return_value = doc

    fill_contract(deal)

    contexto = doc.render.call_args[0][0]
    assert contexto["sole_consultoria"] == "6"
    assert contexto["qualidade_energia"] == "5"
    assert contexto["sole_web"] == "4"
    assert "quatro" not in contexto["sole_web"].lower()


@patch("core.automacao_contrato.buscar_parceiro_plune_por_documento")
@patch("core.automacao_contrato.DocxTemplate")
@patch("core.automacao_contrato.os.path.exists", return_value=True)
def test_numeros_pedidos_no_contexto(mock_exists, mock_docx_cls, mock_parceiro):
    deal = {"id": 746, "title": "Teste", "custom_fields": {}}
    mock_parceiro.return_value = None
    doc = MagicMock()
    mock_docx_cls.return_value = doc

    fill_contract(
        deal,
        numeros_pedidos={
            TIPO_PEDIDO_IMPLANTACAO: "9001",
            TIPO_PEDIDO_RECORRENTE: "9002",
        },
    )

    contexto = doc.render.call_args[0][0]
    assert "9001" in contexto["numeros_pedidos"]
    assert "9002" in contexto["numeros_pedidos"]
