"""Testes: validação da seção Contrato no Pipedrive."""

from __future__ import annotations

import pytest

from core.pipedrive_fields import (
    CAMPOS_CONTRATO_OBRIGATORIOS,
    CAMPOS_CONTRATO_OPCIONAIS,
    FIELD_CEP,
    FIELD_DATA_DE_IMPLANTACAO,
    FIELD_DATA_IMPLANTACAO,
    FIELD_DATA_PAGAMENTO_IMPLANTACAO,
    FIELD_NUMERO_CONTRATO_P1,
    FIELD_NUMERO_CONTRATO_P2,
    FIELD_OBSERVACOES_DETALHES,
    FIELD_VALOR_IMPLANTACAO,
)
from core.pipedrive_validations import (
    DealValidationError,
    _validar_campo_contrato,
)


@pytest.mark.parametrize(
    "field_code",
    [
        FIELD_NUMERO_CONTRATO_P1,
        FIELD_NUMERO_CONTRATO_P2,
        FIELD_DATA_DE_IMPLANTACAO,
        FIELD_DATA_PAGAMENTO_IMPLANTACAO,
        FIELD_DATA_IMPLANTACAO,
        FIELD_VALOR_IMPLANTACAO,
        FIELD_OBSERVACOES_DETALHES,
    ],
)
def test_campos_opcionais_nao_estao_na_lista_obrigatoria(field_code: str):
    obrigatorios = {row[1] for row in CAMPOS_CONTRATO_OBRIGATORIOS}
    assert field_code in CAMPOS_CONTRATO_OPCIONAIS
    assert field_code not in obrigatorios


def test_cep_vazio_retorna_erro():
    deal = {"custom_fields": {FIELD_CEP: ""}}
    msg = _validar_campo_contrato(deal, "CEP", FIELD_CEP, "cep")
    assert msg is not None
    assert "CEP" in msg


def test_cep_valido_ok():
    deal = {"custom_fields": {FIELD_CEP: "80010-000"}}
    assert _validar_campo_contrato(deal, "CEP", FIELD_CEP, "cep") is None
