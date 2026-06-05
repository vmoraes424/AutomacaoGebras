"""Testes: comissão BaseComissao / ValorComissao / PercentualComissao."""

from __future__ import annotations

import pytest

from core.plune_errors import PluneError
from core.plune_pedido import (
    TIPO_PEDIDO_IMPLANTACAO,
    TIPO_PEDIDO_RECORRENTE,
    _montar_campos_comissao,
)
from core.pipedrive_fields import (
    FIELD_GESTAO_USINA_FOTOVOLTAICA,
    FIELD_QUANTIDADE_UCS,
    FIELD_QTD_SOLE,
    FIELD_VALOR_IMPLANTACAO,
    FIELD_VALOR_MENSAL,
)


def _deal(**campos):
    return {"id": 100, "custom_fields": campos}


def test_implantacao_base_valor_pedido_percentual_fixo():
    out = _montar_campos_comissao(
        _deal(**{FIELD_VALOR_IMPLANTACAO: "7000"}),
        TIPO_PEDIDO_IMPLANTACAO,
        "7000",
    )
    assert out["BaseComissao"] == "7.000,00"
    assert out["ValorComissao"] == "7.000,00"
    assert out["PercentualComissao"] == "0,001"


def test_recorrente_base_valor_12x_percentual_quantidade_ucs():
    out = _montar_campos_comissao(
        _deal(
            **{
                FIELD_VALOR_MENSAL: "789",
                FIELD_QUANTIDADE_UCS: 28,
                FIELD_GESTAO_USINA_FOTOVOLTAICA: 7,
            }
        ),
        TIPO_PEDIDO_RECORRENTE,
        "789",
    )
    assert out["BaseComissao"] == "789,00"
    assert out["ValorComissao"] == "9.468,00"
    assert out["PercentualComissao"] == "28"


def test_recorrente_percentual_usa_quantidade_ucs_nao_soma_servicos():
    """PercentualComissao vem de «Quantidade de UC's», não da soma dos serviços."""
    out = _montar_campos_comissao(
        _deal(
            **{
                FIELD_VALOR_MENSAL: "100",
                FIELD_QUANTIDADE_UCS: 15,
                FIELD_QTD_SOLE: 4,
                FIELD_GESTAO_USINA_FOTOVOLTAICA: 7,
            }
        ),
        TIPO_PEDIDO_RECORRENTE,
        "100",
    )
    assert out["PercentualComissao"] == "15"


def test_implantacao_sem_valor_levanta():
    with pytest.raises(PluneError, match="Implantação"):
        _montar_campos_comissao(_deal(), TIPO_PEDIDO_IMPLANTACAO, "")


def test_recorrente_sem_quantidade_ucs_levanta():
    with pytest.raises(PluneError, match="Quantidade de UC's"):
        _montar_campos_comissao(
            _deal(**{FIELD_VALOR_MENSAL: "100", FIELD_QTD_SOLE: 5}),
            TIPO_PEDIDO_RECORRENTE,
            "100",
        )
