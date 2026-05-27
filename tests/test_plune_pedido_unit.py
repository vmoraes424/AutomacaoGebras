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
    _descricao_pedido_plune,
    _criar_pedido_plune_tipo,
    _montar_observacoes_pedido,
    _montar_query_insert_pedido,
    _ordenar_resultados_por_tipo,
    _pedido_integracao_tipo,
    _pedidos_plune_deal_resolvidos,
    _valor_implantacao_valido_para_pedido,
    criar_pedido_plune,
)
from core.pedido_anexos import CacheAnexosDeal
from core.pipedrive_fields import (
    FIELD_GESTAO_USINA_FOTOVOLTAICA,
    FIELD_NUMERO_CONTRATO_P1,
    FIELD_NUMERO_CONTRATO_P2,
    FIELD_OBSERVACOES_DETALHES,
    FIELD_PERCENTUAL_EXITO,
    FIELD_VALOR_IMPLANTACAO,
    FIELD_VALOR_MENSAL,
)


def _parametros_query(query: list[tuple[str, str]]) -> dict[str, str]:
    return dict(query)


def _deal_comissao():
    return {
        "id": 746,
        "title": "Teste",
        "custom_fields": {
            FIELD_NUMERO_CONTRATO_P1: "123",
            FIELD_NUMERO_CONTRATO_P2: "456",
            FIELD_VALOR_IMPLANTACAO: "7000",
            FIELD_VALOR_MENSAL: "789",
            FIELD_GESTAO_USINA_FOTOVOLTAICA: 7,
        },
    }


def _parceiro_minimo():
    return {
        "id": "999",
        "razao_social": "Cliente Teste",
        "documento": "12345678000190",
        "documento_formatado": "12.345.678/0001-90",
    }


class TestDescricaoPedido:
    def test_implantacao_apenas_codigo_contrato(self):
        deal = {
            "id": 746,
            "custom_fields": {
                FIELD_NUMERO_CONTRATO_P1: "123",
                FIELD_NUMERO_CONTRATO_P2: "456",
            },
        }
        assert (
            _descricao_pedido_plune(deal, TIPO_PEDIDO_IMPLANTACAO)
            == "CGRc123i456n1r0a26"
        )

    def test_recorrente_apenas_codigo_contrato(self):
        deal = {
            "id": 746,
            "custom_fields": {
                FIELD_NUMERO_CONTRATO_P1: "123",
                FIELD_NUMERO_CONTRATO_P2: "456",
            },
        }
        assert (
            _descricao_pedido_plune(deal, TIPO_PEDIDO_RECORRENTE)
            == "CGRc123i456n1r0a26"
        )


class TestMontarQueryInsertPedido:
    @patch("core.plune_catalog.resolver_subcentro", return_value=None)
    @patch("core.plune_pedido.settings_por_branch")
    @patch("core.plune_pedido._montar_observacoes_pedido", return_value={})
    @patch("core.plune_pedido._aplicar_dados_cliente_pedido")
    @patch("core.plune_pedido._resolver_tipo_contrato_id", return_value="49")
    @patch("core.plune_pedido._parametro_contabil_id", return_value="1077")
    @patch("core.plune_pedido._resolver_branch_id", return_value="751")
    def test_comissao_na_url_insert(
        self,
        _branch,
        _param,
        _tipo_contrato,
        _cliente,
        _obs,
        mock_settings,
        _sub,
    ):
        mock_settings.return_value = {
            "subcentro_custo_id": "",
            "pedido_serie": "1",
            "pedido_modelo_id": "01",
            "regional_map": {},
            "subcentro3_map": {},
        }
        deal = _deal_comissao()
        parceiro = _parceiro_minimo()

        q_impl = _parametros_query(
            _montar_query_insert_pedido(deal, parceiro, TIPO_PEDIDO_IMPLANTACAO)
        )
        assert q_impl["Venda.Pedido.BaseComissao"] == "7.000,00"
        assert q_impl["Venda.Pedido.ValorComissao"] == "7.000,00"
        assert q_impl["Venda.Pedido.PercentualComissao"] == "0,001"
        assert q_impl["Venda.Pedido.Serie"] == "1"
        assert q_impl["Venda.Pedido.ModeloId"] == "01"
        assert q_impl["Venda.Pedido.TipoContratoId"] == "49"
        assert q_impl["Venda.Pedido.Aprovado"] == "0"

        q_rec = _parametros_query(
            _montar_query_insert_pedido(deal, parceiro, TIPO_PEDIDO_RECORRENTE)
        )
        assert q_rec["Venda.Pedido.BaseComissao"] == "789,00"
        assert q_rec["Venda.Pedido.ValorComissao"] == "9.468,00"
        assert q_rec["Venda.Pedido.PercentualComissao"] == "7"
        assert q_rec["Venda.Pedido.Serie"] == "1"
        assert q_rec["Venda.Pedido.Aprovado"] == "0"

class TestObservacoesPedido:
    def test_observacoes_detalhes_pipe_vai_para_observacao(self):
        deal = {
            "id": 746,
            "title": "Biview",
            "custom_fields": {
                FIELD_VALOR_MENSAL: "789",
                FIELD_VALOR_IMPLANTACAO: "7000",
                FIELD_NUMERO_CONTRATO_P1: "123",
                FIELD_NUMERO_CONTRATO_P2: "456",
                FIELD_GESTAO_USINA_FOTOVOLTAICA: 7,
                FIELD_OBSERVACOES_DETALHES: "Texto livre do Pipedrive",
            },
        }
        out = _montar_observacoes_pedido(deal, TIPO_PEDIDO_RECORRENTE)
        assert out["Observacao"].startswith("Texto livre do Pipedrive")

    @patch("core.plune_pedido.get_enum_label")
    def test_exito_gebras_vem_do_pipedrive(self, mock_enum):
        mock_enum.side_effect = lambda deal, field: (
            "15%" if field == FIELD_PERCENTUAL_EXITO else ""
        )
        deal = {
            "id": 746,
            "title": "Biview",
            "custom_fields": {FIELD_VALOR_MENSAL: "789"},
        }
        out = _montar_observacoes_pedido(deal, TIPO_PEDIDO_RECORRENTE)
        assert "ÊXITO GEBRAS: 15%" in out["Observacao"]
        assert "ÊXITO GEBRAS: 20%" not in out["Observacao"]

    def test_sem_observacoes_detalhes_sem_fallback_servico(self):
        deal = {
            "id": 746,
            "title": "Biview",
            "custom_fields": {
                FIELD_VALOR_MENSAL: "789",
                FIELD_GESTAO_USINA_FOTOVOLTAICA: 7,
            },
        }
        out = _montar_observacoes_pedido(deal, TIPO_PEDIDO_RECORRENTE)
        assert "SERVIÇO" not in out["Observacao"]
        assert "Biview: SOLE" not in out["Observacao"]
        assert out["Observacao"].startswith("MENSALIDADE:")

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
    @patch("core.plune_pedido.vincular_pedidos_plune_implantacao_recorrente")
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
        _vincular,
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
