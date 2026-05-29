"""Testes unitários: normalização e formatação Pipedrive."""

from __future__ import annotations

from core.pipedrive_fields import (
    FIELD_NUMERO_CONTRATO_P1,
    FIELD_NUMERO_CONTRATO_P2,
    formatar_data_ptbr,
    formatar_decimal_plune,
    get_numero_contrato,
    normalizar_cep,
    normalizar_documento,
    normalizar_nome,
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

    def test_montagem_com_p1_p2(self):
        deal = {
            "custom_fields": {
                FIELD_NUMERO_CONTRATO_P1: "00665,01942",
                FIELD_NUMERO_CONTRATO_P2: "352",
            }
        }
        assert get_numero_contrato(deal) == "CGRc00665i352n1r0a26"
        deal["custom_fields"][FIELD_NUMERO_CONTRATO_P1] = "665; 1942"
        assert get_numero_contrato(deal) == "CGRc665i352n1r0a26"

    def test_p1_p2_vazios_usam_deal_id(self):
        deal = {"id": 746, "custom_fields": {}}
        assert get_numero_contrato(deal) == "CGRc746i746n1r0a26"

    def test_apenas_p1_vazio_usa_deal_id(self):
        deal = {
            "id": 746,
            "custom_fields": {
                FIELD_NUMERO_CONTRATO_P2: "352",
            },
        }
        assert get_numero_contrato(deal) == "CGRc746i352n1r0a26"
