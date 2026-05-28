"""Testes unitários: API Venda.AnexoPedido (mock HTTP)."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from core.plune_anexo import (
    _parse_plune_json,
    inserir_anexo_pedido,
    listar_anexos_pedido,
    remover_anexo_pedido,
    remover_todos_anexos_pedido,
    remover_anexos_automacao,
)
from core.plune_errors import PluneApiError, PluneError


class TestParsePluneJson:
    def test_ok(self):
        payload = _parse_plune_json('{"Field": {"Id": {"value": "99"}}}')
        assert payload["Field"]["Id"]["value"] == "99"

    def test_prefixo_lixo(self):
        payload = _parse_plune_json('OK\n{"Field": {}}')
        assert "Field" in payload

    def test_error_status(self):
        with pytest.raises(PluneApiError):
            _parse_plune_json('{"ErrorStatus": "ERRO_X"}')

    def test_json_invalido(self):
        with pytest.raises(PluneError):
            _parse_plune_json("nao é json")


class TestInserirAnexoPedido:
    def test_arquivo_vazio(self):
        with pytest.raises(PluneError, match="vazio"):
            inserir_anexo_pedido(
                pedido_id="1",
                branch_id="751",
                nome_arquivo="x.pdf",
                conteudo=b"",
            )

    def test_sem_pedido_id(self):
        with pytest.raises(PluneError, match="obrigatórios"):
            inserir_anexo_pedido(
                pedido_id="",
                branch_id="751",
                nome_arquivo="x.pdf",
                conteudo=b"x",
            )

    @patch("core.plune_anexo.requests.post")
    def test_insert_ok(self, mock_post, pdf_bytes):
        resp = MagicMock(ok=True, status_code=200)
        resp.text = '{"Field": {"Id": {"value": "4065"}}}'
        mock_post.return_value = resp

        out = inserir_anexo_pedido(
            pedido_id="6742",
            branch_id="751",
            nome_arquivo="../../proposta.pdf",
            conteudo=pdf_bytes,
        )
        assert out["anexo_id"] == "4065"
        assert out["nome_arquivo"] == "proposta.pdf"
        assert out["pedido_id"] == "6742"
        mock_post.assert_called_once()
        _, kwargs = mock_post.call_args
        assert "files" in kwargs

    @patch("core.plune_anexo.requests.post")
    def test_http_erro(self, mock_post, pdf_bytes):
        resp = MagicMock(ok=False, status_code=500, text="erro interno")
        mock_post.return_value = resp
        with pytest.raises(PluneError, match="HTTP 500"):
            inserir_anexo_pedido(
                pedido_id="1",
                branch_id="751",
                nome_arquivo="a.pdf",
                conteudo=pdf_bytes,
            )


class TestListarERemoverAnexos:
    @patch("core.plune_anexo.requests.get")
    def test_listar_anexos_normaliza(self, mock_get):
        resp = MagicMock(ok=True, status_code=200)
        resp.text = (
            '{"data": {"row": [{"Id": {"value": "10"}, "NomeArquivo": {"value": "Contrato_746.pdf"},'
            ' "TipoAnexo": {"value": "CONTRATO"}, "Observacao": {"value": "AUTOMACAO_GEBRAS_CONTRATO v1"}},'
            ' {"Id": {"value": "11"}, "NomeArquivo": {"value": "proposta.pdf"}, "TipoAnexo": {"value": "PROPOSTA"}}]}}'
        )
        mock_get.return_value = resp
        out = listar_anexos_pedido(pedido_id="6742", branch_id="751")
        assert out[0]["anexo_id"] == "10"
        assert out[0]["nome_arquivo"].startswith("Contrato_")
        assert out[0]["tipo_anexo"] == "CONTRATO"
        assert "AUTOMACAO_GEBRAS_CONTRATO" in out[0]["observacao"]
        mock_get.assert_called_once()

    @patch("core.plune_anexo.requests.get")
    def test_remover_anexo_chama_delete(self, mock_get):
        resp = MagicMock(ok=True, status_code=200)
        resp.text = '{"Field": {"Id": {"value": "10"}}}'
        mock_get.return_value = resp
        remover_anexo_pedido(pedido_id="6742", branch_id="751", anexo_id="10")
        mock_get.assert_called_once()

    @patch("core.plune_anexo.remover_anexo_pedido")
    @patch("core.plune_anexo.listar_anexos_pedido")
    def test_remover_contratos_filtra_por_nome(self, mock_listar, mock_rm):
        mock_listar.return_value = [
            {
                "anexo_id": "10",
                "nome_arquivo": "x.pdf",
                "tipo_anexo": "CONTRATO",
                "observacao": "",
            },
            {
                "anexo_id": "11",
                "nome_arquivo": "proposta.pdf",
                "tipo_anexo": "PROPOSTA",
                "observacao": "",
            },
            {
                "anexo_id": "12",
                "nome_arquivo": "random.docx",
                "tipo_anexo": "",
                "observacao": "AUTOMACAO_GEBRAS_CONTRATO v1",
            },
        ]
        out = remover_todos_anexos_pedido(pedido_id="6742", branch_id="751")
        assert out["total"] == 3
        assert mock_rm.call_count == 3

    @patch("core.plune_anexo.remover_anexo_pedido")
    @patch("core.plune_anexo.listar_anexos_pedido")
    def test_remover_anexos_automacao_filtra_por_tipo_ou_obs(
        self, mock_listar, mock_rm
    ):
        mock_listar.return_value = [
            {"anexo_id": "10", "nome_arquivo": "a.pdf", "tipo_anexo": "2", "observacao": ""},
            {"anexo_id": "11", "nome_arquivo": "b.pdf", "tipo_anexo": "99", "observacao": "AUTO_X v1"},
            {"anexo_id": "12", "nome_arquivo": "c.pdf", "tipo_anexo": "99", "observacao": ""},
        ]
        out = remover_anexos_automacao(
            pedido_id="6742",
            branch_id="751",
            tipo_anexo_id="2",
            observacao_prefix="AUTO_X",
        )
        assert out["total"] == 2
        assert mock_rm.call_count == 2
