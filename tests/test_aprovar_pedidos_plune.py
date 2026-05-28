"""Testes unitários: aprovação de pedidos em paralelo."""

from __future__ import annotations

import time
from unittest.mock import patch

from core.plune_pedido import (
    TIPO_PEDIDO_IMPLANTACAO,
    TIPO_PEDIDO_RECORRENTE,
    _aprovar_pedido_plune_tipo,
    aprovar_pedidos_plune,
)


class TestAprovarPedidosPlune:
    @patch("core.plune_pedido._aprovar_pedido_plune_tipo")
    @patch("core.plune_pedido.CacheAnexosDeal")
    def test_paralelo_e_ordenacao(self, mock_cache_cls, mock_aprovar):
        cache = mock_cache_cls.return_value
        inicios = []

        def _aprovar(deal_id, tipo, **kwargs):
            inicios.append((tipo, time.perf_counter()))
            time.sleep(0.05)
            return {
                "status": "approved",
                "tipo": tipo,
                "deal_id": deal_id,
                "pedido_id": "1",
            }

        mock_aprovar.side_effect = _aprovar
        out = aprovar_pedidos_plune("746", data_entrega="19/05/2026")
        assert out["status"] == "approved"
        assert out["pedidos"][0]["tipo"] == TIPO_PEDIDO_IMPLANTACAO
        assert out["pedidos"][1]["tipo"] == TIPO_PEDIDO_RECORRENTE
        assert out["data_entrega"] == "19/05/2026"
        cache.iniciar_prefetch_assincrono.assert_called_once_with(
            proposta=False, contrato=True
        )
        if len(inicios) == 2:
            assert abs(inicios[0][1] - inicios[1][1]) < 0.04

    @patch("core.plune_pedido._aprovar_pedido_plune_tipo")
    @patch("core.plune_pedido.CacheAnexosDeal")
    def test_status_pending_contract_quando_pdf_assinado_indisponivel(
        self, mock_cache_cls, mock_aprovar
    ):
        cache = mock_cache_cls.return_value
        mock_aprovar.side_effect = [
            {
                "status": "pending_contract",
                "tipo": TIPO_PEDIDO_IMPLANTACAO,
                "deal_id": "746",
                "pedido_id": "1",
                "reason": "signed_contract_unavailable",
            },
            {
                "status": "approved",
                "tipo": TIPO_PEDIDO_RECORRENTE,
                "deal_id": "746",
                "pedido_id": "2",
            },
        ]
        out = aprovar_pedidos_plune("746", data_entrega="19/05/2026")
        assert out["status"] == "pending_contract"
        assert out["pedidos"][0]["tipo"] == TIPO_PEDIDO_IMPLANTACAO
        assert out["pedidos"][1]["tipo"] == TIPO_PEDIDO_RECORRENTE
        cache.iniciar_prefetch_assincrono.assert_called_once_with(
            proposta=False, contrato=True
        )

    @patch("core.plune_pedido._plune_get")
    @patch("core.plune_pedido.anexar_contrato_pedido", return_value=None)
    @patch("core.plune_pedido._buscar_pedido_por_pedido_integracao")
    def test_nao_aprova_sem_contrato_assinado(
        self, mock_busca, _mock_anexar, mock_plune_get
    ):
        mock_busca.return_value = {
            "id": "6798",
            "cliente_id": "1001",
            "branch_id": "751",
            "aprovado": False,
            "pedido_integracao": "746-implantacao",
            "status_pedido": "1",
        }
        out = _aprovar_pedido_plune_tipo(
            "746", TIPO_PEDIDO_IMPLANTACAO, data_entrega="26/05/2026"
        )
        assert out["status"] == "pending_contract"
        assert out["reason"] == "signed_contract_unavailable"
        assert out["aprovado"] is False
        mock_plune_get.assert_not_called()
