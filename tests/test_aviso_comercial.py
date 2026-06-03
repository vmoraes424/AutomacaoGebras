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


@patch("core.aviso_comercial.smtplib.SMTP")
@patch("core.aviso_comercial._smtp_configurado", return_value=True)
def test_enviar_aviso_smtp(_mock_cfg, mock_smtp_cls):
    smtp = MagicMock()
    mock_smtp_cls.return_value.__enter__.return_value = smtp
    deal = {"id": 1, "title": "T", "custom_fields": {}}
    assert enviar_aviso_comercial_etapa1(deal, {"implantacao": "100"}) is True
    smtp.sendmail.assert_called_once()


@patch("core.aviso_comercial._smtp_configurado", return_value=False)
def test_enviar_aviso_sem_smtp_nao_levanta(_mock_cfg):
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
        assert [s["name"] for s in seq] == ["Consultor"]
        assert all(s["name"] != "Comercial" for s in seq)
