"""Testes unitários — hub_pedido (sem MySQL real)."""

from decimal import Decimal
from unittest.mock import MagicMock, patch

import pytest

from core.hub_pedido import (
    _id_plune_recorrente_para_hub,
    _parse_codigos_instalacao_p1,
    _perc_economia_do_deal,
    _servicos_do_deal,
    _valor_por_instalacao,
    criar_pedido_hub,
    remover_pedido_hub_por_deal,
    tentar_criar_pedido_hub_deal,
)
from core.pipedrive_fields import FIELD_GESTAO_ACL, FIELD_QTD_SOLE


@pytest.mark.parametrize(
    "label, tem, perc",
    [
        ("15%", True, "15.00"),
        ("20 %", True, "20.00"),
        ("A definir", False, "0"),
        ("", False, "0"),
    ],
)
def test_perc_economia_do_deal(label, tem, perc):
    deal = {"custom_fields": {}}
    with patch("core.hub_pedido.get_enum_label", return_value=label):
        tem_flag, valor = _perc_economia_do_deal(deal)
    assert tem_flag is tem
    assert valor == Decimal(perc)


@pytest.mark.parametrize(
    "p1, esperado",
    [
        ("665", [665]),
        ("00665,01942", [665, 1942]),
        ("665; 1942", [665, 1942]),
        ("665,665", [665]),
    ],
)
def test_parse_codigos_instalacao_p1(p1, esperado):
    assert _parse_codigos_instalacao_p1(p1) == esperado


def test_valor_por_instalacao_reparte_centavos():
    total = Decimal("100.00")
    assert _valor_por_instalacao(total, 0, 3) == Decimal("33.33")
    assert _valor_por_instalacao(total, 1, 3) == Decimal("33.33")
    assert _valor_por_instalacao(total, 2, 3) == Decimal("33.34")


def test_id_plune_recorrente_apenas_recorrente():
    with patch("core.hub_pedido.obter_numeros_pedidos_plune_deal") as mock_nums:
        mock_nums.return_value = {"implantacao": "111", "recorrente": "222"}
        assert _id_plune_recorrente_para_hub("1") == 222
    with patch("core.hub_pedido.obter_numeros_pedidos_plune_deal") as mock_nums:
        mock_nums.return_value = {"implantacao": "111"}
        assert _id_plune_recorrente_para_hub("1") is None


def test_servicos_do_deal_mapeia_ucs():
    deal = {"id": 1}

    def _gv(_deal, field):
        if field == FIELD_QTD_SOLE:
            return "2"
        if field == FIELD_GESTAO_ACL:
            return "0"
        return ""

    with patch("core.hub_pedido.get_val", side_effect=_gv):
        servicos = _servicos_do_deal(deal)
    assert 2 in servicos
    assert 4 not in servicos


def test_criar_pedido_hub_skip_parceiro_novo_kwarg():
    out = criar_pedido_hub("99", parceiro_plune_criado=True)
    assert out["status"] == "skipped"
    assert out["reason"] == "parceiro_novo_plune"


def test_criar_pedido_hub_skip_parceiro_novo():
    with patch("core.hub_pedido.buscar_por_deal_id") as mock_buscar:
        mock_buscar.return_value = {"parceiro_plune_criado": True}
        out = criar_pedido_hub("99")
    assert out["status"] == "skipped"
    assert out["reason"] == "parceiro_novo_plune"


def test_remover_pedido_hub_por_deal_sem_estado():
    with patch("core.hub_pedido.obter_estado_hub_deal", return_value=None):
        stats = remover_pedido_hub_por_deal("1")
    assert stats["hub_pedido"] == 0


def test_remover_pedido_hub_por_deal_remove():
    with patch("core.hub_pedido.obter_estado_hub_deal") as mock_estado:
        mock_estado.return_value = {"hub_pedido_criado": True, "pedido_hub_id": 100}
        with patch("core.hub_pedido.remover_pedido_hub", return_value=True) as mock_rm:
            stats = remover_pedido_hub_por_deal("1")
    assert stats["hub_pedido"] == 1
    mock_rm.assert_called_once_with(100)
