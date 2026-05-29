"""Testes unitários: arquivos Pipedrive (sem API real)."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from core.pipedrive_files import (
    _eh_pdf,
    baixar_arquivo_pipedrive,
    baixar_pdf_proposta_deal,
    escolher_pdf_proposta,
    listar_arquivos_deal,
)


class TestEhPdf:
    def test_por_tipo(self):
        assert _eh_pdf({"file_type": "pdf", "name": "x.txt"}) is True

    def test_por_extensao(self):
        assert _eh_pdf({"file_type": "doc", "name": "proposta.pdf"}) is True

    def test_negativo(self):
        assert _eh_pdf({"file_type": "doc", "name": "nota.docx"}) is False


class TestEscolherPdfProposta:
    def test_prioriza_nome_proposta(self):
        arquivos = [
            {"id": 1, "name": "outro.pdf", "file_type": "pdf"},
            {"id": 2, "name": "Apresentacao Proposta Comercial.pdf", "file_type": "pdf"},
        ]
        assert escolher_pdf_proposta(arquivos)["id"] == 2

    def test_primeiro_pdf_se_sem_proposta_no_nome(self):
        arquivos = [
            {"id": 10, "name": "anexo.pdf", "file_type": "pdf"},
            {"id": 11, "name": "segundo.pdf", "file_type": "pdf"},
        ]
        assert escolher_pdf_proposta(arquivos)["id"] == 10

    def test_vazio(self):
        assert escolher_pdf_proposta([]) is None
        assert escolher_pdf_proposta([{"name": "x.docx"}]) is None


class TestListarArquivosDeal:
    def test_deal_id_vazio(self):
        assert listar_arquivos_deal("") == []

    @patch("core.pipedrive_files.requests.get")
    def test_lista_ok(self, mock_get):
        resp = MagicMock(ok=True, status_code=200)
        resp.json.return_value = {
            "data": [{"id": 1}, {"id": 2}],
            "additional_data": {"pagination": {"more_items_in_collection": False}},
        }
        mock_get.return_value = resp
        assert len(listar_arquivos_deal("565")) == 2

    @patch("core.pipedrive_files.requests.get")
    def test_lista_paginada(self, mock_get):
        page1 = MagicMock(ok=True, status_code=200)
        page1.json.return_value = {
            "data": [{"id": 1}],
            "additional_data": {
                "pagination": {"more_items_in_collection": True, "next_start": 1},
            },
        }
        page2 = MagicMock(ok=True, status_code=200)
        page2.json.return_value = {
            "data": [{"id": 2}],
            "additional_data": {"pagination": {"more_items_in_collection": False}},
        }
        mock_get.side_effect = [page1, page2]
        assert len(listar_arquivos_deal("565")) == 2

    @patch("core.pipedrive_files.requests.get")
    def test_erro_http(self, mock_get):
        resp = MagicMock(ok=False, status_code=401, text="unauthorized")
        mock_get.return_value = resp
        with pytest.raises(RuntimeError, match="401"):
            listar_arquivos_deal("565")


class TestBaixarArquivo:
    @patch("core.pipedrive_files.requests.get")
    def test_baixa_com_token_na_url(self, mock_get, pdf_bytes):
        meta = MagicMock(ok=True, status_code=200)
        meta.json.return_value = {
            "data": {
                "name": "proposta.pdf",
                "url": "https://api.pipedrive.com/files/download/1",
            }
        }
        binario = MagicMock(ok=True, status_code=200)
        binario.content = pdf_bytes
        binario.headers = {"Content-Type": "application/pdf"}
        mock_get.side_effect = [meta, binario]

        conteudo, nome, ctype = baixar_arquivo_pipedrive(2645)
        assert conteudo == pdf_bytes
        assert nome == "proposta.pdf"
        assert ctype == "application/pdf"
        assert mock_get.call_count == 2
        _, kwargs = mock_get.call_args_list[1]
        assert kwargs.get("params", {}).get("api_token")


class TestBaixarPdfPropostaDeal:
    @patch("core.pipedrive_files.baixar_arquivo_pipedrive")
    @patch("core.pipedrive_files.listar_arquivos_deal")
    def test_fluxo_completo(self, mock_listar, mock_baixar, pdf_bytes):
        mock_listar.return_value = [
            {"id": 99, "name": "Proposta Comercial.pdf", "file_type": "pdf"},
        ]
        mock_baixar.return_value = (pdf_bytes, "Proposta Comercial.pdf", "application/pdf")
        out = baixar_pdf_proposta_deal("746")
        assert out == (pdf_bytes, "Proposta Comercial.pdf")

    @patch("core.pipedrive_files.listar_arquivos_deal")
    def test_sem_pdf(self, mock_listar):
        mock_listar.return_value = [{"id": 1, "name": "foto.png", "file_type": "png"}]
        assert baixar_pdf_proposta_deal("746") is None
