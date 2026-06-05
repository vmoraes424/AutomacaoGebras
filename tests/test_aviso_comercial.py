"""Testes: aviso informativo comercial e signatários."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from core.aviso_comercial import enviar_aviso_comercial_etapa1, montar_aviso_comercial
from core.plune_pedido import TIPO_PEDIDO_IMPLANTACAO, TIPO_PEDIDO_RECORRENTE
from core.pipedrive_fields import (
    FIELD_EMAIL_CONSULTOR_GEBRAS,
    FIELD_NOME_CLIENTE,
    extrair_signatarios,
)


def test_montar_aviso_inclui_pedidos_plune():
    deal = {"id": 746, "title": "Cliente X", "custom_fields": {FIELD_NOME_CLIENTE: "Cliente X"}}
    assunto, texto, html = montar_aviso_comercial(
        deal,
        {
            TIPO_PEDIDO_IMPLANTACAO: "6835",
            TIPO_PEDIDO_RECORRENTE: "6834",
        },
    )
    assert "6835" in texto
    assert "6834" in texto
    assert "Implantação: 6835" in texto
    assert "Recorrente: 6834" in html
    assert "746" in assunto


@patch("core.aviso_comercial.GraphEmailSender")
@patch("core.aviso_comercial._graph_configurado", return_value=True)
def test_enviar_aviso_graph(_mock_graph_cfg, mock_sender_cls):
    sender = MagicMock()
    mock_sender_cls.return_value = sender
    deal = {"id": 1, "title": "T", "custom_fields": {}}
    assert enviar_aviso_comercial_etapa1(deal, {"implantacao": "100"}) is True
    sender.send.assert_called_once()


@patch("core.aviso_comercial._graph_configurado", return_value=False)
def test_enviar_aviso_sem_graph_nao_levanta(_mock_graph_cfg):
    assert enviar_aviso_comercial_etapa1({"id": 1, "custom_fields": {}}, {}) is False


class TestExtrairSignatariosSemComercial:
    @patch("core.pipedrive_fields._enum_option_labels_for_field")
    def test_apenas_quatro_signatarios(self, mock_enum_labels):
        mock_enum_labels.side_effect = lambda code: {
            FIELD_EMAIL_CONSULTOR_GEBRAS: {"84": "consultor@gebras.com"},
        }.get(code, {})
        seq = extrair_signatarios(
            {"id": 1, "custom_fields": {FIELD_EMAIL_CONSULTOR_GEBRAS: "84"}}
        )
        assert [s["papel"] for s in seq] == ["Consultor"]
        assert all(s["papel"] != "Comercial" for s in seq)
