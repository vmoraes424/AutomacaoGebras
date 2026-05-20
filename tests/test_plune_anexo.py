"""Testes unitários: upload Venda.AnexoPedido (mock HTTP)."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from core.plune_anexo import _parse_plune_json, inserir_anexo_pedido
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
