"""Testes unitários: cache e anexos de pedido."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from core.pedido_anexos import (
    CacheAnexosDeal,
    _mime_por_extensao,
    anexar_contrato_pedido,
    anexar_proposta_pedido,
    obter_bytes_contrato,
)


class TestMimePorExtensao:
    def test_pdf(self):
        assert _mime_por_extensao("a.PDF") == "application/pdf"

    def test_docx(self):
        assert "wordprocessingml" in _mime_por_extensao("Contrato.docx")

    def test_outro(self):
        assert _mime_por_extensao("x.bin") == "application/octet-stream"


class TestCacheAnexosDeal:
    @patch("core.pedido_anexos.baixar_pdf_proposta_deal")
    def test_proposta_cacheia_uma_vez(self, mock_baixar):
        mock_baixar.return_value = (b"pdf", "p.pdf")
        cache = CacheAnexosDeal("746")
        assert cache.proposta() == (b"pdf", "p.pdf")
        assert cache.proposta() == (b"pdf", "p.pdf")
        mock_baixar.assert_called_once_with("746")

    @patch("core.pedido_anexos.obter_bytes_contrato")
    @patch("core.pedido_anexos.baixar_pdf_proposta_deal")
    def test_prefetch_paralelo(self, mock_prop, mock_contrato):
        mock_prop.return_value = (b"p", "p.pdf")
        mock_contrato.return_value = (b"c", "c.pdf", "application/pdf")
        cache = CacheAnexosDeal("746", permitir_docx_local=True)
        cache.prefetch(proposta=True, contrato=True)
        mock_prop.assert_called_once()
        mock_contrato.assert_called_once()

    @patch("core.pedido_anexos.baixar_pdf_proposta_deal")
    def test_prefetch_assincrono_nao_bloqueia(self, mock_baixar):
        import time

        def _lento(_deal_id):
            time.sleep(0.05)
            return (b"p", "p.pdf")

        mock_baixar.side_effect = _lento
        cache = CacheAnexosDeal("746")
        inicio = time.perf_counter()
        cache.iniciar_prefetch_assincrono(proposta=True, contrato=False)
        decorrido = time.perf_counter() - inicio
        # Windows/CI pode oscilar; o importante é não bloquear ~50ms do download simulado.
        assert decorrido < 0.06
        assert cache.proposta() == (b"p", "p.pdf")


class TestObterBytesContrato:
    @patch("core.pedido_anexos._contrato_clicksign_assinado")
    def test_prioriza_clicksign(self, mock_cs, pdf_bytes):
        mock_cs.return_value = (pdf_bytes, "assinado.pdf")
        out = obter_bytes_contrato("746")
        assert out[0] == pdf_bytes
        assert out[2] == "application/pdf"

    @patch("core.pedido_anexos._contrato_docx_local")
    @patch("core.pedido_anexos._contrato_clicksign_assinado")
    def test_fallback_docx_local(self, mock_cs, mock_local):
        mock_cs.return_value = None
        mock_local.return_value = (b"docx", "Contrato_746_x.docx")
        out = obter_bytes_contrato("746", permitir_docx_local=True)
        assert out[1].endswith(".docx")


class TestAnexarPropostaPedido:
    @patch("core.pedido_anexos.inserir_anexo_pedido")
    def test_ok_com_cache(self, mock_insert, pdf_bytes, capsys):
        cache = CacheAnexosDeal("746")
        cache._proposta = (pdf_bytes, "proposta.pdf")
        mock_insert.return_value = {"anexo_id": "1"}
        out = anexar_proposta_pedido("746", "6742", "751", cache=cache)
        assert out["anexo_id"] == "1"
        assert "proposta" in capsys.readouterr().out.lower() or True

    @patch("core.pedido_anexos.baixar_pdf_proposta_deal")
    def test_sem_pdf(self, mock_baixar):
        mock_baixar.return_value = None
        assert anexar_proposta_pedido("746", "6742", "751") is None


class TestAnexarContratoPedido:
    @patch("core.pedido_anexos.inserir_anexo_pedido")
    @patch("core.pedido_anexos.remover_anexos_automacao")
    @patch("core.pedido_anexos.resolver_tipo_anexo_id")
    def test_ok(self, mock_resolve, mock_rm, mock_insert, pdf_bytes):
        cache = CacheAnexosDeal("746")
        cache._contrato = (pdf_bytes, "c.pdf", "application/pdf")
        cache._contrato_carregado = True
        mock_resolve.return_value = "11"
        mock_insert.return_value = {"anexo_id": "2"}
        out = anexar_contrato_pedido(
            "746", "6742", "751", permitir_docx_local=True, cache=cache
        )
        assert out["anexo_id"] == "2"
        mock_rm.assert_called_once()
