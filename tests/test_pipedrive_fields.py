"""Testes unitários: normalização e formatação Pipedrive."""

from __future__ import annotations

import pytest

from core.pipedrive_fields import (
    FIELD_CODIGO_CLIENTE_INSTALACAO,
    FIELD_CONTATO_GESTOR,
    FIELD_EMAIL_CONSULTOR_GEBRAS,
    FIELD_NOTAS,
    formatar_data_ptbr,
    formatar_decimal_plune,
    get_contato_gestor_contrato,
    get_numero_contrato,
    get_cidade_estado,
    normalizar_cep,
    normalizar_documento,
    normalizar_nome,
    split_cidade_estado,
    sufixo_ano_contrato_gebras,
)


class TestNormalizarDocumento:
    def test_remove_mascara_cnpj(self):
        assert normalizar_documento("52.398.605/0001-86") == "52398605000186"

    def test_vazio(self):
        assert normalizar_documento("") == ""


class TestNormalizarCep:
    def test_somente_digitos_max_8(self):
        assert normalizar_cep("01310-100") == "01310100"

    def test_trunca_excesso(self):
        assert normalizar_cep("013101001999") == "01310100"


class TestNormalizarNome:
    def test_upper_sem_pontuacao_extra(self):
        assert normalizar_nome("  Açúcar & Cia.  ") == "AÇÚCAR CIA"


class TestFormatarDataPtbr:
    def test_iso(self):
        assert formatar_data_ptbr("2026-05-19T12:00:00Z") == "19/05/2026"

    def test_vazio_retorna_hoje(self):
        assert formatar_data_ptbr(None)  # não levanta


class TestFormatarDecimalPlune:
    def test_formato_brasileiro_com_virgula(self):
        assert formatar_decimal_plune("1234,56") == "1.234,56"

    def test_inteiro(self):
        assert formatar_decimal_plune("100") == "100,00"

    def test_invalido(self):
        assert formatar_decimal_plune("abc") == ""


class TestNumeroContrato:
    def test_sufixo_ano_dois_digitos(self):
        assert sufixo_ano_contrato_gebras(ano=2026) == "n1r0a26"
        assert sufixo_ano_contrato_gebras(ano=2027) == "n1r0a27"
        assert sufixo_ano_contrato_gebras(ano=2030) == "n1r0a30"

    def test_montagem_com_primeira_instalacao_e_cliente(self):
        deal = {
            "custom_fields": {
                FIELD_CODIGO_CLIENTE_INSTALACAO: "352/00665,01942",
            }
        }
        assert get_numero_contrato(deal) == "CGRc00665i352n1r0a26"
        deal["custom_fields"][FIELD_CODIGO_CLIENTE_INSTALACAO] = "352/665; 1942"
        assert get_numero_contrato(deal) == "CGRc665i352n1r0a26"

    def test_p1_p2_vazios_usam_deal_id(self):
        deal = {"id": 746, "custom_fields": {}}
        assert get_numero_contrato(deal) == "CGRc746i746n1r0a26"

    def test_apenas_p1_vazio_usa_deal_id(self):
        deal = {
            "id": 746,
            "custom_fields": {
                FIELD_CODIGO_CLIENTE_INSTALACAO: "352",
            },
        }
        assert get_numero_contrato(deal) == "CGRc746i352n1r0a26"

    def test_ignora_notas_usa_primeira_instalacao_do_campo(self):
        deal = {
            "custom_fields": {
                FIELD_NOTAS: "00665,01942",
                FIELD_CODIGO_CLIENTE_INSTALACAO: "352/1234,3456",
            }
        }
        assert get_numero_contrato(deal) == "CGRc1234i352n1r0a26"


class TestParseCodigoClienteInstalacao:
    def test_somente_cliente(self):
        from core.pipedrive_fields import parse_codigo_cliente_instalacao

        assert parse_codigo_cliente_instalacao("352") == (352, [])

    def test_cliente_com_uma_instalacao(self):
        from core.pipedrive_fields import parse_codigo_cliente_instalacao

        assert parse_codigo_cliente_instalacao("352/1234") == (352, [1234])

    def test_cliente_com_varias_instalacoes(self):
        from core.pipedrive_fields import parse_codigo_cliente_instalacao

        assert parse_codigo_cliente_instalacao("352/665,1942") == (352, [665, 1942])

    def test_formato_invalido(self):
        from core.pipedrive_fields import parse_codigo_cliente_instalacao

        with pytest.raises(ValueError, match="instalação"):
            parse_codigo_cliente_instalacao("352/abc")

    def test_format_codigo_cliente_instalacao(self):
        from core.pipedrive_fields import format_codigo_cliente_instalacao

        assert format_codigo_cliente_instalacao(352, []) == "352"
        assert format_codigo_cliente_instalacao(352, [665, 1942]) == "352/665,1942"


class TestSplitCidadeEstado:
    def test_formato_pipedrive_hifen(self):
        assert split_cidade_estado("Pelotas - RS, Brasil") == ("Pelotas", "RS")

    def test_hifen_sem_pais(self):
        assert split_cidade_estado("Curitiba - PR") == ("Curitiba", "PR")

    def test_formato_legado_barra(self):
        assert split_cidade_estado("Pelotas/RS") == ("Pelotas", "RS")

    def test_sem_separador(self):
        assert split_cidade_estado("Curitiba") == ("Curitiba", "")

    def test_get_cidade_estado_do_deal(self):
        deal = {
            "custom_fields": {
                "2bf3850e0a6dc7232f5f44197e79ffcc5642c1c5": "Pelotas - RS, Brasil"
            }
        }
        assert get_cidade_estado(deal) == ("Pelotas", "RS")


class TestContatoGestorContrato:
    def test_usa_email_consultor_gebras(self):
        deal = {
            "custom_fields": {
                FIELD_EMAIL_CONSULTOR_GEBRAS: "consultor@gebras.com",
                FIELD_CONTATO_GESTOR: "legado@gebras.com",
            }
        }
        assert get_contato_gestor_contrato(deal) == "consultor@gebras.com"

    def test_fallback_campo_legado(self):
        deal = {"custom_fields": {FIELD_CONTATO_GESTOR: "legado@gebras.com"}}
        assert get_contato_gestor_contrato(deal) == "legado@gebras.com"
