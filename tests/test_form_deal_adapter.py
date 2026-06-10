"""Adaptador formulario web → deal (Fase 5)."""

from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

import pytest

from core.form_deal_adapter import (
    DealFormSnapshot,
    merge_form_into_deal,
    preparar_deal_para_automacao,
)
from core.pipedrive_fields import FIELD_QTD_SOLE, get_val

FIXTURES = Path(__file__).resolve().parent / "fixtures" / "formulario_v1"


def _load(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


@pytest.fixture
def deal_pipe_g1() -> dict:
    return _load("deal_pipe_g1.json")


@pytest.fixture
def form_g1() -> dict:
    return _load("form_payload_v1_g1.json")


def test_merge_form_into_deal_preserva_metadados_pipe(deal_pipe_g1, form_g1):
    merged = merge_form_into_deal(deal_pipe_g1, form_g1)
    assert merged["id"] == deal_pipe_g1["id"]
    assert merged["title"] == deal_pipe_g1["title"]
    assert merged["owner_id"] == deal_pipe_g1["owner_id"]
    assert merged["stage_id"] == deal_pipe_g1["stage_id"]


def test_merge_g1_custom_fields_equivalentes_ao_pipe(deal_pipe_g1, form_g1):
    merged = merge_form_into_deal(deal_pipe_g1, form_g1)
    assert get_val(merged, FIELD_QTD_SOLE) == "4"
    assert merged["custom_fields"][FIELD_QTD_SOLE] == "4"


def test_precedencia_form_maior_que_pipe(deal_pipe_g1, form_g1):
    pipe = deepcopy(deal_pipe_g1)
    pipe["custom_fields"][FIELD_QTD_SOLE] = 1
    form = deepcopy(form_g1)
    form["servicos"]["sole_web"] = 4
    merged = merge_form_into_deal(pipe, form)
    assert get_val(merged, FIELD_QTD_SOLE) == "4"


def test_flag_desligada_retorna_pipe_inalterado(deal_pipe_g1, form_g1):
    def _loader(_deal_id: int):
        return DealFormSnapshot(999001, "validated", "v1", form_g1)

    result = preparar_deal_para_automacao(
        deal_pipe_g1,
        formulario_web_enabled=False,
        form_loader=_loader,
    )
    assert result.source == "pipe"
    assert result.skipped_reason is None
    assert result.deal == deal_pipe_g1


def test_flag_ligada_sem_formulario_pula(deal_pipe_g1):
    result = preparar_deal_para_automacao(
        deal_pipe_g1,
        formulario_web_enabled=True,
        form_loader=lambda _id: None,
    )
    assert result.skipped_reason == "formulario_web_ausente"


def test_flag_ligada_form_draft_pula(deal_pipe_g1, form_g1):
    result = preparar_deal_para_automacao(
        deal_pipe_g1,
        formulario_web_enabled=True,
        form_loader=lambda _id: DealFormSnapshot(999001, "draft", "v1", form_g1),
    )
    assert result.skipped_reason == "formulario_web_nao_validado"
    assert result.form_status == "draft"


def test_flag_ligada_form_validated_mescla(deal_pipe_g1, form_g1):
    result = preparar_deal_para_automacao(
        deal_pipe_g1,
        formulario_web_enabled=True,
        form_loader=lambda _id: DealFormSnapshot(999001, "validated", "v1", form_g1),
    )
    assert result.source == "form_merged"
    assert result.skipped_reason is None
    assert get_val(result.deal, FIELD_QTD_SOLE) == "4"
