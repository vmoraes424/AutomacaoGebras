"""Cenarios golden G1–G6 (secao 7.6) — adaptador form > Pipe."""

from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from unittest.mock import patch

import pytest

from core.form_deal_adapter import merge_form_into_deal, preparar_deal_para_automacao
from core.form_validation_v1 import validate_form_payload_v1
from core.hub_pedido import erros_validacao_observacoes_hub
from core.pipedrive_fields import (
    FIELD_CODIGO_CLIENTE_INSTALACAO,
    FIELD_QTD_SOLE,
    extrair_signatarios,
    get_numero_contrato,
    get_val,
    parse_codigo_cliente_instalacao,
)
from core.pipedrive_validations import _implantacao_exige_data_pagamento

FIXTURES = Path(__file__).resolve().parent / "fixtures" / "formulario_v1"


def _load(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def _plune_patches():
    return (
        patch("core.form_validation_v1.sincronizar_subcentros_de_pedidos"),
        patch("core.form_validation_v1.resolver_subcentro", return_value="1"),
        patch("core.pipedrive_validations.filial_tem_mapeamento", return_value=True),
        patch("core.pipedrive_validations.resolver_branch_id", return_value="751"),
    )


class TestGoldenG1:
    def test_adaptador_preserva_contexto_g1(self):
        deal_pipe = _load("deal_pipe_g1.json")
        form = _load("form_payload_v1_g1.json")
        expected = _load("expected_g1.json")
        merged = merge_form_into_deal(deal_pipe, form)

        assert get_val(merged, FIELD_QTD_SOLE) == expected["sole_web"]
        raw_codigo = get_val(merged, FIELD_CODIGO_CLIENTE_INSTALACAO)
        cliente, instalacoes = parse_codigo_cliente_instalacao(raw_codigo)
        assert cliente == expected["codigo_cliente"]
        assert instalacoes == expected["instalacoes"]
        assert get_numero_contrato(merged).startswith(expected["numero_contrato_pattern"])

        signatarios = extrair_signatarios(merged)
        assert len(signatarios) == expected["signatarios_count"]
        assert [s["papel"] for s in signatarios] == expected["signatarios_ordem"]
        assert erros_validacao_observacoes_hub(merged) == []


class TestGoldenG2:
    def test_implantacao_zero_nao_exige_data(self):
        form = _load("form_payload_v1_g2_implantacao_zero.json")
        form["anexos"] = {"proposta_comercial_anexada": True}
        deal_pipe = _load("deal_pipe_g1.json")
        merged = merge_form_into_deal(deal_pipe, form)
        assert _implantacao_exige_data_pagamento(merged) is False
        patches = _plune_patches()
        for p in patches:
            p.start()
        try:
            errors = validate_form_payload_v1(100, form)
        finally:
            for p in patches:
                p.stop()
        assert "datas.data_pagamento_implantacao" not in errors


class TestGoldenG4:
    def test_flag_off_pipe_inalterado(self):
        deal_pipe = _load("deal_pipe_g1.json")
        form = _load("form_payload_v1_g1.json")
        from core.form_deal_adapter import DealFormSnapshot

        result = preparar_deal_para_automacao(
            deal_pipe,
            formulario_web_enabled=False,
            form_loader=lambda _id: DealFormSnapshot(999001, "validated", "v1", form),
        )
        assert result.deal == deal_pipe
        assert result.source == "pipe"


class TestGoldenG5:
    def test_incompleto_nao_valida(self):
        payload = _load("form_payload_v1_incompleto.json")
        errors = validate_form_payload_v1(746, payload)
        assert errors
        assert "signatarios.email_diretor_gebras" in errors


class TestGoldenG6:
    def test_precedencia_sole_web(self):
        deal_pipe = _load("deal_pipe_g1.json")
        pipe = deepcopy(deal_pipe)
        pipe["custom_fields"][FIELD_QTD_SOLE] = 1
        form = _load("form_payload_v1_g1.json")

        off = preparar_deal_para_automacao(pipe, formulario_web_enabled=False)
        assert get_val(off.deal, FIELD_QTD_SOLE) == "1"

        from core.form_deal_adapter import DealFormSnapshot

        on = preparar_deal_para_automacao(
            pipe,
            formulario_web_enabled=True,
            form_loader=lambda _id: DealFormSnapshot(999001, "validated", "v1", form),
        )
        assert get_val(on.deal, FIELD_QTD_SOLE) == "4"
