"""Testes: validação da seção Contrato no Pipedrive."""

from __future__ import annotations

from unittest.mock import patch

import pytest

from core.pipedrive_fields import (
    CAMPOS_CONTRATO_OBRIGATORIOS,
    CAMPOS_CONTRATO_OPCIONAIS,
    FIELD_CEP,
    FIELD_DATA_PAGAMENTO_IMPLANTACAO,
    FIELD_INSCRICAO_MUNICIPAL,
    FIELD_CODIGO_CLIENTE_INSTALACAO,
    FIELD_NOTAS,
    FIELD_OBSERVACOES_DETALHES,
    FIELD_QUANTIDADE_UCS,
    FIELD_VALOR_IMPLANTACAO,
    get_numero_contrato,
)
from core.pipedrive_validations import (
    DealValidationError,
    _implantacao_exige_data_pagamento,
    _validar_campo_contrato,
    notificar_validacao_aprovada,
    reabrir_deal_falha_automacao,
    validar_deal_para_automacao,
)


@pytest.mark.parametrize(
    "field_code",
    [
        FIELD_INSCRICAO_MUNICIPAL,
        FIELD_DATA_PAGAMENTO_IMPLANTACAO,
        FIELD_VALOR_IMPLANTACAO,
    ],
)
def test_campos_implantacao_sao_obrigatorios(field_code: str):
    obrigatorios = {row[1] for row in CAMPOS_CONTRATO_OBRIGATORIOS}
    assert field_code in obrigatorios
    assert field_code not in CAMPOS_CONTRATO_OPCIONAIS


def test_observacoes_unico_campo_opcional():
    assert CAMPOS_CONTRATO_OPCIONAIS == frozenset({FIELD_OBSERVACOES_DETALHES})
    obrigatorios = {row[1] for row in CAMPOS_CONTRATO_OBRIGATORIOS}
    assert FIELD_OBSERVACOES_DETALHES not in obrigatorios


def test_tipos_campos_implantacao():
    tipos = {row[1]: row[2] for row in CAMPOS_CONTRATO_OBRIGATORIOS}
    assert tipos[FIELD_INSCRICAO_MUNICIPAL] == "text"
    assert tipos[FIELD_DATA_PAGAMENTO_IMPLANTACAO] == "date"
    assert tipos[FIELD_VALOR_IMPLANTACAO] == "money_implantacao"


def test_valor_implantacao_zero_ok():
    deal = {"custom_fields": {FIELD_VALOR_IMPLANTACAO: "0"}}
    assert (
        _validar_campo_contrato(
            deal, "Valor de Implantação", FIELD_VALOR_IMPLANTACAO, "money_implantacao"
        )
        is None
    )


def test_valor_implantacao_vazio_retorna_erro():
    deal = {"custom_fields": {FIELD_VALOR_IMPLANTACAO: ""}}
    msg = _validar_campo_contrato(
        deal, "Valor de Implantação", FIELD_VALOR_IMPLANTACAO, "money_implantacao"
    )
    assert msg is not None
    assert "Valor de Implantação" in msg


def test_inscricao_municipal_vazia_retorna_erro():
    deal = {"custom_fields": {FIELD_INSCRICAO_MUNICIPAL: ""}}
    msg = _validar_campo_contrato(
        deal, "Inscrição Municipal", FIELD_INSCRICAO_MUNICIPAL, "text"
    )
    assert msg is not None
    assert "Inscrição Municipal" in msg


def test_data_pagamento_implantacao_vazia_retorna_erro_quando_valor_exige():
    deal = {
        "custom_fields": {
            FIELD_VALOR_IMPLANTACAO: "5000",
            FIELD_DATA_PAGAMENTO_IMPLANTACAO: "",
        }
    }
    msg = _validar_campo_contrato(
        deal,
        "Data de Pagamento da Implantação",
        FIELD_DATA_PAGAMENTO_IMPLANTACAO,
        "date",
    )
    assert msg is not None
    assert "Data de Pagamento da Implantação" in msg


def test_data_pagamento_implantacao_ignorada_quando_valor_zero():
    deal = {
        "custom_fields": {
            FIELD_VALOR_IMPLANTACAO: "0",
            FIELD_DATA_PAGAMENTO_IMPLANTACAO: "",
        }
    }
    assert _implantacao_exige_data_pagamento(deal) is False


def test_data_pagamento_implantacao_ignorada_quando_valor_1():
    deal = {"custom_fields": {FIELD_VALOR_IMPLANTACAO: "1"}}
    assert _implantacao_exige_data_pagamento(deal) is False


def test_data_pagamento_implantacao_exigida_quando_valor_maior_que_1():
    deal = {"custom_fields": {FIELD_VALOR_IMPLANTACAO: "5000"}}
    assert _implantacao_exige_data_pagamento(deal) is True


def test_codigos_hub_sao_obrigatorios():
    obrigatorios = {row[1] for row in CAMPOS_CONTRATO_OBRIGATORIOS}
    assert FIELD_NOTAS in obrigatorios
    assert FIELD_CODIGO_CLIENTE_INSTALACAO in obrigatorios
    assert FIELD_NOTAS not in CAMPOS_CONTRATO_OPCIONAIS
    assert FIELD_CODIGO_CLIENTE_INSTALACAO not in CAMPOS_CONTRATO_OPCIONAIS


def test_quantidade_ucs_e_obrigatoria():
    obrigatorios = {row[1] for row in CAMPOS_CONTRATO_OBRIGATORIOS}
    assert FIELD_QUANTIDADE_UCS in obrigatorios
    assert FIELD_QUANTIDADE_UCS not in CAMPOS_CONTRATO_OPCIONAIS
    tipos = {row[1]: row[2] for row in CAMPOS_CONTRATO_OBRIGATORIOS}
    assert tipos[FIELD_QUANTIDADE_UCS] == "uc"


def test_quantidade_ucs_vazia_retorna_erro():
    deal = {"custom_fields": {FIELD_QUANTIDADE_UCS: ""}}
    msg = _validar_campo_contrato(
        deal, "Quantidade de UC's", FIELD_QUANTIDADE_UCS, "uc"
    )
    assert msg is not None
    assert "Quantidade de UC's" in msg


def test_quantidade_ucs_invalida_retorna_erro():
    deal = {"custom_fields": {FIELD_QUANTIDADE_UCS: "abc"}}
    msg = _validar_campo_contrato(
        deal, "Quantidade de UC's", FIELD_QUANTIDADE_UCS, "uc"
    )
    assert msg is not None
    assert "número" in msg.lower()


def test_quantidade_ucs_valida_ok():
    deal = {"custom_fields": {FIELD_QUANTIDADE_UCS: "12"}}
    assert (
        _validar_campo_contrato(
            deal, "Quantidade de UC's", FIELD_QUANTIDADE_UCS, "uc"
        )
        is None
    )


def test_cep_vazio_retorna_erro():
    deal = {"custom_fields": {FIELD_CEP: ""}}
    msg = _validar_campo_contrato(deal, "CEP", FIELD_CEP, "cep")
    assert msg is not None
    assert "CEP" in msg


def test_cep_valido_ok():
    deal = {"custom_fields": {FIELD_CEP: "80010-000"}}
    assert _validar_campo_contrato(deal, "CEP", FIELD_CEP, "cep") is None


def test_get_numero_contrato_sem_codigos_hub_usa_deal_id():
    deal = {"id": 746, "custom_fields": {}}
    assert get_numero_contrato(deal) == "CGRc746i746n1r0a26"


def test_get_numero_contrato_com_codigos_hub():
    deal = {
        "id": 746,
        "custom_fields": {
            FIELD_CODIGO_CLIENTE_INSTALACAO: "456/123",
        },
    }
    assert get_numero_contrato(deal) == "CGRc123i456n1r0a26"


@patch("core.pipedrive_validations.listar_arquivos_deal")
@patch("core.pipedrive_validations.erros_validacao_observacoes_hub", return_value=[])
@patch("core.pipedrive_validations.sincronizar_subcentros_de_pedidos")
@patch("core.pipedrive_validations.resolver_subcentro", return_value="1")
@patch("core.pipedrive_validations.settings_por_branch")
@patch("core.pipedrive_validations.resolver_branch_id", return_value="751")
@patch("core.pipedrive_validations.filial_tem_mapeamento", return_value=True)
def test_validar_deal_exige_anexo_proposta_comercial(
    _mock_filial,
    _mock_branch,
    mock_settings,
    _mock_sub,
    _mock_sync,
    _mock_hub,
    mock_listar,
):
    mock_settings.return_value = {
        "subcentro_custo_id": "5",
        "regional_map": {},
        "subcentro3_map": {},
    }
    mock_listar.return_value = [{"name": "contrato.pdf"}]
    deal_minimo = {"id": 999, "custom_fields": {}}

    with pytest.raises(DealValidationError) as exc:
        validar_deal_para_automacao(deal_minimo)

    assert any("Proposta Comercial" in msg for msg in exc.value.mensagens)


@patch("core.pipedrive_validations.listar_arquivos_deal")
@patch("core.pipedrive_validations.erros_validacao_observacoes_hub", return_value=[])
@patch("core.pipedrive_validations.sincronizar_subcentros_de_pedidos")
@patch("core.pipedrive_validations.resolver_subcentro", return_value="1")
@patch("core.pipedrive_validations.settings_por_branch")
@patch("core.pipedrive_validations.resolver_branch_id", return_value="751")
@patch("core.pipedrive_validations.filial_tem_mapeamento", return_value=True)
def test_validar_deal_com_proposta_comercial_nao_erro_so_por_anexo(
    _mock_filial,
    _mock_branch,
    mock_settings,
    _mock_sub,
    _mock_sync,
    _mock_hub,
    mock_listar,
):
    mock_settings.return_value = {
        "subcentro_custo_id": "5",
        "regional_map": {},
        "subcentro3_map": {},
    }
    mock_listar.return_value = [{"name": "Proposta Comercial assinada.pdf"}]
    deal_minimo = {"id": 999, "custom_fields": {}}

    with pytest.raises(DealValidationError) as exc:
        validar_deal_para_automacao(deal_minimo)

    assert not any("Proposta Comercial" in msg for msg in exc.value.mensagens)


@patch("core.pipedrive_validations.reabrir_deal")
@patch("core.pipedrive_validations.criar_nota_deal")
@patch("core.pipedrive_stages.reverter_deal_para_negociacao")
def test_reabrir_deal_falha_automacao_reverte_para_negociacao(
    mock_reverter, mock_nota, mock_reabrir
):
    reabrir_deal_falha_automacao("746", ["Plune: CNPJ duplicado"])
    mock_nota.assert_called_once()
    assert "Plune" in mock_nota.call_args[0][1]
    mock_reverter.assert_called_once_with("746")
    mock_reabrir.assert_called_once_with("746")


@patch("core.pipedrive_validations._deal_ja_tem_nota_validacao_ok", return_value=False)
@patch("core.pipedrive_validations.criar_nota_deal")
def test_notificar_validacao_aprovada_cria_anotacao(mock_nota, _mock_ja_tem):
    assert notificar_validacao_aprovada("746") is True
    mock_nota.assert_called_once_with("746", mock_nota.call_args[0][1])
    assert "validação" in mock_nota.call_args[0][1].lower()
    assert "concluída com sucesso" in mock_nota.call_args[0][1].lower()


@patch("core.pipedrive_validations._deal_ja_tem_nota_validacao_ok", return_value=True)
@patch("core.pipedrive_validations.criar_nota_deal")
def test_notificar_validacao_aprovada_nao_duplica(mock_nota, _mock_ja_tem):
    assert notificar_validacao_aprovada("746") is False
    mock_nota.assert_not_called()
