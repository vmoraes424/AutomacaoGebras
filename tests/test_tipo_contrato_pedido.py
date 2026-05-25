"""Testes: TipoContratoId por tipo de pedido e maior UC (sem fallback)."""

from __future__ import annotations

import pytest

from core.plune_errors import PluneError
from core.plune_pedido import (
    TIPO_PEDIDO_IMPLANTACAO,
    TIPO_PEDIDO_RECORRENTE,
    _resolver_tipo_contrato_id,
)
from core.pipedrive_fields import (
    FIELD_GESTAO_ACL,
    FIELD_GESTAO_USINA_FOTOVOLTAICA,
    FIELD_INDICADORES_QUALIDADE,
    FIELD_QTD_SOLE,
    FIELD_QUALIDADE_ENERGIA,
)


def _deal(**campos):
    return {"id": 746, "custom_fields": campos}


def test_implantacao_sempre_id_1():
    assert (
        _resolver_tipo_contrato_id(_deal(), TIPO_PEDIDO_IMPLANTACAO) == "1"
    )


def test_recorrente_usina_maior_uc():
    deal = _deal(
        **{
            FIELD_GESTAO_USINA_FOTOVOLTAICA: 7,
            FIELD_GESTAO_ACL: 6,
            FIELD_QTD_SOLE: 4,
            FIELD_INDICADORES_QUALIDADE: 5,
            FIELD_QUALIDADE_ENERGIA: 6,
        }
    )
    assert _resolver_tipo_contrato_id(deal, TIPO_PEDIDO_RECORRENTE) == "49"


def test_recorrente_acl_vence_se_maior():
    deal = _deal(
        **{
            FIELD_GESTAO_ACL: 10,
            FIELD_GESTAO_USINA_FOTOVOLTAICA: 2,
        }
    )
    assert _resolver_tipo_contrato_id(deal, TIPO_PEDIDO_RECORRENTE) == "41"


def test_recorrente_sem_uc_levanta_erro():
    with pytest.raises(PluneError, match=r"UCs > 0"):
        _resolver_tipo_contrato_id(_deal(), TIPO_PEDIDO_RECORRENTE)
