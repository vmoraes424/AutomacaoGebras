"""Testes unitários: normalização e formatação Pipedrive."""

from __future__ import annotations

from core.pipedrive_fields import (
    formatar_data_ptbr,
    formatar_decimal_plune,
    normalizar_cep,
    normalizar_documento,
    normalizar_nome,
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
