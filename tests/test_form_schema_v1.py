"""Validação de domínio do formulário v1 (Fase 4) — paridade com pipedrive_validations."""

from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from unittest.mock import patch

import pytest

from core.form_schema_v1 import form_payload_to_deal_dict, parse_form_payload_v1
from core.form_validation_v1 import validate_form_payload_v1
from core.pipedrive_fields import (
    FIELD_DATA_PAGAMENTO_IMPLANTACAO,
    FIELD_INSCRICAO_MUNICIPAL,
    FIELD_QUANTIDADE_UCS,
    FIELD_VALOR_IMPLANTACAO,
)
from core.pipedrive_validations import (
    _implantacao_exige_data_pagamento,
    _validar_campo_contrato,
)

FIXTURES = Path(__file__).resolve().parent / "fixtures" / "formulario_v1"


def _load(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def _deal_from_form(payload: dict, deal_id: int = 746) -> dict:
    parsed = parse_form_payload_v1(payload)
    return form_payload_to_deal_dict(deal_id, parsed)


def _plune_patches():
    return (
        patch("core.form_validation_v1.sincronizar_subcentros_de_pedidos"),
        patch("core.form_validation_v1.resolver_subcentro", return_value="1"),
        patch("core.pipedrive_validations.filial_tem_mapeamento", return_value=True),
        patch("core.pipedrive_validations.resolver_branch_id", return_value="751"),
    )


class TestSchemaV1Parse:
    def test_parse_payload_parcial_preenche_defaults(self):
        parsed = parse_form_payload_v1({"cliente": {"contratante": "X"}})
        assert parsed.cliente.contratante == "X"
        assert parsed.servicos.sole_web == 0
        assert parsed.schema_version == "v1"

    def test_servicos_coerce_string_para_int(self):
        parsed = parse_form_payload_v1({"servicos": {"sole_web": "4"}})
        assert parsed.servicos.sole_web == 4


class TestParidadePipedriveValidations:
    """Espelha casos de tests/test_pipedrive_validations.py com entrada form v1."""

    @pytest.mark.parametrize(
        "field_path,pipe_field,label,tipo,value,expect_error",
        [
            (
                "valores.valor_implantacao",
                FIELD_VALOR_IMPLANTACAO,
                "Valor de Implantação",
                "money_implantacao",
                "0",
                False,
            ),
            (
                "valores.valor_implantacao",
                FIELD_VALOR_IMPLANTACAO,
                "Valor de Implantação",
                "money_implantacao",
                "",
                True,
            ),
            (
                "cliente.inscricao_municipal",
                FIELD_INSCRICAO_MUNICIPAL,
                "Inscrição Municipal",
                "text",
                "",
                True,
            ),
            (
                "servicos.quantidade_ucs",
                FIELD_QUANTIDADE_UCS,
                "Quantidade de UC's",
                "uc",
                "12",
                False,
            ),
            (
                "cliente.cep",
                "6d3373f7ee86c7d2449824136baf3ee1938a8ef1",
                "CEP",
                "cep",
                "",
                True,
            ),
            (
                "cliente.cep",
                "6d3373f7ee86c7d2449824136baf3ee1938a8ef1",
                "CEP",
                "cep",
                "80010-000",
                False,
            ),
        ],
    )
    def test_campo_contrato_paridade(
        self,
        field_path,
        pipe_field,
        label,
        tipo,
        value,
        expect_error,
    ):
        base = _load("form_payload_v1_g1.json")
        section, _, key = field_path.partition(".")
        base[section][key] = value
        deal = _deal_from_form(base)
        msg = _validar_campo_contrato(deal, label, pipe_field, tipo)
        if expect_error:
            assert msg is not None
        else:
            assert msg is None

    def test_quantidade_ucs_vazia_retorna_erro_no_deal(self):
        deal = _deal_from_form(_load("form_payload_v1_g1.json"))
        deal["custom_fields"][FIELD_QUANTIDADE_UCS] = ""
        msg = _validar_campo_contrato(
            deal, "Quantidade de UC's", FIELD_QUANTIDADE_UCS, "uc"
        )
        assert msg is not None
        assert "Quantidade de UC's" in msg

    def test_quantidade_ucs_invalida_retorna_erro_no_deal(self):
        deal = _deal_from_form(_load("form_payload_v1_g1.json"))
        deal["custom_fields"][FIELD_QUANTIDADE_UCS] = "abc"
        msg = _validar_campo_contrato(
            deal, "Quantidade de UC's", FIELD_QUANTIDADE_UCS, "uc"
        )
        assert msg is not None

    def test_implantacao_zero_nao_exige_data_pagamento(self):
        payload = _load("form_payload_v1_g2_implantacao_zero.json")
        deal = _deal_from_form(payload)
        assert _implantacao_exige_data_pagamento(deal) is False
        payload["anexos"] = {"proposta_comercial_anexada": True}
        patches = _plune_patches()
        for p in patches:
            p.start()
        try:
            errors = validate_form_payload_v1(100, payload)
        finally:
            for p in patches:
                p.stop()
        assert "datas.data_pagamento_implantacao" not in errors

    def test_implantacao_maior_que_um_exige_data(self):
        payload = _load("form_payload_v1_g1.json")
        payload["datas"]["data_pagamento_implantacao"] = ""
        deal = _deal_from_form(payload)
        assert _implantacao_exige_data_pagamento(deal) is True
        msg = _validar_campo_contrato(
            deal,
            "Data de Pagamento da Implantação",
            FIELD_DATA_PAGAMENTO_IMPLANTACAO,
            "date",
        )
        assert msg is not None


class TestValidateFormPayloadV1:
    def test_incompleto_retorna_erros_estruturados(self):
        payload = _load("form_payload_v1_incompleto.json")
        errors = validate_form_payload_v1(746, payload)
        assert errors
        assert "cliente.endereco" in errors or "cliente.cep" in errors
        assert "signatarios.email_diretor_gebras" in errors
        assert "servicos.sole_web" in errors

    def test_g1_valido_transiciona_sem_erros(self):
        payload = _load("form_payload_v1_g1.json")
        patches = _plune_patches()
        for p in patches:
            p.start()
        try:
            errors = validate_form_payload_v1(746, payload)
        finally:
            for p in patches:
                p.stop()
        assert errors == {}

    def test_g2_implantacao_zero_sem_data_pagamento_ok(self):
        payload = _load("form_payload_v1_g2_implantacao_zero.json")
        payload["anexos"] = {"proposta_comercial_anexada": True}
        patches = _plune_patches()
        for p in patches:
            p.start()
        try:
            errors = validate_form_payload_v1(100, payload)
        finally:
            for p in patches:
                p.stop()
        assert "datas.data_pagamento_implantacao" not in errors

    def test_sem_proposta_comercial_retorna_erro(self):
        payload = deepcopy(_load("form_payload_v1_g2_implantacao_zero.json"))
        payload["anexos"] = {"proposta_comercial_anexada": False}
        patches = _plune_patches()
        for p in patches:
            p.start()
        try:
            errors = validate_form_payload_v1(100, payload)
        finally:
            for p in patches:
                p.stop()
        assert "anexos.proposta_comercial_anexada" in errors
