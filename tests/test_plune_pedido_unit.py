"""Testes unitários: plune_pedido (helpers, paralelo, criar com mocks)."""

from __future__ import annotations

import time
from unittest.mock import MagicMock, patch

import pytest

from core.plune_pedido import (
    TIPO_PEDIDO_IMPLANTACAO,
    TIPO_PEDIDO_RECORRENTE,
    PluneError,
    _anexar_documentos_pedido_criado,
    _criar_pedido_plune_tipo,
    _ordenar_resultados_por_tipo,
    _pedido_integracao_tipo,
    _pedidos_plune_deal_resolvidos,
    _valor_implantacao_valido_para_pedido,
    criar_pedido_plune,
)
from core.pedido_anexos import CacheAnexosDeal


class TestHelpers:
    def test_pedido_integracao(self):
        assert _pedido_integracao_tipo("746", "implantacao") == "746-implantacao"

    def test_valor_implantacao_valido(self):
        assert _valor_implantacao_valido_para_pedido("2") is True
        assert _valor_implantacao_valido_para_pedido("1") is False
        assert _valor_implantacao_valido_para_pedido("") is False

    def test_ordenar_resultados(self):
        desordenado = [
            {"tipo": TIPO_PEDIDO_RECORRENTE, "status": "created"},
            {"tipo": TIPO_PEDIDO_IMPLANTACAO, "status": "created"},
        ]
        ordenado = _ordenar_resultados_por_tipo(desordenado)
        assert ordenado[0]["tipo"] == TIPO_PEDIDO_IMPLANTACAO
        assert ordenado[1]["tipo"] == TIPO_PEDIDO_RECORRENTE

    def test_pedidos_resolvidos(self):
        assert _pedidos_plune_deal_resolvidos(
            [{"status": "created"}, {"status": "skipped"}]
        )
        assert not _pedidos_plune_deal_resolvidos(
            [{"status": "created"}, {"status": "partial"}]
        )


class TestAnexarDocumentosParalelo:
    @patch("core.plune_pedido.anexar_contrato_pedido")
    @patch("core.plune_pedido.anexar_proposta_pedido")
    def test_chama_proposta_e_contrato(self, mock_prop, mock_contr):
        mock_prop.return_value = {"anexo_id": "1"}
        mock_contr.return_value = {"anexo_id": "2"}
        cache = CacheAnexosDeal("746")
        anexos = _anexar_documentos_pedido_criado(
            "746", "6742", "751", cache=cache, anexar_contrato_dev=True
        )
        assert anexos["proposta"]["anexo_id"] == "1"
        assert anexos["contrato"]["anexo_id"] == "2"
        mock_prop.assert_called_once()
        mock_contr.assert_called_once()


class TestCriarPedidoPluneTipo:
    @patch("core.plune_pedido.carregar_pedidos_plune_criados")
    def test_skip_implantacao_valor_invalido(self, mock_criados, deal_minimo, parceiro_minimo):
        mock_criados.return_value = set()
        deal = {**deal_minimo, "custom_fields": {}}
        with patch("core.plune_pedido.get_val", return_value="1"):
            out = _criar_pedido_plune_tipo(
                deal, parceiro_minimo, False, TIPO_PEDIDO_IMPLANTACAO
            )
        assert out["status"] == "skipped"
        assert out["reason"] == "valor_implantacao_invalido_ou_menor_igual_1"

    @patch("core.plune_pedido._anexar_documentos_pedido_criado")
    @patch("core.plune_pedido.salvar_pedido_plune_criado")
    @patch("core.plune_pedido._plune_get")
    @patch("core.plune_pedido._montar_query_insert_pedido")
    @patch("core.plune_pedido._parametro_contabil_id")
    @patch("core.plune_pedido._resolver_branch_id")
    @patch("core.plune_pedido._buscar_pedido_id_por_pedido_integracao")
    @patch("core.plune_pedido.carregar_pedidos_plune_criados")
    def test_created_com_anexos(
        self,
        mock_criados,
        mock_busca,
        mock_branch,
        mock_param,
        mock_query,
        mock_plune,
        mock_salvar,
        mock_anexos,
        deal_minimo,
        parceiro_minimo,
    ):
        mock_criados.return_value = set()
        mock_busca.return_value = None
        mock_branch.return_value = "751"
        mock_param.return_value = "1"
        mock_query.return_value = []
        mock_plune.return_value = {
            "Field": {"Id": {"value": "9001"}, "Aprovado": {"value": "1"}},
        }
        mock_anexos.return_value = {"proposta": {"anexo_id": "10"}}

        out = _criar_pedido_plune_tipo(
            deal_minimo,
            parceiro_minimo,
            True,
            TIPO_PEDIDO_RECORRENTE,
            anexar_contrato_dev=False,
        )
        assert out["status"] == "created"
        assert out["pedido_id"] == "9001"
        assert "proposta" in out["anexos"]
        mock_anexos.assert_called_once()


class TestCriarPedidoPluneParalelo:
    @patch("core.plune_pedido.marcar_pedido_criado")
    @patch("core.plune_pedido.CacheAnexosDeal")
    @patch("core.plune_pedido._criar_pedido_plune_tipo")
    @patch("core.plune_pedido._resolver_ou_criar_parceiro")
    @patch("core.plune_pedido.get_documento")
    @patch("core.plune_pedido.buscar_deal_por_id")
    def test_dois_tipos_em_paralelo(
        self,
        mock_deal,
        mock_doc,
        mock_parceiro,
        mock_criar_tipo,
        mock_cache_cls,
        mock_marcar,
        deal_minimo,
        parceiro_minimo,
    ):
        mock_deal.return_value = deal_minimo
        mock_doc.return_value = "52398605000186"
        mock_parceiro.return_value = (parceiro_minimo, False)

        inicios = []

        def _criar_lento(deal, parceiro, criado, tipo, **kwargs):
            inicios.append((tipo, time.perf_counter()))
            time.sleep(0.05)
            return {
                "status": "created",
                "tipo": tipo,
                "pedido_id": "1" if tipo == TIPO_PEDIDO_IMPLANTACAO else "2",
            }

        mock_criar_tipo.side_effect = _criar_lento
        cache = MagicMock()
        mock_cache_cls.return_value = cache

        result = criar_pedido_plune("746")
        assert result["status"] == "created"
        assert len(result["pedidos"]) == 2
        # Se sequencial, delta entre inícios seria ~0.05s; em paralelo, quase 0
        if len(inicios) == 2:
            delta = abs(inicios[0][1] - inicios[1][1])
            assert delta < 0.04, f"tipos não rodaram em paralelo (delta={delta:.3f}s)"
        mock_cache_cls.assert_called_once()
        cache.iniciar_prefetch_assincrono.assert_called_once()

    @patch("core.plune_pedido.buscar_deal_por_id")
    def test_deal_nao_encontrado(self, mock_deal):
        mock_deal.return_value = None
        with pytest.raises(PluneError, match="não encontrado"):
            criar_pedido_plune("999")
