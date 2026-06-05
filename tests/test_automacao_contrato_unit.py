"""Testes unitários: ClicksignClient (sem API real)."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from core.automacao_contrato import ClicksignClient, _retomar_fluxo_interrompido


@pytest.fixture
def cliente():
    return ClicksignClient("https://sandbox.clicksign.com/api/v3", "token-teste")


class TestBaixarPdfAssinado:
    def test_sem_documentos(self, cliente):
        with patch.object(cliente, "_request") as mock_req:
            resp = MagicMock(ok=True, status_code=200)
            resp.json.return_value = {"data": []}
            mock_req.return_value = resp
            assert cliente.baixar_pdf_assinado("env-1") is None

    def test_baixa_primeiro_com_signed_url(self, cliente, pdf_bytes):
        with patch.object(cliente, "_request") as mock_req:
            list_resp = MagicMock(ok=True)
            list_resp.json.return_value = {"data": [{"id": "doc-1"}]}
            doc_resp = MagicMock(ok=True)
            doc_resp.json.return_value = {
                "data": {
                    "attributes": {
                        "filename": "contrato.docx",
                        "downloads": {
                            "signed_file_url": "https://files.example/signed.pdf",
                        },
                    }
                }
            }
            mock_req.side_effect = [list_resp, doc_resp]

            with patch("core.automacao_contrato.requests.get") as mock_get:
                bin_resp = MagicMock(ok=True, status_code=200)
                bin_resp.content = pdf_bytes
                mock_get.return_value = bin_resp
                conteudo, nome = cliente.baixar_pdf_assinado("env-1")
                assert conteudo == pdf_bytes
                assert nome == "contrato.pdf"

    def test_url_relativa(self, cliente, pdf_bytes):
        with patch.object(cliente, "_request") as mock_req:
            list_resp = MagicMock(ok=True)
            list_resp.json.return_value = {"data": [{"id": "d1"}]}
            doc_resp = MagicMock(ok=True)
            doc_resp.json.return_value = {
                "data": {
                    "attributes": {
                        "filename": "x.pdf",
                        "downloads": {"signed_file_url": "/downloads/abc"},
                    }
                }
            }
            mock_req.side_effect = [list_resp, doc_resp]
            with patch("core.automacao_contrato.requests.get") as mock_get:
                bin_resp = MagicMock(ok=True, content=pdf_bytes)
                mock_get.return_value = bin_resp
                cliente.baixar_pdf_assinado("env-1")
                url_chamada = mock_get.call_args[0][0]
                assert url_chamada.startswith("https://sandbox.clicksign.com")


class TestImportsModuloPrincipal:
    def test_import_sem_ciclo(self):
        import core.automacao_contrato  # noqa: F401
        import core.plune_pedido  # noqa: F401
        import core.pedido_anexos  # noqa: F401


class TestRetomarFluxoInterrompido:
    def test_retoma_quando_ha_envelope_pendente(self):
        assert _retomar_fluxo_interrompido(
            {"envelope_id": "9091c56e-f326-457f-a762-41a3be90db44"}
        )

    def test_retoma_dev_sem_clicksign(self):
        assert _retomar_fluxo_interrompido(
            {"envelope_id": "sem-envelope-746", "pedidos_plune_criados": 1}
        )

    def test_nao_retoma_primeira_vez(self):
        assert not _retomar_fluxo_interrompido(None)


class TestCancelEnvelope:
    def test_cancel_envelope_faz_patch(self, cliente):
        with patch.object(cliente, "_request") as mock_req:
            resp = MagicMock(ok=True, status_code=200)
            mock_req.return_value = resp
            cliente.cancel_envelope("env-123")
            args, kwargs = mock_req.call_args
            assert args[0] == "PATCH"
            assert "/envelopes/env-123" in args[1]
            payload = kwargs.get("json") or {}
            assert payload["data"]["attributes"]["status"] == "canceled"
