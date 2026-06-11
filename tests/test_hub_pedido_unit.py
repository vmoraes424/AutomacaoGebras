"""Testes unitários — hub_pedido (sem MySQL real)."""

from decimal import Decimal
from unittest.mock import MagicMock, patch

import pytest

from core.automacao_config import AutomacaoConfig
from core.hub_pedido import (
    HubPedidoError,
    _id_plune_recorrente_para_hub,
    _parse_codigos_notas,
    _parse_observacoes_uc_hub,
    _perc_economia_do_deal,
    _resolver_token_servico_hub,
    criar_pedido_hub,
    erros_validacao_observacoes_hub,
    sincronizar_pedido_hub_deal,
    validar_observacoes_hub_obrigatorias,
    remover_pedido_hub_por_deal,
)

def _mock_catalogo():
    from core.hub_pedido import _ServicoCatalogoHub

    return (
        _ServicoCatalogoHub(1, "SOLE Consultoria", "sole consultoria", "sole consultoria", "sc"),
        _ServicoCatalogoHub(
            2, "SOLE Web (com telemetria)", "sole web (com telemetria)",
            "sole web (com telemetria)", "sw",
        ),
        _ServicoCatalogoHub(
            3, "Gestão de Usina Fotovoltaica", "gestao de usina fotovoltaica",
            "gestao de usina fotovoltaica", "guf",
        ),
        _ServicoCatalogoHub(
            4, "Gestão Mercado Livre", "gestao mercado livre",
            "gestao mercado livre", "gml",
        ),
        _ServicoCatalogoHub(5, "DECS", "decs", "decs", "decs"),
        _ServicoCatalogoHub(
            6, "Gestão de Qualidade de Energia", "gestao de qualidade de energia",
            "gestao de qualidade de energia", "gqe",
        ),
    )


@pytest.fixture(autouse=True)
def _catalogo_hub():
    with patch("core.hub_pedido._catalogo_servicos_hub", return_value=_mock_catalogo()):
        yield


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
def test_parse_codigos_notas(p1, esperado):
    assert _parse_codigos_notas(p1) == esperado


def test_p1_p2_campo_combinado_cliente_barra_instalacao():
    from core.hub_pedido import _p1_p2_do_deal

    deal = {
        "custom_fields": {
            "41a3157128d51e2fc803eeec4b242efafcb55b4e": "352/665,1942",
        }
    }
    assert _p1_p2_do_deal(deal) == ([665, 1942], 352)


def test_erros_validacao_aceita_formato_cliente_barra_instalacao():
    deal = {
        "id": 746,
        "custom_fields": {
            "41a3157128d51e2fc803eeec4b242efafcb55b4e": "352/1234",
            "4fba2f9323c64acdcac770e38f2c0cdb840796bc": "",
        },
    }
    erros = erros_validacao_observacoes_hub(deal)
    assert not any("deve ser numérico" in e for e in erros)


def test_observacoes_vazio_opcional_no_ganho_obrigatorio_no_hub():
    deal = {
        "id": 1,
        "custom_fields": {
            "41a3157128d51e2fc803eeec4b242efafcb55b4e": "100/665",
            "4fba2f9323c64acdcac770e38f2c0cdb840796bc": "",
        },
    }
    assert erros_validacao_observacoes_hub(deal) == []
    with pytest.raises(HubPedidoError, match="obrigatório"):
        validar_observacoes_hub_obrigatorias("1", "", [665], 100)


def test_observacoes_independente_de_notas_usa_instalacoes_do_campo():
    texto = (
        "UC = 00665 - SOLE WEB + Gestão ACL - Mercado Livre de Energia = 1.500,92; "
        "UC = 01942 - ACL + Sole Consultoria = 454.564,00"
    )
    linhas = validar_observacoes_hub_obrigatorias("746", texto, [1234, 3456], 352)
    assert [linha.codigo_instalacao for linha in linhas] == [1234, 3456]


def test_observacoes_sem_formato_uc():
    with pytest.raises(HubPedidoError, match="UC ="):
        validar_observacoes_hub_obrigatorias(
            "1", "texto livre sem estrutura", [665], 100
        )


def test_parse_observacoes_uc_exemplo_pipe():
    texto = (
        "UC = 00665 - SOLE WEB + Gestão ACL - Mercado Livre de Energia = 1.500,92; "
        "UC = 01942 - ACL + Sole Consultoria = 454.564,00"
    )
    linhas = _parse_observacoes_uc_hub(texto)
    assert len(linhas) == 2
    assert linhas[0].identificacao == "00665"
    assert linhas[0].servicos == (2, 4)
    assert linhas[0].valor == Decimal("1500.92")
    assert linhas[1].identificacao == "01942"
    assert linhas[1].servicos == (4, 1)
    assert linhas[1].valor == Decimal("454564.00")


def test_resolver_codigo_instalacao_por_identificacao():
    from core.hub_pedido import _resolver_codigo_instalacao_hub

    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = (665,)
    mock_conn = MagicMock()
    mock_conn.cursor.return_value.__enter__ = lambda s: mock_cursor
    mock_conn.cursor.return_value.__exit__ = MagicMock(return_value=False)

    with patch("core.hub_pedido.hub_conn") as mock_hub:
        mock_hub.return_value.__enter__.return_value = mock_conn
        mock_hub.return_value.__exit__ = MagicMock(return_value=False)
        assert _resolver_codigo_instalacao_hub("00665", 123) == 665
    mock_cursor.execute.assert_called_once()
    sql, params = mock_cursor.execute.call_args[0]
    assert "IDENTIFICACAO" in sql
    assert params == ("00665", 123)


def test_observacoes_rejeita_valor_sem_formato_br():
    texto = "UC = 00665 - SOLE WEB = 7897979"
    with pytest.raises(HubPedidoError, match="1.500,92"):
        _parse_observacoes_uc_hub(texto)


def test_observacoes_rejeita_uc_separadas_por_virgula():
    texto = (
        "UC = 00665 - SOLE WEB = 1.500,92, UC = 01942 - ACL = 500,00"
    )
    with pytest.raises(HubPedidoError, match=";"):
        validar_observacoes_hub_obrigatorias("1", texto, [665, 1942], 100)


def test_resolver_rejeita_sole_ambiguo():
    with pytest.raises(HubPedidoError, match="ambíguo"):
        _resolver_token_servico_hub("SOLE")


def test_resolver_aceita_sole_web():
    assert _resolver_token_servico_hub("SOLE WEB") == 2


def test_id_plune_recorrente_apenas_recorrente():
    with patch("core.hub_pedido.obter_numeros_pedidos_plune_deal") as mock_nums:
        mock_nums.return_value = {"implantacao": "111", "recorrente": "222"}
        assert _id_plune_recorrente_para_hub("1") == 222
    with patch("core.hub_pedido.obter_numeros_pedidos_plune_deal") as mock_nums:
        mock_nums.return_value = {"implantacao": "111"}
        assert _id_plune_recorrente_para_hub("1") is None


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


def test_criar_pedido_hub_skip_ja_criado():
    with patch("core.hub_pedido.buscar_por_deal_id") as mock_buscar:
        mock_buscar.return_value = {
            "parceiro_plune_criado": False,
            "hub_pedido_criado": True,
            "pedido_hub_id": 42,
        }
        out = criar_pedido_hub("99")
    assert out["status"] == "skipped"
    assert out["reason"] == "hub_pedido_ja_criado"
    assert out["pedido_hub_id"] == 42


def test_sincronizar_atualiza_quando_pedido_ja_existe():
    with patch("core.hub_pedido.buscar_por_deal_id") as mock_buscar:
        mock_buscar.return_value = {
            "parceiro_plune_criado": False,
            "hub_pedido_criado": True,
            "pedido_hub_id": 42,
        }
        with patch("core.hub_pedido._pedido_hub_existe", return_value=True):
            with patch(
                "core.hub_pedido.atualizar_pedido_hub",
                return_value={"status": "updated", "pedido_hub_id": 42},
            ) as mock_atualizar:
                out = sincronizar_pedido_hub_deal("99")
    assert out["status"] == "updated"
    mock_atualizar.assert_called_once_with("99", parceiro_plune_criado=None)


def test_sincronizar_recria_quando_flag_sem_linha_no_hub():
    with patch("core.hub_pedido.buscar_por_deal_id") as mock_buscar:
        mock_buscar.return_value = {
            "parceiro_plune_criado": False,
            "hub_pedido_criado": True,
            "pedido_hub_id": 42,
        }
        with patch("core.hub_pedido._pedido_hub_existe", return_value=False):
            with patch(
                "core.hub_pedido.criar_pedido_hub",
                return_value={"status": "created", "pedido_hub_id": 99},
            ) as mock_criar:
                out = sincronizar_pedido_hub_deal("99")
    assert out["status"] == "created"
    mock_criar.assert_called_once_with(
        "99", parceiro_plune_criado=None, ignorar_ja_criado=True
    )


def test_sincronizar_prod_nao_cria_antes_aprovacao():
    with patch("core.hub_pedido.buscar_por_deal_id", return_value=None):
        out = sincronizar_pedido_hub_deal("99", permitir_criacao=False)
    assert out["status"] == "skipped"
    assert out["reason"] == "hub_aguardando_aprovacao_plune"


def test_sincronizar_prod_atualiza_se_pedido_ja_existe():
    with patch("core.hub_pedido.buscar_por_deal_id") as mock_buscar:
        mock_buscar.return_value = {
            "parceiro_plune_criado": False,
            "hub_pedido_criado": True,
            "pedido_hub_id": 42,
        }
        with patch("core.hub_pedido._pedido_hub_existe", return_value=True):
            with patch(
                "core.hub_pedido.atualizar_pedido_hub",
                return_value={"status": "updated", "pedido_hub_id": 42},
            ) as mock_atualizar:
                out = sincronizar_pedido_hub_deal("99", permitir_criacao=False)
    assert out["status"] == "updated"
    mock_atualizar.assert_called_once_with("99", parceiro_plune_criado=None)


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


def test_criar_pedido_hub_pula_quando_pular_hub():
    cfg = AutomacaoConfig(pular_hub=True)
    with patch("core.hub_pedido.get_automacao_config", return_value=cfg):
        out = criar_pedido_hub("99")
    assert out == {
        "status": "skipped",
        "deal_id": "99",
        "reason": "hub_criacao_desabilitada",
    }
